# Why Did It Move?

KPI anomaly detection and automated root-cause analysis, built on synthetic UK motor-insurance renewal data.

## The problem

When a KPI such as the renewal rate suddenly moves, analysts spend hours slicing the data by channel, region and age to find out why. This project automates that.

## How it works

1. **Detect.** Each month's renewal rate is compared with the previous 6 months using a robust z-score (median and MAD), so past outliers don't distort the baseline.
2. **Explain.** The change in the overall rate is split by segment into a **rate effect** (customers in the segment behaved differently) and a **mix effect** (the segment's share of customers changed). Contributions add up exactly to the total change within each dimension.

## Key result

The data contains a planted incident: from June 2025, price-comparison-website (PCW) customers receive larger premium increases. The tool detected the June 2025 drop (robust z of about -25) and identified **channel = PCW** as the top driver of the -9.1 point move, with no hints given.

## Run it yourself

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.generate_data
python -m src.load_db
pytest -q
```

## Data note

The data is synthetic, generated with a hidden incident, because real insurer data is confidential.

## Limitations and next steps

- With a threshold of 3.0 the detector raised four false alarms (Sep 2024, Apr 2025, May 2025, Dec 2025) because natural variance in the synthetic data is very low. Requiring a minimum absolute move (for example 1 percentage point) would remove them.
- Analysis is one dimension at a time. Segments from different dimensions overlap, so contributions must not be added across dimensions. Two-way combinations such as PCW x age band are a next step.
- No significance test per segment yet.
- Next: a BigQuery version of the SQL, and a Looker or Power BI dashboard.
