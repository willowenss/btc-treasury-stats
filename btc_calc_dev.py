import math
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta
import io

BTC_PRICE = 109_000  # Hardcoded BTC price

ticker_logos = {
    "gns": "gns.png",
    "kulr": "kulr.png",
    "mooninc": "mooninc.jpg",
    "smlr": "smlr.png",
    "jetking": "jetking.png",
    "metaplanet": "metaplanet.jpg",
    "mstr": "mstr.png",
}

st.set_page_config(page_title="BTC Risk-Adjusted Visual", layout="centered")
col1, col2 = st.columns([5, 1])
with col1:
    st.title("₿TC Treasury Analysis")
with col2:
    try:
        logo = Image.open("assets/utxologo.webp")
        st.image(logo, width=100)
    except:
        st.warning("UTXO logo not found.")

def parse_number(label, default=0.0):
    raw = st.text_input(label, value=f"{default:,}")
    try:
        return float(raw.replace(",", ""))
    except:
        return 0.0

# Inject compact CSS to reduce padding/margin/font
st.markdown("""
    <style>
    div[data-baseweb="input"] input {
        font-size: 13px;
        padding: 6px;
    }
    label {
        font-size: 13px !important;
    }
    .stTextInput, .stNumberInput {
        margin-bottom: 5px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Grouped into two columns for space efficiency
col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Company Name")
    ticker = st.text_input("Ticker")
    shares_outstanding = parse_number("Shares")
    share_price = parse_number("Share Price (USD)")
    btc_nav = parse_number("BTC NAV (USD)")
    fiat_debt = parse_number("Fiat Debt (USD)")

with col2:
    btc_yield_ytd = parse_number("BTC Yield YTD (%)")
    months_since_start = parse_number("YTD Months", default=1)
    current_mnav = parse_number("Current mNAV")
    projected_yield = parse_number("Projected BTC Yield (%)", default=btc_yield_ytd)
    risk_score = parse_number("Risk Score (1 = neutral, >1 = riskier, <1 = safer)", default=1.0)
# --- Compute Results ---
if st.button("Generate Visual"):
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

    # --- Generate Vertical Stat Card ---
    img = Image.new('RGB', (1000, 1000), color='white')
    draw = ImageDraw.Draw(img)


    try:
        font_title = ImageFont.truetype("Arial Bold.ttf", 50)
        font_sub = ImageFont.truetype("Arial.ttf", 44)
        font_bold = ImageFont.truetype("Arial Bold.ttf", 48)
    except:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_bold = ImageFont.load_default()

    # Draw text (cleaner, no emojis)
    # Title with date
    today_str = datetime.today().strftime("%b %d, %Y")
    draw.text((50, 50), f"BTC Treasury Snapshot", font=font_title, fill='black')
    try:
        font_italic = ImageFont.truetype("Arial Italic.ttf", 44)
    except:
        font_italic = font_sub

    draw.text((50, 100), today_str, font=font_italic, fill='black')

    draw.text((50, 140), f"{name} ({ticker})", font=font_bold, fill='black')

    draw.line([(50, 200), (950, 200)], fill="#e0e0e0", width=2)

    draw.text((50, 240), "Risk-Adjusted Days to Full Coverage:", font=font_bold, fill='black')
    draw.text((60, 300), f"{risk_adjusted_days:.0f} days", font=font_bold, fill='#f2a900')

    draw.text((50, 360), "Risk-Adjusted Months to Full Coverage:", font=font_bold, fill='black')
    draw.text((60, 420), f"{risk_adjusted_months:.2f} months", font=font_bold, fill='#f2a900')


    # draw.text((50, 440), "BTC Yield 1Y Annualized %:", font=font_bold, fill='black')
    # draw.text((60, 490), f"{btc_yield_1y:.2f}%", font=font_bold, fill='#f2a900')

    draw.text((50, 540), "Projected Date to Full Coverage:", font=font_bold, fill='black')
    draw.text((60, 590), projected_date, font=font_bold, fill='#f2a900')

    draw.text((50, 860), "@UTXOmgmt", font=font_italic, fill='black')

    draw.text((50, 920), "utxo.management", font=font_bold, fill='black')
    

    # Overlay the logo if available
    try:
        logo = Image.open("assets/utxologo.webp").convert("RGBA")
        logo.thumbnail((150, 150))  # Resize logo to fit top-right
        img.paste(logo, (img.width - logo.width - 30, 30), logo)  # Top-right with transparency
    except:
        st.warning("Failed to overlay UTXO logo. Check file path and format.")
    
    # Overlay ticker-specific logo in bottom-right
    logo_filename = ticker_logos.get(ticker.lower())
    if logo_filename:
        try:
            logo_path = f"assets/{logo_filename}"
            logo = Image.open(logo_path).convert("RGBA")
            logo.thumbnail((120, 120))
            img.paste(logo, (img.width - logo.width - 30, img.height - logo.height - 30), logo)
        except Exception as e:
            st.warning(f"Error loading company logo: {e}")


    # Convert to bytes for Streamlit
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()

    st.image(img, caption="Tweetable Treasury Graphic")
    st.download_button("Download Image", data=byte_im, file_name=f"{ticker}_stat_card.png", mime="image/png")