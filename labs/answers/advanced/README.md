# Advanced learner exercise reference answers

These Level 10–15 reference answers are available to learners. Start with the matching incomplete `*-exercise.py` under `labs/notebooks/level-10` through `level-15`. Use lesson hints 1 and 2 first, then compare your implementation with the `*-answer.py` in this directory.

Each reference answer must:

- implement every TODO contract stated by its learner starter;
- include assertions for normal behavior and the important boundary/failure cases;
- contain no `TODO` or `NotImplementedError`;
- emit a `PASS:` marker when its contract tests succeed.

The Level 10–15 smoke runners call:

```bash
python3 labs/answers/advanced/check_exercises.py --level <10-15>
```

That checker proves both sides of the exercise contract:

1. the learner starter compiles but fails specifically at its intended TODO boundary;
2. the corresponding reference answer executes successfully and passes its assertions.

These answers are intentionally linked from learner-facing lessons for self-checking. They are exercise solutions, not project submissions.
