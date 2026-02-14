# Volatility Regime Mini

## Data Source
- Source: `yfinance` SPY daily history, saved locally as `/Users/livefree/projects/volatility-regime-mini/data/spy.csv`.
- Working range for this mini workflow: `2008-01-01` to `2024-12-31`.
- Step 1 output: `/Users/livefree/projects/volatility-regime-mini/data/spy_2008_2024_returns.csv` with columns:
  - `date, close, return`
  - `return = log(close_t / close_{t-1})`

## Feature Design Logic
- Step 2 builds daily features in `/Users/livefree/projects/volatility-regime-mini/data/spy_2008_2024_features.csv`.
- Feature vector:
  - `vol10`: 10-day rolling volatility of returns
  - `vol30`: 30-day rolling volatility of returns
  - `mean10`: 10-day rolling mean of returns
  - `mean30`: 30-day rolling mean of returns
  - `r_lag1, r_lag2, r_lag3`: lagged returns
- After rolling windows and lags, incomplete rows are dropped.

## Baseline Method
- Step 3 uses `/Users/livefree/projects/volatility-regime-mini/src/baseline.py`.
- Pipeline:
  - Standardize features with z-score.
  - Run KMeans clustering for `k=2` and `k=3`.
  - Save labels into `/Users/livefree/projects/volatility-regime-mini/data/spy_2008_2024_regimes.csv` as:
    - `cluster_k2`
    - `cluster_k3`

## Observation Summary (V1)
- Regime labels are strongly tied to volatility level.
  - `k=2` avg `vol30`: cluster `0` = `0.0253`, cluster `1` = `0.0089`.
  - `k=3` avg `vol30`: cluster `0` = `0.0409` (highest-vol), cluster `2` = `0.0128`, cluster `1` = `0.0084`.
- High-vol periods are visibly separated in the overlay plots:
  - `/Users/livefree/projects/volatility-regime-mini/experiments/close_regime_overlay.png`
  - `/Users/livefree/projects/volatility-regime-mini/experiments/vol30_regime_overlay.png`
- 2008 and 2020 show clear regime concentration shifts (especially in higher-vol clusters), but 2008 is more extreme.
- Regime persistence exists but is uneven:
  - `k=3` average run length is ~`19.25` days for cluster `1` and ~`5.8` days for cluster `2`.
  - This suggests a dominant low-vol regime with shorter noisy transitions.

## Current Questions
- Is clustering mostly a volatility proxy rather than a richer latent market state?
- How much regime switching is true structural change vs. noise oscillation?
- Is there lag between market shocks and regime reassignment due to rolling-window features?
- Would a learned representation (autoencoder latent space) produce cleaner regime boundaries and fewer short flips?
