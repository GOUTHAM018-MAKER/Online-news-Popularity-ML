# Team contributions

**Project:** Understanding and Predicting Online News Popularity  
**Course:** ES 335

The team reports an equal contribution to the project as a whole. The work was collaborative, rather than divided into separately owned analysis and website components. The areas below describe the shared project work; the 50% share applies to the overall contribution, not a measured allocation of hours to each task.

## Shared project work

- **Problem formulation and scope:** developing the question of whether article-level features improve predictions of recorded social shares over a constant baseline, defining one article as the unit of analysis, and identifying the information available at prediction time.
- **Data understanding and preprocessing:** working with the UCI Online News Popularity dataset, examining its variables and quality issues, and considering the reasons for excluding features with uncertain publication-time availability or fitting provenance. The project documents invalid-ratio handling, median imputation, Ridge scaling and the log-transformed target.
- **Model comparison and evaluation:** working on the comparison of a median baseline, Ridge regression, random forest and boosted trees, using chronological training, validation and test partitions. The evaluation separates validation-based selection from final testing and explains log MAE, RMSLE and raw-share MAE.
- **Results and interpretation:** developing the explanation of the modest improvement over the baseline, the overprediction of low-share articles and underprediction of viral articles, and the limits of the day-level bootstrap interval. The conclusions distinguish predictive association from causation.
- **Website and interaction:** contributing to the presentation of the question, methods, evidence and conclusions on the static website. The promotion-budget explorer lets visitors compare models, channels, budgets and popularity thresholds using precomputed test predictions, precision, recall, lift and selected or missed cases.
- **Reproducibility and documentation:** contributing to the organization of the analysis source, notebook, saved validation trials, exact splits, predictions, setup instructions, data-access information, citations and AI-use disclosure.

## Tools, assistance and attribution

Python and its scientific libraries support the analysis; HTML, CSS and JavaScript support the website. OpenAI Codex and Claude assistance is described in [AI_USE.md](AI_USE.md). Equal team contribution does not mean that every implementation step was written without assistance. The execution checks recorded in [VERIFICATION.md](VERIFICATION.md) are identified separately and are not attributed to independent student reruns.

Both team members share responsibility for the submitted project, its interpretation and the explanation of its methods and limitations.
