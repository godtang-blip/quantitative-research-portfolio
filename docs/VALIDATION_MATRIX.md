# Validation Matrix

| Check | Status | Scope |
|---|---|---|
| Synthetic execution verification | Pass | 21 tests in an isolated Python 3.12 environment. Four matching assertions failed against original code in prior private validation. |
| Short-window repeatability | Pass | 24 pairs reproduced in two private short-window runs with the same frozen input. |
| Archive arithmetic | Pass | 40 original scenario summaries reconciled with stored files. |
| Historical v5.3 reproduction | Fail | Earlier multi-year results did not reproduce within the original tolerance. |
| Exact notebook and runtime | Partial | Common functions matched. The actual run revision remains unknown. |
| Corrected full-period performance | Unverified | Only restricted short comparisons were run. |
| Independent sample and survivorship | Unverified | Independent evaluation was not performed. The universe uses later survivors. |
| Actual execution | Unverified | Intraday sequences, order-book position and fills are unknown. |

[Machine-readable evidence](../results/validation_evidence.csv)
