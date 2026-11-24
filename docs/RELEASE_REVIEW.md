# Release Review

| Area | Decision |
|---|---|
| Market-data inputs | Withheld. The original study used Yahoo Finance data. No provider agreement or written redistribution permission was available. The Yahoo legal terms endpoint could not be retrieved from the validation environment. Permission for raw-data access alone would not establish permission to publish aggregates or derivative charts. |
| Market-derived exhibits | Withheld pending a review of applicable terms and data provenance. The four Phase 4 aggregate CSVs and four market-derived figures are excluded, along with historical return, drawdown, benchmark, subgroup and directional performance claims. The original fifth figure is replaced by a text matrix. |
| Alternative evidence | The public-facing draft uses verification counts, a synthetic execution diagram, research methods and the recorded reproduction failure. The synthetic diagram and validation CSV contain no market observations. |
| Code and external dependencies | The execution code and tests are carried over byte-for-byte from the Phase 4 candidate. They use the Python standard library and contain no original notebook engine, private data loader or vendor code. GitHub Actions are referenced by verified release commits, and their source is not bundled. |
| Code rights and license | Owner approval to publish the contributed code and license choice are open. No license has been assigned. If code rights cannot be confirmed, a narrative-only release can omit `src/`, `tests/`, `requirements.txt` and the workflow. Update reproduction links and label the test result as privately verified in that edition. |
| Credentials and personal data | A limited pattern scan covered the release files. Raw account state, emails, credentials, market observations and notebook metadata were excluded. The related-project URLs are intentionally included. |
| History and identity | This draft is prepared in a fresh Git repository with no inherited commits or remotes. Commit only with the owner's approved GitHub noreply address and approved display name. Check both author and committer metadata before any external visibility change. |
| Publication | The owner must clear code rights or choose the narrative-only edition before public release. Keep the earlier archive, work branches and research repository private. |

If written clearance for market-derived exhibits is obtained, add only the cleared material and restore its source labels, limitations and associated claims together. [Research limitations](RESEARCH_LIMITATIONS.md)

See the [provider sources and category-by-category decisions](DATA_PUBLICATION_REVIEW.md).
