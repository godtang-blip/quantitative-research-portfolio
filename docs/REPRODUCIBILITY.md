# Reproducibility

The corrected model and tests use the CPython standard library. The release check used an isolated Python 3.12.14 virtual environment.

```sh
python3.12 -m venv .venv
PYTHONPATH=src .venv/bin/python -B -m unittest discover -s tests -v
```

Expected result is 21 passing tests, including four portable assertions that failed against the original functions in the earlier private audit. The published synthetic suite exercises the corrected implementation. The figure mirrors a synthetic input from `tests/test_regressions.py`.

The [validation CSV](../results/validation_evidence.csv) records check scope and provenance. Reproducing the historical 24 pairs requires the private frozen market snapshots, settings and original notebook functions used in the restricted replay. The Phase 4 test code and execution layer were carried over unchanged. The original notebook loader and market inputs are absent. Earlier v5.3 inputs, daily NAV and execution revision remain incomplete.

The bundled workflow runs the same synthetic tests on Python 3.12 using read-only repository permissions. The assertions need no market data, credentials or live accounts.
