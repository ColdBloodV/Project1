# FINDINGS — FIFO Verification: Francesca Alfaro

## Score

| Pool | Found | Total | Score |
|---|---:|---:|---:|
| Released (practice) — initial CRV | 6 | 8 | 75% |
| Released (practice) — final CRV | 8 | 8 | 100% |
| Hidden (reported at grading) | — | — | Pending |

The final constrained-random verification environment detected all eight mutants in the released practice pool, exceeding the project's 90% mutation-score threshold.

**Command run:**

```bash
cd ~/homework/craft-vv-student
source /opt/course/cocotb-env/bin/activate

# Run the clean FIFO constrained-random testbench
make -C code/tb/fifo_crv SIM=verilator

# Run mutation testing against the released pool
python code/lib/craft_mutate/mutate.py \
  --tb code/tb/fifo_crv \
  --pool code/tb/fifo_crv/mutants_released.yaml \
  --sim verilator \
  --timeout 120 \
  --json fifo_crv_mutation_results.json

# View saved mutation results
cat fifo_crv_mutation_results.json
```

**Final mutation result:**

```text
[baseline] running clean fifo.sv through fifo_crv ...
  clean RTL: 1 tests passed.

  [found  ] full_offbyone
  [found  ] empty_offbyone
  [found  ] ignore_full
  [found  ] ignore_empty
  [found  ] count_wr_dec
  [found  ] rd_data_wrptr
  [found  ] mem_corrupt
  [found  ] wrptr_wrap_early

==== found/total = 8/8 = 100.0% (threshold 90%) ====
```

## Survivors

**Final regression: No released mutants survived.**

However, the initial constrained-random regression detected only six of the eight mutants. Two mutants survived because the random transaction constraints intentionally prevented illegal FIFO operations.

| Mutant | What it changes | Reachable by initial stimulus? | Observable by scoreboard? | Why it initially survived |
|---|---|---|---|---|
| `ignore_full` | Allows writes even when the FIFO is full | No | Yes | The random generator prevented writes at full occupancy |
| `ignore_empty` | Allows reads even when the FIFO is empty | No | Yes | The random generator prevented reads at zero occupancy |

### Survivor Analysis

**1. `ignore_full` — Overflow protection**

The original FIFO prevents writes when the full flag is asserted:

```systemverilog
assign do_wr = wr_en & ~full;
```

The mutant removes this protection:

```systemverilog
assign do_wr = wr_en;
```

The initial constrained-random generator contained a constraint that prevented write requests whenever occupancy reached `DEPTH`.

Consequently, the incorrect behavior introduced by this mutant was never activated during the initial regression.

To address this, a directed test was added that fills the FIFO to capacity and then attempts an additional write. The scoreboard verifies that occupancy remains unchanged and the stored data remains in the expected order.

The updated testbench successfully detected this mutant.

**2. `ignore_empty` — Underflow protection**

The original FIFO prevents reads when the empty flag is asserted:

```systemverilog
assign do_rd = rd_en & ~empty;
```

The mutant removes this protection:

```systemverilog
assign do_rd = rd_en;
```

The initial constrained-random generator prevented read requests when FIFO occupancy was zero.

Therefore, the incorrect empty-read behavior was never exercised.

A directed test was added that drains the FIFO completely and then attempts an additional read. The scoreboard verifies that occupancy remains zero and the empty flag remains asserted.

The updated testbench successfully detected this mutant.

### Final Survivor Status

After adding both directed boundary tests, all eight released mutants were detected.

The final mutation score improved from 75% to 100%.

## What I Changed, and What It Bought

| Change | Score Before | Score After | Faults Detected |
|---|---:|---:|---|
| Initial constrained-random testbench with reference-model scoreboard | Not measured | 6/8 (75%) | `full_offbyone`, `empty_offbyone`, `count_wr_dec`, `rd_data_wrptr`, `mem_corrupt`, `wrptr_wrap_early` |
| Added directed read-while-empty test | 6/8 (75%) | Not measured separately | `ignore_empty` |
| Added directed write-while-full test and data-order verification | 6/8 (75%) | Not measured separately | `ignore_full` |
| Reran complete regression with both directed tests | 6/8 (75%) | 8/8 (100%) | Both previously surviving mutants |

The most significant improvement was combining legal constrained-random verification with directed boundary testing.

The initial testbench used pyvsc constraints to prevent read requests while empty and write requests while full. Although these constraints generated valid normal-operation traffic, they prevented the testbench from activating two important boundary faults.

Adding directed tests allowed the verification environment to exercise these corner cases without changing the legal random transaction constraints.

### Functional Coverage Results

The constrained-random regression executed 5,000 cycles and collected functional coverage using `cocotb-coverage`.

| Coverage Metric | Covered Bins | Total Bins | Coverage |
|---|---:|---:|---:|
| FIFO occupancy | 9 | 9 | 100% |
| Requested operation | 4 | 4 | 100% |
| Selected write-data values | 4 | 4 | 100% |
| Occupancy × requested operation | 32 | 32 | 100% |
| **Total** | **49** | **49** | **100%** |

The testbench exercised all FIFO occupancy states from zero to eight, all four requested-operation combinations, and all defined legal occupancy-operation cross combinations.

The data coverage point sampled the randomized write-data field, including cycles without an accepted write.

Although the initial regression achieved 100% functional coverage, two mutants survived. This demonstrated that the original coverage model did not include the rejected boundary operations necessary to detect overflow and underflow protection faults.

The directed tests closed this verification gap.

### Additional Implementation Changes

During mutation testing, Verilator initially reported a width-expansion warning in the FIFO full-flag comparison, preventing the mutation harness from compiling the clean RTL.

The comparison was changed to explicitly match the occupancy counter width:

```systemverilog
assign full = (cnt == (ADDRW+1)'(DEPTH));
```

The corresponding `full_offbyone` entry in the released mutation YAML was adjusted to match the updated expression while preserving the intended fault.

After these changes, the clean RTL baseline passed and mutation testing completed successfully.

## Residual Risk

A 100% mutation score for the released pool does not guarantee complete verification of the FIFO. The eight released mutants represent a limited selection of possible implementation faults.

1. **Reachability:** The testbench exercises the default eight-entry, eight-bit FIFO configuration. It does not exhaustively test every possible input sequence or parameter configuration.

2. **Observability:** The scoreboard checks occupancy, full and empty flags, and read data whenever the FIFO is nonempty. Faults that do not affect these observed outputs may remain undetected.

3. **Reset behavior:** The testbench verifies initialization reset, but does not currently include a dedicated reset-during-active-traffic test. Additional reset testing would improve confidence in recovery behavior.

4. **Randomized coverage:** The constrained-random regression executes 5,000 cycles and achieves all defined functional coverage bins. However, this does not represent exhaustive verification of every possible control and data combination. Python's random module is seeded with 4701, but deterministic pyvsc solver replay has not yet been independently confirmed.

5. **Parameterization:** Verification was performed using WIDTH = 8 and DEPTH = 8. Other parameter configurations may reveal issues that are not observable with the default configuration.

6. **Coverage model limitations:** The current coverage model focuses on occupancy, requested operations, selected data values, and occupancy-operation crosses. Additional coverpoints for reset, accepted operations, and occupancy transitions would provide more complete coverage.

## If I Had Another Day

I would prioritize adding a directed reset-during-traffic test to verify that the FIFO correctly clears its state while data is present.

I would also run additional constrained-random regressions using independently controlled pyvsc seeds, test alternative FIFO depths and widths, and extend functional coverage to include accepted operations and occupancy transitions.

These improvements would increase confidence in the FIFO implementation and help detect faults not represented by the released mutation pool.

## Conclusion

The Project 1 FIFO verification environment successfully combined constrained-random stimulus, a Python reference-queue scoreboard, functional coverage, and directed boundary testing.

The initial constrained-random regression achieved 100% of the defined functional coverage bins but detected only six of the eight released mutants.

Analysis of the surviving mutants revealed that the random constraints prevented illegal read and write requests at the FIFO boundaries.

After adding directed overflow and underflow tests, the mutation score increased from 75% to 100%, with all eight released mutants detected.

These results demonstrate that constrained-random verification and functional coverage are most effective when supplemented by targeted tests for important corner cases.