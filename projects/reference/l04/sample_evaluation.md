# Sample evaluation — p04-tokenizer-workbench

This is an example of applying the rubric to the committed reference solution. It is not a required learner wording template.

| Criterion | Score | Evidence |
|---|---:|---|
| Deterministic tokenization and vocabulary | 15/15 | Regex split is deterministic; special IDs are fixed at 0–3; sorted ordinary vocabulary is repeatable. |
| Subword and byte representations | 14/15 | Suffix-based subword reuse and UTF-8 round-trip both work. The toy subword rule is intentionally narrower than a production learned tokenizer. |
| Special tokens, padding, truncation, masks | 20/20 | BOS/EOS are preserved under truncation; padding uses ID 0; masks align exactly. |
| Embedding and position alignment | 15/15 | One embedding row is returned per ID; real token positions follow the mask. |
| Context/evaluation reasoning | 14/15 | Fixed slices expose efficiency/coverage tradeoffs. The tiny evaluator does not benchmark latency or downstream model quality. |
| Failure analysis and debugging | 10/10 | Rare-name/emoji/multilingual slices expose word-vocabulary coverage failures and preserve the exact evidence needed to debug. |
| Reproducibility and communication | 10/10 | Standard-library-only reference passes the objective validator with committed deterministic fixtures. |

**Total: 98/100**

## Example decision note
The tiny word vocabulary is efficient on familiar text but loses unseen words to `<unk>`, so it is not a safe general-purpose representation. The byte path preserves every supplied UTF-8 string, including emoji and Korean text, but can use more positions. The suffix-based subword path shows how reusable pieces can reduce whole-word dependence, although this toy rule is not a trained production tokenizer. For a user-generated multilingual product, coverage failures are more serious than a small token-count win on familiar English, so the word-only vocabulary would not be selected. I would next evaluate a real learned subword tokenizer on a larger representative corpus. I would also measure downstream context usage and model quality before making a production decision.

## Example debug note
- **Failing input:** `quokka predicts`
- **Evidence:** the word tokenizer maps `quokka` to `<unk>` while UTF-8 bytes preserve every character.
- **Hypothesis:** the word vocabulary was built from a narrow training corpus and has no reusable smaller pieces for the unseen name.
- **Focused check:** inspect the training vocabulary and compare the same input with byte/subword-style pieces.
- **Result:** the word path loses identity; the byte path keeps the spelling; the toy subword rule still does not fully solve this unseen stem.
- **Next step:** train/evaluate a real subword vocabulary on representative names and multilingual slices.
