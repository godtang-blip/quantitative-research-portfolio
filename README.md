# Quantitative Research Portfolio

Independent research on whether backtest conclusions survive scrutiny of execution, transaction costs and reproducibility.

**Finding** A daily-bar engine can use a price reached before entry to close a trade, and a slippage rule can move a reported fill beyond its limit. The corrected execution model evaluates prices after entry, enforces limit bounds and accounts for residual simulated slippage separately. Daily bars still leave the actual sequence unknown.

| What was checked | Evidence |
|---|---|
| Corrected execution rules | **21 synthetic tests passed**. Four of those assertions had failed against the original functions during private validation. |
| Repeatability with frozen inputs | **24 paired comparisons** reproduced across two short windows in a separate private replay. |
| Archived equity and ETF study | **40 original scenarios** were reconciled to their stored outputs. |
| Historical v5.3 returns | The 2018–2023 reproduction failed its original tolerance. The exact run revision remains unresolved. |

Survivorship bias remains unresolved. No independent out-of-sample evaluation was performed, and full-period performance for the corrected model is unverified. Synthetic examples quantify the four execution differences. Archived market performance exhibits await redistribution clearance.

[Featured study](research/execution-model/README.md) · [Synthetic comparison](research/execution-model/README.md#quantitative-synthetic-comparison) · [Validation evidence](results/validation_evidence.csv) · [한국어 요약](docs/RESEARCH_SUMMARY_KO.md)

ChatGPT and Codex contributed substantially to code generation, error analysis, fixes, tests and documentation. The researcher supplied the source bundle, defined the research question and set the validation scope. [AI development trail](docs/AI_DEVELOPMENT_TRAIL.md) · [Research limitations](docs/RESEARCH_LIMITATIONS.md) · [Data publication review](docs/DATA_PUBLICATION_REVIEW.md)

## Run the synthetic tests

From the repository root with Python 3.12 on macOS or Linux:

```sh
python3.12 -m venv .venv
PYTHONPATH=src .venv/bin/python -B -m unittest discover -s tests -v
```

The suite uses the standard library and synthetic bars. [Reproducibility](docs/REPRODUCIBILITY.md) · [Validation matrix](docs/VALIDATION_MATRIX.md)

## Supplementary research

- [Bitcoin breakout robustness](research/btc-robustness/README.md) documents the design of the archived parameter and cost sensitivity study.
- [GitHub Actions paper trading](research/paper-trading/README.md) describes an archived no-fill automation run. The implementation source was unavailable for review.

## Related Research Projects

- [Asia GARP Research Engine](https://github.com/godtang-blip/ai-quant-asia-garp-research) · Quantitative screening and AI-assisted financial data processing. Predictive validity of the scores remains unverified.
- [DB HiTek Equity Research Report](https://github.com/godtang-blip/ai-quant-asia-garp-research/blob/main/case-studies/db-hitek/db-hitek-equity-research-2026-11-20.pdf) · Company fundamental analysis and valuation case study.
