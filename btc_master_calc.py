import math
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta
import io
import os

BTC_PRICE = 109_000  # Hardcoded BTC price

TICKER_LOGOS = {
    "gns": "gns.png",
    "kulr": "kulr.png",
    "mooninc": "mooninc.jpg",
    "smlr": "smlr.png",
    "jetking": "jetking.png",
    "metaplanet": "metaplanet.jpg",
    "mstr": "mstr.png",
}

st.set_page_config(page_title="BTC Treasury Dashboard", layout="wide")
st.markdown("<h1 style='text-align: center;'>₿TC Treasury Dashboard - Multi-Company View</h1>", unsafe_allow_html=True)

# Load CSV data
DATA_PATH = "company_data.csv"
df = pd.read_csv(DATA_PATH)

# Display each company's stat card
for index, row in df.iterrows():
    name = row['name']
    ticker = row['ticker']
    shares_outstanding = row['shares_outstanding']
    share_price = row['share_price']
    btc_nav = row['btc_nav']
    fiat_debt = row['fiat_debt']
    btc_yield_ytd = row['btc_yield_ytd']
    months_since_start = row['months_since_start']
    current_mnav = row['current_mnav']
    projected_yield = row['projected_yield']
    risk_score = row['risk_score']

    # --- Compute Results ---
    market_cap = shares_outstanding * share_price
    btc_yield_multiple = 1 + (projected_yield / 100)
    btc_yield_1y = btc_yield_multiple ** (12 / months_since_start)

    if btc_yield_1y <= 1 or current_mnav <= 1:
        months_to_cover = float('inf')
    else:
        months_to_cover = math.log(current_mnav) / math.log(btc_yield_1y) * 12

    days_to_cover = months_to_cover * 30.44
    risk_adjusted_days = days_to_cover * risk_score
    risk_adjusted_months = months_to_cover * risk_score
    projected_date = (datetime.today() + timedelta(days=risk_adjusted_days)).strftime("%b %d, %Y")

    # --- Generate Stat Card ---
    img = Image.new('RGB', (1000, 1000), color='white')
    draw = ImageDraw.Draw(img)
    try:
        font_title = ImageFont.truetype("Arial Bold.ttf", 50)
        font_sub = ImageFont.truetype("Arial.ttf", 44)
        font_bold = ImageFont.truetype("Arial Bold.ttf", 48)
    except:
        font_title = font_sub = font_bold = ImageFont.load_default()

    today_str = datetime.today().strftime("%b %d, %Y")
    draw.text((50, 50), f"BTC Treasury Snapshot", font=font_title, fill='black')
    draw.text((50, 100), today_str, font=font_sub, fill='black')
    draw.text((50, 140), f"{name} ({ticker})", font=font_bold, fill='black')
    draw.line([(50, 200), (950, 200)], fill="#e0e0e0", width=2)
    draw.text((50, 240), "Risk-Adjusted Days to Full Coverage:", font=font_bold, fill='black')
    draw.text((60, 300), f"{risk_adjusted_days:.0f} days", font=font_bold, fill='#f2a900')
    draw.text((50, 360), "Risk-Adjusted Months to Full Coverage:", font=font_bold, fill='black')
    draw.text((60, 420), f"{risk_adjusted_months:.2f} months", font=font_bold, fill='#f2a900')
    draw.text((50, 540), "Projected Date to Full Coverage:", font=font_bold, fill='black')
    draw.text((60, 590), projected_date, font=font_bold, fill='#f2a900')
    draw.text((50, 860), "@UTXOmgmt", font=font_sub, fill='black')
    draw.text((50, 920), "utxo.management", font=font_bold, fill='black')

    try:
        logo = Image.open("assets/utxologo.webp").convert("RGBA")
        logo.thumbnail((150, 150))
        img.paste(logo, (img.width - logo.width - 30, 30), logo)
    except:
        st.warning("UTXO logo not found.")

    logo_filename = TICKER_LOGOS.get(ticker.lower())
    if logo_filename:
        try:
            logo_path = f"assets/{logo_filename}"
            logo = Image.open(logo_path).convert("RGBA")
            logo.thumbnail((120, 120))
            img.paste(logo, (img.width - logo.width - 30, img.height - logo.height - 30), logo)
        except Exception as e:
            st.warning(f"Error loading company logo for {ticker}: {e}")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()

    if index % 3 == 0:
        cols = st.columns(3)  # new row every 3 items

    with cols[index % 3]:
        st.image(img, caption=f"{name} ({ticker.upper()}) Stat Card", width=300)
        st.download_button(
            "Download Image", 
            data=byte_im, 
            file_name=f"{ticker}_stat_card.png", 
            mime="image/png"
        )