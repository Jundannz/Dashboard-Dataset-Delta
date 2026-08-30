# FIRELINE: Kalimantan Wildfire Monitoring & Population Impact Dashboard

Interactive geospatial dashboard for monitoring NASA FIRMS VIIRS thermal hotspots across Kalimantan, cross-referenced with BPS provincial population density to support wildfire and haze-exposure mitigation planning.

**Live Demo:** [dashboard-dataset-delta.streamlit.app](https://dashboard-dataset-delta.streamlit.app/)

---

## Overview

FIRELINE ingests VIIRS 375m active-fire detections and lets analysts filter, visualize, and prioritize hotspots by confidence level, satellite pass time, and fire radiative power (FRP). A companion population-density layer (BPS) contextualizes which provinces face the highest exposure risk from smoke and haze, supporting triage decisions for ground verification teams.

## Data Architecture

| Source | Description | Key Attributes |
|---|---|---|
| **NASA FIRMS (VIIRS, 375m)** | Satellite-derived thermal anomaly detections over Kalimantan | `latitude`, `longitude`, `frp`, `acq_date`, `acq_time`, `confidence`, `daynight` |
| **BPS Indonesia** | Provincial population and land area statistics | Population, area (km²), computed density (jiwa/km²) — West, Central, South, East Kalimantan |

Population data is currently embedded in `app.py` as a static reference table; it is not sourced from an external file.

## Tech Stack

- Python 3.10+
- [Streamlit](https://streamlit.io/) — web application framework
- [Pandas](https://pandas.pydata.org/) — data loading and filtering
- [Plotly Express](https://plotly.com/python/plotly-express/) — interactive spatial map and charts

## Repository Structure

```
dashboard-fireline/
├── app.py                  # Main Streamlit application
├── firms_kalimantan.csv    # VIIRS hotspot dataset
├── requirements.txt        # Python dependencies
└── README.md
```

## Local Installation & Setup

**1. Clone the repository**
```bash
git clone https://github.com/<your-org>/Dashboard-Dataset-Delta.git
cd Dashboard-Dataset-Delta
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Run the app**
```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`.

## Key Metric Definitions

| Term | Definition |
|---|---|
| **FRP (Fire Radiative Power)** | Measured in megawatts (MW); quantifies the radiant heat output of a detected fire. Higher FRP generally indicates larger or more intense burning, making it a proxy for fire severity. Hotspots with FRP > 50 MW are flagged as "Critical" in this dashboard. |
| **Confidence** | VIIRS detection confidence flag: `h` (High), `n` (Nominal), `l` (Low). Indicates the algorithm's certainty that a detected pixel is an actual fire versus a false positive (e.g., sun glint, hot surfaces). |
| **Daynight** | Satellite overpass timing: `D` (Day) or `N` (Night), based on solar zenith angle at detection time. |