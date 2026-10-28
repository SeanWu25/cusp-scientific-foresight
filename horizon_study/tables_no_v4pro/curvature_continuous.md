# Curvature for continuous horizon outcomes (FRQ score, date score)

Event-stratified curvature: OLS of the outcome on squared centred horizon (years) with event and model fixed effects, event-clustered SE (analogue of the conditional-logit curvature for Binary/MCQ). GLMM quadratic: the h+h2 crossed random-intercept fit (pooled.json).

| corpus | task | items / events | GLMM quadratic [95% CI] | event-stratified curvature [95% CI] (p) |
|---|---|---|---|---|
| Original | frq | 18,461 / 4,135 | -0.050 [-0.081, -0.019] | -0.055 [-0.090, -0.021] (0.0014) |
| Original | date | 11,285 / 2,752 | -0.092 [-0.104, -0.079] | -0.076 [-0.087, -0.065] (1.1e-39) |
| Merged | frq | 23,398 / 4,765 | +0.010 [-0.010, +0.029] | +0.012 [-0.009, +0.034] (0.27) |
| Merged | date | 12,765 / 2,948 | -0.055 [-0.065, -0.045] | -0.032 [-0.043, -0.022] (8.4e-10) |
