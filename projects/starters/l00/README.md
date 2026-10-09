# p00-data-detective — Data Detective: Build and Explain a Tiny Predictor

## Goal
Demonstrate that you can define a tiny prediction task, preserve fair evaluation evidence, compare a baseline, investigate a failure, and explain what the evidence does and does not support.

## Prerequisites
Complete Level 0 through L0.12, [Debug and Improve a Tiny Predictor](https://aizero.ruzincompany.com/learn/00-level-0/l00-12-debug-and-improve-a-tiny-predictor). You should be able to identify features and labels, explain a train/test split, count prediction mistakes, compare against a baseline, and change one thing at a time.

You have **two valid completion paths**. The Level 0 learning goal is experimental reasoning, so local Python is not required for Core completion.

## Path A — Core: browser evidence + explanation

Use this path if you have not learned repository, terminal, or Python implementation workflow yet.

1. Open L0.12, [Debug and Improve a Tiny Predictor](https://aizero.ruzincompany.com/learn/00-level-0/l00-12-debug-and-improve-a-tiny-predictor), and run its Lab unchanged.
2. Record the starter `debug_record`, especially `before`, `after`, and `baseline`.
3. Find `candidate_threshold = 3` in the Lab and change only `3` to `2`.
4. Before running, predict what will happen to input `2`.
5. Run again and record the new `before`, `after`, and `baseline` values.
6. Fill in the Core Evidence Report template, [CORE_REPORT_TEMPLATE.md](CORE_REPORT_TEMPLATE.md). To get it as a file, open the [Data Detective project page](https://aizero.ruzincompany.com/projects/p00-data-detective), choose **Download project files**, and unzip the download; the template is inside. You can also open the template link and copy its prompts into your own document.

This path is complete when your evidence report demonstrates all five rubric areas. There is no upload or grading service: you keep the report and score it yourself against the rubric on the project page. You do not need to implement Python functions or run a terminal validator for the Core path.

## Path B — Builder: local Python implementation

Use this path when you want to practice turning the same reasoning into code.

If repository/terminal workflow is new, read the [Project Workbench](https://aizero.ruzincompany.com/project-workbench) first. It explains the repository root, terminal, validator, and the setup-debugging order.

### Setup

No third-party packages are required. Use Python 3.11+ from the repository root.

Open `projects/starters/l00/data_detective.py` and complete the marked TODOs.

Your program must:
1. treat the numeric measurement as the **feature** and `ready` as the **label**;
2. choose a threshold using only `TRAIN_EXAMPLES`;
3. evaluate the chosen threshold on `TEST_EXAMPLES` without tuning on the test answers;
4. compare test mistakes with a majority-label baseline learned from the training labels;
5. produce a short report containing the chosen threshold, model mistakes, baseline mistakes, and a cautious conclusion;
6. investigate the intentional `NOISY_TEST_EXAMPLES` scenario and write a short debug note.

### Builder deliverables
- completed `data_detective.py`;
- terminal output from the validation command;
- a short `debug-note.md` containing: observed failure, hypothesis, one change, result, and next step;
- a 4–8 sentence explanation of what the held-out evidence supports and one limitation.

### Builder validation
From the repository root, run:

```bash
python projects/tests/l00/validate_submission.py projects/starters/l00/data_detective.py
```

Expected success evidence ends with:

```text
PASS: p00-data-detective objective checks
```

The checks are behavioral. Your printed wording does not need to match a reference solution exactly.

## Intentional failure/debug path

Both completion paths must include a failure investigation.

- Core path: change the L0.12 candidate threshold from `3` to `2` and explain why input `2` becomes a mistake.
- Builder path: after the clean evaluation passes, evaluate `NOISY_TEST_EXAMPLES`, identify the conflicting example, state one hypothesis, run one focused check/change, and record what the evidence supports.

Do not immediately change several things. A failed hypothesis is still useful evidence when it is recorded.

## Reproducibility and provenance
The project uses deterministic, synthetic teaching data. No external dataset, model, network access, credentials, or secrets are required.

The browser Core path is reproducible from the canonical L0.12 starter and recorded edit. The Builder validation path uses only Python's standard library.