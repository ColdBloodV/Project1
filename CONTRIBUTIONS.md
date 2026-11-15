# Contributions — FIFO Constrained-Random Verification · Project 1

**Members:** Francesca Alfaro (NID: [enter NID])

**Repo:** [enter repository URL]

**Track:** FIFO Constrained-Random Verification

**Last updated:** November 14, 2026

**Project:** EEE 4701 — Project 1

---

## M1 — Verification Planning and Environment

| Member | What they owned | Evidence (commits / files / PRs) | Approx. share |
|---|---|---|---|
| Francesca Alfaro | Verification planning, FIFO specification analysis, constrained-random testbench development, and reference-model integration | `vplan.md`, `code/tb/fifo_crv/test_fifo.py`, `code/lib/models/fifo_model.py` (integration) | [confirm share] |

**Shared or paired work:**

[Record any collaboration with teammates. If this was individual work, enter "None — individual project."]

**What slipped, and who picked it up:**

No specific missed milestone has been documented. [Update if applicable.]

## M2 — Constrained-Random Testing and Functional Coverage

| Member | What they owned | Evidence (commits / files / PRs) | Approx. share |
|---|---|---|---|
| Francesca Alfaro | Configured pyvsc transaction constraints, executed the 5,000-cycle constrained-random regression, integrated cocotb-coverage, and reviewed functional coverage results | `code/tb/fifo_crv/test_fifo.py`, simulation logs | [confirm share] |

**Shared or paired work:**

[Record any collaboration or code reviews.]

**What slipped, and who picked it up:**

The legal constrained-random coverage model did not exercise rejected reads while empty or writes while full. These gaps were identified through subsequent mutation testing.

**Changes to the division of labor since M1, and why:**

[Complete if working with teammates; otherwise enter "Not applicable."]

## M3 — Mutation Testing and Coverage Closure

| Member | What they owned | Evidence (commits / files / PRs) | Approx. share |
|---|---|---|---|
| Francesca Alfaro | Executed the mutation harness, analyzed surviving mutants, added directed empty-read and full-write tests, and reran the mutation regression | `code/tb/fifo_crv/test_fifo.py`, `code/tb/fifo_crv/mutants_released.yaml`, `fifo_crv_mutation_results.json`, `FINDINGS.md` | [confirm share] |

**Shared or paired work:**

[Record any collaboration or reviews.]

**What slipped, and who picked it up:**

The initial mutation regression detected 6/8 mutants (75%). The `ignore_full` and `ignore_empty` mutants survived because legal transaction constraints prevented the relevant boundary requests.

Directed boundary tests were subsequently added, improving the mutation score to 8/8 (100%).

A Verilator width warning also prevented the initial mutation baseline from compiling. The full-flag comparison was width-corrected, and the corresponding mutant definition was updated to match.

**Changes to the division of labor since M2, and why:**

[Complete if applicable.]

## M4 — Documentation and Final Submission

| Member | What they owned | Evidence (commits / files / PRs) | Approx. share |
|---|---|---|---|
| Francesca Alfaro | Revised verification plan, documented mutation results and coverage closure, and prepared project contribution records | `vplan.md`, `FINDINGS.md`, `CONTRIBUTIONS.md` | [confirm share] |

**Shared or paired work:**

[Record any collaboration or review.]

**What slipped, and who picked it up:**

Final report, reproducibility checks, and submission status remain to be confirmed.

---

## Whole-Project Summary

| Member | Principal contributions | Overall share |
|---|---|---:|
| Francesca Alfaro | Verification planning, constrained-random testbench implementation, reference-model scoreboard integration, functional coverage, mutation testing, directed boundary testing, debugging, and documentation | [confirm share] |

**The three technical results I can explain and defend:**

1. **Constrained-random FIFO verification:** Implemented a cocotb testbench using pyvsc to generate 5,000 cycles of legal randomized FIFO transactions, with occupancy-dependent constraints and a reference-model scoreboard.

2. **Functional coverage:** Collected coverage for FIFO occupancy, requested operations, selected data values, and occupancy-operation combinations. The regression achieved 49/49 defined coverage bins (100%).

3. **Mutation testing and coverage closure:** Analyzed the two mutants surviving the initial 6/8 regression, added directed boundary tests, and achieved a final mutation score of 8/8 (100%).

## Non-Code Contributions

| Member | Contribution | Where it shows |
|---|---|---|
| Francesca Alfaro | Verification planning and requirements mapping | `vplan.md` |
| Francesca Alfaro | Functional coverage analysis | Simulation output and final report |
| Francesca Alfaro | Mutation survivor analysis and coverage closure documentation | `FINDINGS.md` |
| Francesca Alfaro | Debugging Verilator compilation and mutation harness compatibility | `code/dut/fifo.sv`, `code/tb/fifo_crv/mutants_released.yaml` |
| Francesca Alfaro | Documentation of project contributions | `CONTRIBUTIONS.md` |

## AI Assistance

AI assistance was used during the development and documentation of the verification environment. Generated suggestions were reviewed and tested through the course simulation and mutation-testing tools.

| Where | Used for | Verified by | Where verification shows |
|---|---|---|---|
| `code/tb/fifo_crv/test_fifo.py` | Assistance with cocotb testbench structure, scoreboard calls, timing, and directed boundary tests | Francesca Alfaro | Passing clean RTL simulation |
| `code/dut/fifo.sv` | Explanation and correction of Verilator width warning | Francesca Alfaro | Successful clean RTL compilation |
| `code/tb/fifo_crv/mutants_released.yaml` | Assistance updating the mutant search expression after the RTL width correction | Francesca Alfaro | Successful mutation harness execution |
| `vplan.md` | Assistance reviewing and revising verification documentation | Francesca Alfaro | Comparison against implemented testbench |
| `FINDINGS.md` | Assistance organizing coverage and mutation results | Francesca Alfaro | Recorded 6/8 and 8/8 mutation results |
| `CONTRIBUTIONS.md` | Assistance drafting the contribution record | Francesca Alfaro | Final review against repository history pending |

AI assistance did not replace simulation-based verification. The final testbench was executed against the clean RTL and evaluated using the released mutation pool.

## Attestation

- [ ] Every contribution claim has been checked against repository history.
- [ ] Milestone sections accurately reflect when work was completed.
- [ ] All participating members have reviewed this file.
- [ ] Required confidential individual peer evaluations have been submitted, if applicable.

**Note:** Commit hashes, milestone dates, team membership, and contribution percentages must be verified before submission. This document is a reconstruction of the work discussed during Project 1 and should not be presented as a contemporaneously updated four-milestone record unless that is accurate.