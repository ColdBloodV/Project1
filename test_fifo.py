
"""Project 1: Constrained-Random Verification of a Synchronous FIFO."""

import random

import cocotb
import vsc

from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from models.fifo_model import FifoModel

from cocotb_coverage.coverage import (
    CoverPoint,
    CoverCross,
    coverage_db,
)

WIDTH = 8
DEPTH = 8
MASK = (1 << WIDTH) - 1

SEED = 4701
NUM_CYCLES = 5000


@vsc.randobj
class FifoTxn:
    """Constrained-random FIFO transaction."""

    def __init__(self):
        self.wr_en = vsc.rand_bit_t(1)
        self.rd_en = vsc.rand_bit_t(1)
        self.wr_data = vsc.rand_bit_t(WIDTH)

        # Current occupancy supplied by the reference model.
        self.count = vsc.uint32_t()

    @vsc.constraint
    def fifo_constraints(self):

        # Legal random transactions only.
        with vsc.if_then(self.count == 0):
            self.rd_en == 0

        with vsc.if_then(self.count == DEPTH):
            self.wr_en == 0

        # Near empty: favor writes.
        with vsc.if_then(self.count <= 1):
            vsc.dist(self.wr_en, [
                vsc.weight(0, 1),
                vsc.weight(1, 9),
            ])
            vsc.dist(self.rd_en, [
                vsc.weight(0, 9),
                vsc.weight(1, 1),
            ])

        # Middle occupancy: favor reads and writes.
        with vsc.else_if(self.count < 7):
            vsc.dist(self.wr_en, [
                vsc.weight(0, 1),
                vsc.weight(1, 9),
            ])
            vsc.dist(self.rd_en, [
                vsc.weight(0, 1),
                vsc.weight(1, 9),
            ])

        # Near full: favor reads.
        with vsc.else_then:
            vsc.dist(self.wr_en, [
                vsc.weight(0, 9),
                vsc.weight(1, 1),
            ])
            vsc.dist(self.rd_en, [
                vsc.weight(0, 1),
                vsc.weight(1, 9),
            ])


class FifoScoreboard:
    """Compare DUT outputs against the FIFO reference model."""

    def __init__(self, model):
        self.model = model
        self.cycles = 0

    def predict(self, wr, data, rd):
        self.model.step(wr, data, rd)

    def check(self, dut):
        self.cycles += 1

        actual_count = int(dut.count.value)
        actual_full = int(dut.full.value)
        actual_empty = int(dut.empty.value)

        assert actual_count == self.model.count, (
            f"Cycle {self.cycles}: count={actual_count}, "
            f"expected={self.model.count}; "
            f"queue={list(self.model.q)}"
        )

        assert actual_full == int(self.model.full), (
            f"Cycle {self.cycles}: full={actual_full}, "
            f"expected={int(self.model.full)}"
        )

        assert actual_empty == int(self.model.empty), (
            f"Cycle {self.cycles}: empty={actual_empty}, "
            f"expected={int(self.model.empty)}"
        )

        # First-word-fall-through data check.
        if not self.model.empty:
            actual_data = int(dut.rd_data.value)

            assert actual_data == self.model.head, (
                f"Cycle {self.cycles}: rd_data=0x{actual_data:02X}, "
                f"expected=0x{self.model.head:02X}; "
                f"queue={list(self.model.q)}"
            )


# ============================================
# FUNCTIONAL COVERAGE
# ============================================

@CoverPoint(
    "fifo.occupancy",
    xf=lambda count, wr, rd, data: count,
    bins=list(range(DEPTH + 1)),
)
@CoverPoint(
    "fifo.operation",
    xf=lambda count, wr, rd, data: (wr, rd),
    bins=[(0, 0), (1, 0), (0, 1), (1, 1)],
)
@CoverPoint(
    "fifo.data",
    xf=lambda count, wr, rd, data: data,
    bins=[0x00, 0x55, 0xAA, 0xFF],
)
@CoverCross(
    "fifo.occupancy_operation",
    items=["fifo.occupancy", "fifo.operation"],
    ign_bins=[
        (0, (0, 1)),
        (0, (1, 1)),
        (DEPTH, (1, 0)),
        (DEPTH, (1, 1)),
    ],
)
def sample_fifo_coverage(count, wr, rd, data):
    pass


# ============================================
# DIRECTED-TEST HELPER
# ============================================

async def drive_and_check(dut, scoreboard, wr, rd, data=0):
    """Apply one operation and verify the resulting FIFO state."""

    # Drive inputs before the next rising clock edge.
    await FallingEdge(dut.clk)

    dut.wr_en.value = wr
    dut.rd_en.value = rd
    dut.wr_data.value = data

    scoreboard.predict(wr, data, rd)

    await RisingEdge(dut.clk)
    await Timer(1, units="ns")

    scoreboard.check(dut)


# ============================================
# MAIN TEST
# ============================================

@cocotb.test()
async def test_crv(dut):

    # Start the clock.
    cocotb.start_soon(
        Clock(dut.clk, 10, units="ns").start()
    )

    model = FifoModel(WIDTH, DEPTH)
    scoreboard = FifoScoreboard(model)

    # ----------------------------------------
    # RESET
    # ----------------------------------------

    dut.wr_en.value = 0
    dut.rd_en.value = 0
    dut.wr_data.value = 0
    dut.rst_n.value = 0

    for _ in range(3):
        await RisingEdge(dut.clk)

    await Timer(1, units="ns")
    model.reset()
    scoreboard.check(dut)

    dut.rst_n.value = 1
    await FallingEdge(dut.clk)

    # ----------------------------------------
    # CONSTRAINED-RANDOM TESTING
    # ----------------------------------------

    occupancies_seen = {0}

    saw_full = False
    saw_empty = True
    saw_simultaneous = False

    random.seed(SEED)
    txn = FifoTxn()

    dut.wr_en.value = 0
    dut.rd_en.value = 0
    dut.wr_data.value = 0

    for cycle in range(NUM_CYCLES):

        pre_count = model.count
        txn.count = pre_count
        txn.randomize()

        wr = int(txn.wr_en)
        rd = int(txn.rd_en)
        data = int(txn.wr_data) & MASK

        # Verify the generator respects legal-operation constraints.
        assert not (pre_count == 0 and rd), (
            f"Cycle {cycle}: illegal read while empty"
        )

        assert not (pre_count == DEPTH and wr), (
            f"Cycle {cycle}: illegal write while full"
        )

        # Sample coverage before updating the model.
        sample_fifo_coverage(pre_count, wr, rd, data)

        if wr and rd and 0 < pre_count < DEPTH:
            saw_simultaneous = True

        # Drive inputs.
        dut.wr_en.value = wr
        dut.rd_en.value = rd
        dut.wr_data.value = data

        # Update reference model.
        scoreboard.predict(wr, data, rd)

        # Check after the active clock edge.
        await RisingEdge(dut.clk)
        await Timer(1, units="ns")

        scoreboard.check(dut)

        occupancies_seen.add(model.count)

        if model.count == DEPTH:
            saw_full = True

        if model.count == 0:
            saw_empty = True

        await FallingEdge(dut.clk)

    # ----------------------------------------
    # DIRECTED BOUNDARY TESTS
    # ----------------------------------------

    # The random loop ends at a falling edge.
    # Disable previous controls so the next cycle is idle.
    dut.wr_en.value = 0
    dut.rd_en.value = 0
    dut.wr_data.value = 0

    # Test 1: Drain FIFO until empty.
    while model.count > 0:
        await drive_and_check(
            dut, scoreboard,
            wr=0, rd=1
        )

    # Attempt to read while empty.
    # Correct FIFO must ignore this request.
    await drive_and_check(
        dut, scoreboard,
        wr=0, rd=1
    )

    assert model.count == 0
    dut._log.info("Empty-read protection test passed")

    # Test 2: Fill FIFO completely with known data.
    for i in range(DEPTH):
        await drive_and_check(
            dut, scoreboard,
            wr=1, rd=0,
            data=i + 1
        )

    assert model.count == DEPTH

    # Attempt to write while full.
    # Correct FIFO must ignore this request.
    await drive_and_check(
        dut, scoreboard,
        wr=1, rd=0,
        data=0xAA
    )

    assert model.count == DEPTH
    dut._log.info("Full-write protection test passed")

    # Drain FIFO to check ordering after the full-write attempt.
    while model.count > 0:
        await drive_and_check(
            dut, scoreboard,
            wr=0, rd=1
        )

    # Disable controls after the final directed operation.
    dut.wr_en.value = 0
    dut.rd_en.value = 0

    dut._log.info("Directed boundary tests completed")

    # ----------------------------------------
    # COVERAGE REQUIREMENTS
    # ----------------------------------------

    missing = set(range(DEPTH + 1)) - occupancies_seen

    assert not missing, (
        f"Missing FIFO occupancy states: {sorted(missing)}"
    )

    assert saw_full, "FIFO never reached full"
    assert saw_empty, "FIFO never reached empty"
    assert saw_simultaneous, (
        "No simultaneous read/write at intermediate occupancy"
    )

    # ----------------------------------------
    # FINAL SUMMARY
    # ----------------------------------------

    dut._log.info("====================================")
    dut._log.info("FIFO CRV COVERAGE SUMMARY")
    dut._log.info(f"Seed: {SEED}")
    dut._log.info(f"Random cycles: {NUM_CYCLES}")
    dut._log.info(f"Scoreboard checks: {scoreboard.cycles}")
    dut._log.info(
        f"Occupancies reached: {sorted(occupancies_seen)}"
    )
    dut._log.info(f"Reached full: {saw_full}")
    dut._log.info(f"Reached empty: {saw_empty}")
    dut._log.info(f"Simultaneous read/write: {saw_simultaneous}")
    dut._log.info("Illegal random transactions: 0")
    dut._log.info("Directed empty-read test: completed")
    dut._log.info("Directed full-write test: completed")

    dut._log.info("====================================")
    dut._log.info("FUNCTIONAL COVERAGE")
    dut._log.info(
        f"Total coverage: {coverage_db['fifo'].cover_percentage:.2f}%"
    )

    coverage_db.report_coverage(
        dut._log.info,
        bins=True,
    )
