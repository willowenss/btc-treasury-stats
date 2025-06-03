import math
from tabulate import tabulate

BTC_PRICE = 109_000  # Hardcoded BTC price

def get_float_input(prompt, optional=False):
    while True:
        user_input = input(prompt)
        if optional and user_input.strip() == '':
            return None
        try:
            return float(user_input.replace(',', '').replace('%', ''))
        except ValueError:
            print("Please enter a valid number.")

def bold(text):
    return f"\033[1m{text}\033[0m"

def btc_treasury_model():
    print("=== BTC Treasury Company Analysis ===")

    # Inputs
    name = input("Company Name: ")
    ticker = input("Ticker: ")
    shares_outstanding = get_float_input("Shares: ")
    share_price = get_float_input("Share Price (in USD): ")
    btc_nav = get_float_input("BTC NAV (in USD): ")
    fiat_debt = get_float_input("Fiat Debt (in USD): ")
    btc_yield_ytd = get_float_input("BTC Yield YTD %: ")
    months_since_start = get_float_input("YTD Months: ")
    current_mnav = get_float_input("Current mNAV: ")
    projected_yield = get_float_input("Projected BTC Yield % (optional): ", optional=True)
    risk_score = get_float_input("Risk Score (1 = neutral, >1 = riskier, <1 = safer, optional): ", optional=True)

    # Handle optional values
    if projected_yield is None:
        projected_yield = btc_yield_ytd
    if risk_score is None:
        risk_score = 1.0

    # Derived calculations
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
    fiat_debt_pct = (fiat_debt / btc_nav) * 100 if btc_nav > 0 else 0
    enterprise_value = market_cap + fiat_debt

    # Output using tabulate
    print(f"\n--- Results for {name} ({ticker}) ---\n")
    table = [
        ["Market Cap", f"${market_cap:,.0f}"],
        ["Enterprise Value", f"${enterprise_value:,.0f}"],
        ["BTC NAV", f"${btc_nav:,.0f}"],
        ["Fiat Debt", f"${fiat_debt:,.0f} ({fiat_debt_pct:.1f}%)"],
        ["BTC Yield YTD", f"{btc_yield_ytd:.2f}%"],
        ["Projected BTC Yield", f"{projected_yield:.2f}%"],
        ["BTC Yield Multiple", f"{btc_yield_multiple:.2f}"],
        ["BTC Yield 1Y Annualized", f"{btc_yield_1y:.2f}"],
        ["Current mNAV", f"{current_mnav:.2f}"],
        ["Days to Cover mNAV", f"{days_to_cover:.0f} days"],
        ["Months to Cover mNAV", f"{months_to_cover:.2f}"],
        [bold("Risk-Adjusted Days to Cover"), bold(f"{risk_adjusted_days:.0f} days")],
        [bold("Risk-Adjusted Months to Cover"), bold(f"{risk_adjusted_months:.2f}")]
    ]

    print(tabulate(table, headers=["Metric", "Value"], tablefmt="fancy_grid"))

if __name__ == "__main__":
    btc_treasury_model()