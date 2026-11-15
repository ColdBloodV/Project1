# AI Assistance Log — Project 1: FIFO Verification

**Student:** Francesca Alfaro  
**Project:** FIFO Constrained-Random Verification  
**Date:** November 14, 2026

## AI Tools Used

ChatGPT was used to assist with testbench development, debugging, verification planning, and project documentation.

## AI Assistance Summary

| Task | AI Assistance | Student Verification |
|---|---|---|
| cocotb testbench | Helped develop and debug the constrained-random testbench and scoreboard integration | Executed the testbench using Verilator |
| pyvsc constraints | Helped structure legal randomized FIFO transactions | Verified simulation behavior and functional coverage |
| Functional coverage | Helped organize coverage points and interpret coverage results | Confirmed 49/49 defined coverage bins |
| Mutation testing | Helped diagnose compilation errors and analyze surviving mutants | Executed the mutation harness |
| Directed boundary tests | Helped develop tests for writes while full and reads while empty | Confirmed mutation score improved from 6/8 to 8/8 |
| Verification plan | Helped revise `vplan.md` to reflect implemented functionality | Reviewed against the project implementation |
| Findings | Helped document mutation results and residual risks | Compared with recorded regression results |
| Contributions | Helped prepare `CONTRIBUTIONS.md` | Final accuracy review pending |

## Verification Results

The completed FIFO testbench executed 5,000 constrained-random cycles and achieved 100% of the defined functional coverage bins.

The initial mutation regression detected 6 out of 8 released mutants.

After adding directed overflow and underflow tests, the final mutation regression detected all 8 released mutants.

## Student Responsibility

AI-generated code suggestions were evaluated through simulation and mutation testing. AI-generated documentation was reviewed against the implementation and recorded results.

The student remains responsible for the accuracy, functionality, and submission of the project.

## Limitations

The final regression does not guarantee exhaustive FIFO verification. Additional tests for active reset, alternative FIFO configurations, and random-seed reproducibility could improve verification confidence.