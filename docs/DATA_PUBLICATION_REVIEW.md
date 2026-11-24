# Market Data Publication Review

Reviewed on 2026-11-24. The archived equity/ETF run used Yahoo Finance adjusted daily OHLCV through `yfinance`. The v5.6 Bitcoin and SPY inputs were frozen Yahoo price snapshots. The material available for review did not establish the upstream exchange/vendor contract, the contract applicable when the data were acquired, or a separate redistribution grant.

## Sources and applicable scope

- Yahoo's [Terms of Service](https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html), [Yahoo Finance product terms endpoint](https://legal.yahoo.com/us/en/yahoo/terms/product-atos/finance/index.html) and [API terms referenced by yfinance](https://policies.yahoo.com/us/en/yahoo/terms/product-atos/apiforydn/index.htm) are the provider-side sources to examine for content use, disclosure, redistribution and downstream display. The network denied access to the terms hosts, so the current text, exact provider clause numbers and applicability could not be verified. No Yahoo clause is quoted or treated as a grant.
- The [yfinance README caution and Legal Stuff section](https://github.com/ranaroussi/yfinance#legal-stuff) were retrieved. The README says the API is intended for personal use and directs data users to Yahoo terms for rights over downloaded data. That statement is the library maintainer's notice. It does not establish a license from Yahoo or an upstream vendor.
- The [yfinance Apache 2.0 license, Section 4, Redistribution](https://github.com/ranaroussi/yfinance/blob/main/LICENSE.txt) applies to use and redistribution of the software under that license. It does not license fetched market data. This repository includes no yfinance code and the executable synthetic suite uses the Python standard library. Portfolio-code publication approval and a project license are separate owner decisions.

## Release decisions

| Material | Decision | Basis |
|---|---|---|
| Raw market snapshots | Withhold | No verified redistribution grant or independent permission from an upstream provider. |
| Security-level time series and adjusted price or volume exports | Withhold | A subset, export or change of format still carries vendor observations. |
| Researcher-calculated aggregate returns, risk metrics, simulated realized trade counts and benchmark comparisons | Withhold pending clarification | These products differ from raw data exports. The reviewed material did not establish whether non-reconstructable aggregates are covered by a permission or exception. |
| Researcher-produced charts made from aggregates | Withhold pending clarification | Figure authorship and permission to publish the underlying derived values require separate review. |
| Synthetic execution counterexamples and their chart | Included in the private review draft | Inputs are hand-specified regression bars and order levels, without vendor observations. Code and figure publication remain subject to owner approval. |

After written confirmation, prioritize the 2023 Range E short-window cumulative returns, drawdowns, realized trade counts, same-period benchmark and execution comparison figure. Check the equity cost-sensitivity aggregates and BTC distributions separately. Include the scenario definitions and short-window limits with any restored values.
