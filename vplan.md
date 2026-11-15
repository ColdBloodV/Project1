# Project 1 — FIFO Verification Plan

## 1. Verification Objective

The objective of this project is to verify the functionality of a parameterized synchronous First-Word Fall-Through (FWFT) FIFO using cocotb, pyvsc, and cocotb-coverage.

The verification environment uses constrained-random stimulus, directed boundary tests, and a Python reference-queue scoreboard to compare the Design Under Test (DUT) against the FIFO specification.

The default configuration is:

- **WIDTH:** 8 bits
- **DEPTH:** 8 entries
- **Random test cycles:** 5,000
- **Configured seed:** 4701
- **Simulator:** Verilator

The verification strategy combines legal constrained-random operations with directed tests for boundary conditions that the random generator intentionally excludes.

## 2. Features and Requirements

| ID | Requirement | Expected Behavior | Priority |
|---|---|---|---|
| FIFO-01 | Synchronous reset | Reset clears occupancy on the rising clock edge | High |
| FIFO-02 | Write operation | Writes are accepted when the FIFO is not full | High |
| FIFO-03 | Read operation | Reads are accepted when the FIFO is not empty | High |
| FIFO-04 | Simultaneous read/write | Both operations are accepted at intermediate occupancy; count remains unchanged | High |
| FIFO-05 | Status flags | Full and empty flags accurately reflect occupancy | High |
| FIFO-06 | Data ordering | Data is returned in first-in, first-out order | High |
| FIFO-07 | Overflow protection | Writes attempted while full are ignored | High |
| FIFO-08 | Underflow protection | Reads attempted while empty are ignored | High |
| FIFO-09 | FWFT output | Read data reflects the current head whenever the FIFO is nonempty | High |
| FIFO-10 | Pointer wrap-around | Data ordering remains correct after repeated writes and reads | Medium |

FIFO-01 through FIFO-06 represent the primary behavioral requirements. FIFO-07 through FIFO-10 expand verification to important boundary conditions and data-integrity behavior.

## 3. Test Matrix

| Test | Requirements | Verification Method | Status |
|---|---|---|---|
| Initial reset | FIFO-01, FIFO-05 | Assert reset and check count, full, and empty | Implemented |
| Write operations | FIFO-02, FIFO-05 | Random and directed writes checked against reference model | Implemented |
| Read operations | FIFO-03, FIFO-06 | Random and directed reads checked against reference model | Implemented |
| Fill to full | FIFO-02, FIFO-05 | Write until occupancy reaches DEPTH | Implemented |
| Drain to empty | FIFO-03, FIFO-05 | Read until occupancy reaches zero | Implemented |
| Overflow protection | FIFO-07 | Attempt a write while full and verify no state change | Implemented |
| Underflow protection | FIFO-08 | Attempt a read while empty and verify no state change | Implemented |
| Simultaneous read/write | FIFO-04 | Exercise both enables at intermediate occupancy | Implemented |
| FWFT behavior | FIFO-09 | Compare output data with the reference queue head | Implemented |
| Pointer wrap-around | FIFO-06, FIFO-10 | Exercise repeated FIFO operations and check ordering | Covered through regression; dedicated test recommended |
| Reset during active traffic | FIFO-01, FIFO-05 | Assert reset after data has entered the FIFO | Planned |

The constrained-random regression exercises normal FIFO behavior across all occupancy levels. Directed tests supplement the regression by checking operations that are intentionally excluded by the legal transaction constraints.

## 4. Verification Environment

The verification environment is implemented in `code/tb/fifo_crv/test_fifo.py` and uses the reference model in `code/lib/models/fifo_model.py`.

### 4.1 Transaction Generator

The `FifoTxn` class uses pyvsc to randomize:

- Write enable (`wr_en`)
- Read enable (`rd_en`)
- Write data (`wr_data`)

The current FIFO occupancy is supplied to the generator as a non-random field. Constraints use this occupancy to prevent read requests while empty and write requests while full during random testing.

### 4.2 Driver

The testbench drives control signals and write data before the active clock edge.

The directed-test helper, `drive_and_check()`, applies a requested operation and advances the simulation to the next rising edge.

### 4.3 Monitor and Sampling

The testbench samples DUT outputs after the rising clock edge, with a short delay to allow registered state updates to settle.

The current implementation performs this sampling directly through the scoreboard rather than through a separate monitor class.

### 4.4 Reference Model and Scoreboard

The `FifoModel` maintains a Python queue representing expected FIFO contents.

The scoreboard updates the reference model according to the requested operation and the pre-edge FIFO state.

After each operation, the scoreboard compares:

- FIFO occupancy (`count`)
- Full flag (`full`)
- Empty flag (`empty`)
- FWFT output data (`rd_data`) whenever the FIFO is nonempty

Any mismatch causes an assertion failure, allowing the testbench to identify incorrect FIFO behavior.

## 5. Functional Coverage Model

Functional coverage is implemented using `cocotb-coverage`.

### 5.1 Implemented Coverpoints

| Coverpoint | Bins | Total |
|---|---|---|
| FIFO occupancy | Individual values 0 through 8 | 9 |
| Requested operation | Idle, write only, read only, simultaneous read/write | 4 |
| Write-data value | `0x00`, `0x55`, `0xAA`, `0xFF` | 4 |
| Occupancy × requested operation | Legal occupancy-operation combinations | 32 |

**Total defined coverage bins: 49**

The occupancy coverpoint tracks every possible FIFO occupancy value from empty to full.

The operation coverpoint records all four combinations of the write and read enables.

The data coverpoint records selected values of the randomized write-data field. These values are sampled regardless of whether a write is accepted.

### 5.2 Cross Coverage

The implemented cross coverage combines FIFO occupancy with the requested operation.

Four combinations are excluded from the legal constrained-random coverage target:

- Read only while empty
- Simultaneous read/write while empty
- Write only while full
- Simultaneous read/write while full

These exclusions apply only to the legal random coverage model. Empty-read and full-write rejection behavior is tested separately using directed transactions.

### 5.3 Coverage Results

The completed constrained-random regression reported:

| Coverage Metric | Result |
|---|---|
| Occupancy | 9/9 bins |
| Requested operations | 4/4 bins |
| Selected data values | 4/4 bins |
| Occupancy × operation | 32/32 bins |
| **Total functional coverage** | **49/49 bins — 100%** |

All defined legal functional coverage bins were exercised during the regression.

This result demonstrates closure of the implemented coverage model, but does not imply that every possible FIFO behavior has been tested.

### 5.4 Future Coverage Improvements

Additional coverage points may be introduced for:

- Accepted operations versus requested operations
- Reset during active traffic
- Occupancy transitions
- Data patterns associated specifically with accepted writes
- Boundary operations exercised by directed tests

These are potential improvements and are not included in the reported 49-bin coverage total.

## 6. Constrained-Random Strategy

The testbench executes 5,000 constrained-random cycles using pyvsc.

The random generator adjusts operation probabilities according to the current FIFO occupancy.

### 6.1 Near-Empty Occupancy

When occupancy is zero or one, writes are favored to encourage the FIFO to fill.

The generator also prevents reads while empty.

### 6.2 Intermediate Occupancy

At intermediate occupancy levels, both write and read enables are favored.

This encourages simultaneous read/write transactions and exercises data ordering while occupancy remains unchanged.

### 6.3 Near-Full Occupancy

Near full, reads are favored to reduce occupancy and encourage repeated movement between FIFO states.

The generator prevents writes when the FIFO is full.

### 6.4 Reproducibility

The testbench records a configured seed value of 4701 and initializes Python's random module with that seed.

The exact pyvsc solver-seeding behavior remains to be verified before claiming fully deterministic transaction replay.

## 7. Directed Boundary Verification

Two directed tests were added after the constrained-random regression to verify behavior excluded by the legal random constraints.

### 7.1 Empty-Read Protection

The FIFO is drained until its occupancy reaches zero.

A read request is then asserted while the FIFO is empty.

The expected behavior is:

- The read request is ignored.
- Occupancy remains zero.
- The empty flag remains asserted.
- The reference model and DUT remain consistent.

This test detects faults that allow reads to proceed while the FIFO is empty.

### 7.2 Full-Write Protection

The FIFO is filled to its maximum occupancy using known data values.

An additional write request is then asserted while the FIFO is full.

The expected behavior is:

- The write request is ignored.
- Occupancy remains at DEPTH.
- The full flag remains asserted.
- Previously stored data remains in the correct order.

The FIFO is subsequently drained and checked against the reference queue.

This test detects faults that allow writes to proceed while the FIFO is full.

## 8. Coverage Closure

Coverage closure was evaluated using the results of the constrained-random regression and the mutation-testing harness.

The 5,000-cycle regression achieved 100% of the implemented functional coverage bins.

However, the initial mutation test detected only six of the eight released mutants.

The two surviving mutants were:

- `ignore_full`
- `ignore_empty`

These survived because the constrained-random generator intentionally prohibited write requests while full and read requests while empty.

To address this limitation, directed full-write and empty-read tests were added without removing the legal transaction constraints.

After these additions, the clean RTL continued to pass and both previously surviving mutants were detected.

This demonstrates that functional coverage closure alone does not guarantee detection of all targeted faults. Directed corner-case testing provides an important complement to constrained-random verification.

## 9. Mutation Testing

Mutation testing was performed using the released FIFO mutant pool and the course-provided mutation harness.

The mutation score is calculated as:

\[
\text{Mutation Score} =
\frac{\text{Detected Mutants}}{\text{Total Mutants}}
\times 100\%
\]

### 9.1 Final Mutation Results

| Mutant | Fault Description | Result |
|---|---|---|
| `full_offbyone` | Full flag asserts one entry early | Found |
| `empty_offbyone` | Empty flag asserts at the wrong occupancy | Found |
| `ignore_full` | Writes incorrectly accepted while full | Found |
| `ignore_empty` | Reads incorrectly accepted while empty | Found |
| `count_wr_dec` | Write-only operation decrements count | Found |
| `rd_data_wrptr` | Output reads from the write pointer | Found |
| `mem_corrupt` | Stored data is modified during writes | Found |
| `wrptr_wrap_early` | Write pointer wraps one entry early | Found |

**Final mutation score: 8/8 = 100%**

The project threshold is 90%, which was exceeded.

No mutants survived the final regression.

### 9.2 Mutation Pool Compatibility

A width mismatch in the full-flag comparison initially prevented the mutation harness from compiling the clean RTL under Verilator.

The comparison was updated to use an explicit width cast, and the corresponding mutation definition was adjusted to match the revised RTL expression.

These changes should be documented with the project deliverables so the final mutation results can be reproduced.

## 10. Risks and Priorities

| Risk | Impact | Mitigation |
|---|---|---|
| Incorrect scoreboard timing | False failures or missed bugs | Predict from pre-edge state and check after rising edge |
| Missing boundary conditions | Undetected overflow/underflow faults | Directed full-write and empty-read tests |
| Insufficient random diversity | Functional coverage holes | Occupancy-dependent random distributions |
| Pointer wrap-around bugs | Incorrect FIFO ordering | Repeated operations and reference-queue comparison |
| Reset during active traffic | Incorrect reset recovery | Add a dedicated active-reset test |
| Nonreproducible random sequences | Difficult debugging | Verify pyvsc seeding and retain regression commands |
| Mutation compilation errors | Invalid mutation results | Validate the clean RTL baseline before mutation scoring |

## 11. Completion Criteria

The verification effort will be considered complete when:

- [x] Initial reset behavior is verified.
- [x] Normal write and read operations are verified.
- [x] Simultaneous read/write operations are exercised.
- [x] Full and empty boundary protection is verified.
- [x] The constrained-random regression passes.
- [x] All implemented functional coverage bins are covered.
- [x] The released mutation pool is evaluated.
- [x] The required mutation threshold is achieved.
- [ ] Reset during active traffic is explicitly tested.
- [ ] pyvsc seed reproducibility is confirmed.
- [ ] Verification results and RTL/mutation-pool adjustments are documented in the final report.
- [ ] Final project documentation and team deliverables are completed.

## 12. Summary

The FIFO verification environment combines a Python reference model, a scoreboard, constrained-random transactions, functional coverage, and directed boundary testing.

The completed regression achieved 100% coverage of the 49 defined functional coverage bins and detected all eight released FIFO mutants.

The mutation-testing results demonstrate the value of combining legal constrained-random verification with directed corner-case testing.

Remaining work focuses on documenting reproducibility, confirming active-reset behavior, and completing the final project deliverables.