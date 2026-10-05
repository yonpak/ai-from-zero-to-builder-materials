# Data Detective — Core Evidence Report

Use this template with the canonical browser Lab in Lesson 0.12. Short, specific answers are better than long general statements.

## 1. Prediction task

- What is the feature?
- What is the label?
- In your own words, what does the threshold predictor do?

## 2. Fair evidence

- Which examples are used for learning/choosing the rule?
- Which examples are held out for evaluation?
- Why would repeatedly changing the threshold after reading final test answers weaken the fairness of that test?

## 3. Starter result

Run the Lab unchanged.

- `before`:
- `after`:
- `baseline`:
- Which specific held-out example is fixed by the candidate threshold?
- What does the baseline give you that the model score alone does not?

## 4. Intentional unsuccessful change

Change only:

```python
candidate_threshold = 3
```

to:

```python
candidate_threshold = 2
```

Before running, write your prediction:

- What should happen to input `2`?

Then run the Lab.

- new `before`:
- new `after`:
- new `baseline`:
- Which example is now wrong, and why?

## 5. Debug record

- **Failure:**
- **Evidence:**
- **Hypothesis:**
- **One change/check:**
- **Result:**
- **Next step:**

## 6. Conclusion

Write 4–8 sentences that answer:

- Which threshold performed better on this held-out set?
- Did it beat the majority baseline?
- What evidence supports that claim?
- What does this tiny experiment **not** prove?
- Name one limitation or one kind of new case you would want to test next.
