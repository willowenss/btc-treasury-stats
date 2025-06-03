# BTC Treasury Stats

Streamlit app that models public company Bitcoin exposure and generates tweetable stat cards.

## Features
- Risk-adjusted BTC coverage time
- Yield-based projections
- Branded stat card image generator
- Company logo overlay (via `assets/`)
- now implemented - full grid view for all companies

GRID VIEW is data from company_data.csv :) just edit this to change data 


### Create a Python virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt  # install dependencies
```

## single company stat card generator 
```bash
streamlit run btc_calc_dev.py
```

## run the dashboard with all companies live in grid-view
```bash
streamlit run btc_master_calc.py
```

Built by Will Owens @ UTXO Management
