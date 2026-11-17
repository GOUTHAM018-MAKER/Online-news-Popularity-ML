# Understand and defend the project

1. One row is one Mashable article. We predict its recorded shares using conservative publication-time content statistics. The target is a snapshot, not a fixed seven-day outcome.
2. Explain why URL, timedelta, keyword share summaries, referenced-article shares and LDA topics were excluded. LDA is not inherently leaky: its original fitting provenance is unknown, and we cannot refit topics without article text.
3. Describe the date-grouped 60/20/20 split, validation-only selection, then refitting on train+validation before testing. Explain why random splitting can overstate future performance.
4. Explain log MAE, RMSLE and raw MAE. What happens when a 1,000-share article is predicted as 10,000? Why do viral outliers dominate raw MAE?
5. Explain the baseline and three families, the small tuning grid and the train-only preprocessing. Explain why scaling matters for Ridge but not trees.
6. Open the decision explorer. Change the promotion budget and popularity threshold; explain precision, recall and lift. Why does the median baseline use random tie-breaking? Inspect missed popular articles and explain why this is retrospective evaluation rather than evidence that promotion causes more shares.
7. Changing the baseline to a mean of log shares would optimize squared log error rather than absolute log error. Changing the target to fixed-horizon shares would require new labels.
8. The day bootstrap interval describes sampled test days, not all uncertainty or causal effects. Future drift and training randomness are not covered.
9. Explain why an association between an article feature and shares would not prove that editing that feature increases shares.
10. Each student: record actual contribution, explain one implementation detail and one limitation without relying on AI wording.
