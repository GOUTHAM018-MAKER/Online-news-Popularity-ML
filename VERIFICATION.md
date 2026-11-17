# Verification record

## Completed execution and integrity checks

These checks were run automatically during project preparation with OpenAI Codex. This record identifies the checks performed; it does not attribute their execution to either student.

- **Full analysis and independent rerun:** the complete seven-candidate pipeline ran on the supplied CSV, followed by a separate rerun in an isolated working directory. Both runs used Python 3.13.9, NumPy 2.3.5, pandas 2.3.3, scikit-learn 1.7.2 and Matplotlib 3.10.6. They produced the same CSV checksum, 41 included features, row-level splits, validation choices and winning model (random forest, leaf size 30). All exported metrics and held-out predictions matched within absolute tolerance 1e-10. No example result from a newer library version is claimed.
- **Split integrity:** verified 39,644 unique original row IDs, no dates shared between partitions, strict chronological ordering and exact test row-ID correspondence between splits and predictions.
- **Exported metrics:** recomputed all four models' log MAE from test_predictions.csv and matched summary.json to numerical precision.
- **Notebook execution:** all eight code cells in notebooks/analysis.ipynb were executed successfully; execution counts and outputs are saved. Execution used Python 3.13.9 and IPython 9.7.0 in a shared in-process namespace, without a networked Jupyter kernel. The cells inspect canonical results and independently recompute metrics; full training is done separately by analyze.py. Notebook structure was validated with nbformat 5.10.4.
- **Website content and links:** generated docs/index.html from src/build_site.py, checked all local assets exist, verified every one of the 11 navigation targets, unique element IDs and conclusion/reproduction ordering. The conclusion and reproduction details use summary.json, and docs/README.md matches the root README exactly.
- **Interaction logic:** JavaScript syntax checks and mocked-DOM execution passed for all four models, all three popularity thresholds, and promotion budgets of 1%, 10% and 50%. Shortlist and missed-popular views, empty data, a zero-popular sample, deterministic learned-model ties and the constant-baseline random-tie expectation were checked. Both repository links resolve to the expected source URL on standard GitHub Pages URLs.
- **Independent interaction arithmetic:** a separate pandas calculation matched the JavaScript default allocation: 932 promoted, 236 hits among 1,047 popular articles; precision 0.2532188841, recall 0.2254059217 and lift 2.2521244020.
- **Scope preservation:** the original analysis source, bundled result files and style.css were left unchanged. The separate rerun did not replace the canonical results.

## Browser and publication status

Real desktop/mobile rendering, console status and the published GitHub Pages deployment are not verified by these automated checks. The chart's larger left margin and horizontally scrolling navigation are implemented, but need a visual browser check, especially at 390px width. Mocked canvas/DOM execution does not establish a rendered layout. No publication or portal submission is recorded here.

## Student confirmation record

Independent student reruns, browser checks and actual contributions remain to be confirmed by the authors. Record completed checks and observations here after doing them; proposed review responsibilities are in CONTRIBUTIONS.md.


## Review performed on 17 November 2026

A fresh isolated full training run used the UCI public ZIP, Python 3.13.9 and the pinned library versions. Validation trials, feature manifest, metrics.csv and splits.csv matched the supplied exports exactly. Test prediction exports matched within 1e-10; tiny floating-point differences in error summaries and bootstrap endpoints did not change displayed results. Canonical outputs were retained.

Independent recomputation from exported predictions matched all four models’ log MAE, RMSLE and raw-share MAE. Split chronology, unique row IDs, test-row correspondence and browser prediction data were checked. Default explorer arithmetic matched 932 promoted, 236 hits, 1,047 popular, precision 25.3%, recall 22.5% and lift 2.25.

Browser review verified the opening takeaway at a narrow phone layout, navigation to the explorer, baseline random-tie interpretation and missed-popular case selection. No browser errors or warnings were reported during these checks. This was a focused browser check, not an exhaustive device or control matrix.

The short AI disclosure names Codex and Claude. Repository links point to the supplied submission repository. GitHub upload and Pages publication remain blocked by account access; no public deployment was verified. Student contributions and independent understanding remain to be confirmed by the authors. Earlier entries describe bundled historical checks; this section records this review separately.
