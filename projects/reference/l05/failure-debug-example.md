# Intentional failure/debug example — incompatible head count

**Failing configuration:** `width=10`, `n_head=3`.

**Evidence:** the residual stream has 10 feature channels, but three equal heads would require `10 / 3` channels per head, which is not an integer.

**Hypothesis:** the reshape/split contract is invalid before attention scores are even computed.

**Focused check:** assert `width % n_head == 0` before splitting channels.

**Result:** the reference raises `ValueError("embedding width must be divisible by n_head")` immediately.

**Next step:** restore a divisible configuration, then run the separate causal-prefix test because valid shapes alone do not prove that future information is blocked.
