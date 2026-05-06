# Silicon Island 🇹🇼

Interactive data dashboard about Taiwan's role in the global semiconductor supply chain. Made for CPSC 481 (Information Visualization) at NTUST.

**Live demo:** [silicon-island.onrender.com](https://taiwan-chip-dashboard.onrender.com)
*(hosted on Render free tier — might take ~30 seconds to wake up if nobody's visited recently, just wait it out)*

---

## What is this?

Taiwan makes around 90% of the world's most advanced chips. That's kind of insane when you think about it — one natural disaster or geopolitical incident and basically every supply chain on the planet breaks. Cars, iPhones, servers, medical equipment, all of it.

I wanted to actually visualize how deep that dependency goes, so I built this dashboard using real trade data. There are three main sections:

- **The Story** — walks you through the whole picture: Taiwan's export economy, how chip fabrication actually works, who depends on it, and what countries are (or aren't) doing to reduce that dependency
- **Deep Dive** — more detailed charts if you want to dig into specifics: trade flows, TSMC revenue breakdowns, which industries are most exposed, how markets reacted to geopolitical events
- **Explore Data** — open-ended exploration where you can filter by country, product category, or commodity. Has data going back to the early 2000s for 60+ countries

---

## Data sources

Everything here is real data — no made-up numbers or illustrative estimates.

| Dataset | Source |
|---|---|
| Taiwan export destinations (2006–2024) | ITC Trade Map |
| Taiwan exported products by HS category | ITC Trade Map |
| IC chip exports (HS 8542, 1997–2024) | UN Comtrade |
| TSMC annual financials | TSMC Investor Relations |
| Taiwan GDP (quarterly) | Taiwan DGBAS |
| TAIEX index | Taiwan Stock Exchange |
| US–Taiwan bilateral trade | US Census Bureau |
| Country-level commodity breakdowns | Taiwan MOEA |

---

## Running it locally

You'll need Python 3.10+ and the dataset files (not in the repo because they're too big).

```bash
git clone https://github.com/yourusername/taiwan-chip-dashboard
cd taiwan-chip-dashboard
pip install -r requirements.txt
streamlit run app.py
```

The app looks for a `../Datasets/` folder relative to the project root. It should look like this:

```
Datasets/
├── Destinations/          # ITC Trade Map destination CSVs
├── Products/              # ITC Trade Map product CSVs
├── Trade/                 # UN Comtrade IC export CSVs
├── tsmc/                  # tsmc_wafer_revenue_summary.csv
├── Exports by Country:Region and Detailed Commodity Category/
├── US-Taiwan Trade.xlsx
├── Taiwan official statistics (MOEA:DGBAS).csv
└── Market Data/
    └── chart_*.csv        # TAIEX daily prices
```

---

## Deploying on Render

There's a `render.yaml` in the repo so most of the setup is automatic.

1. Push to GitHub (make sure the datasets are included or hosted somewhere)
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect the repo
4. Render will pick up `render.yaml` and configure everything
5. Deploy — first build takes a few minutes

Free tier spins down after inactivity, so the first visit is slow. Nothing I can do about that without paying for a plan.

---

## Stack

- **Streamlit** — app framework
- **Plotly** — charts and the animated choropleth map
- **Pandas / NumPy** — data wrangling
- **D3.js + TopoJSON** — custom world map (embedded as an HTML component)
- **OpenPyXL** — reading the MOEA Excel files

---

## Project structure

```
taiwan_dashboard/
├── app.py                  # entry point, navigation
├── data_loader.py          # all data loading and caching
├── config.py               # paths and color constants
├── styles.py               # global CSS injection
├── plotly_style.py         # shared chart theme
├── tabs/
│   ├── overview.py         # The Story tab
│   ├── deep_dive.py        # Deep Dive tab
│   ├── explore.py          # Explore Data tab
│   ├── hero.py             # hero section with flag map
│   ├── tsmc.py             # TSMC financials charts
│   ├── trade.py            # trade flow charts
│   ├── stranglehold.py     # IC export growth
│   ├── exposure.py         # industry exposure
│   ├── scenarios.py        # supply chain fragility
│   ├── geopolitics.py      # TAIEX + geopolitical events
│   └── destination_choropleth.py  # animated world map
```

---

*CPSC 481 · Spring 2026*
