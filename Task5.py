# unit_converter.py
import streamlit as st
import requests

# ---- Conversion helper functions ----
def usd_to_inr(amount, rate):
    return amount * rate

def inr_to_usd(amount, rate):
    return amount / rate if rate != 0 else 0

def c_to_f(c):
    return c * 9.0 / 5.0 + 32.0

def f_to_c(f):
    return (f - 32.0) * 5.0 / 9.0

def cm_to_inch(cm):
    return cm / 2.54

def inch_to_cm(inch):
    return inch * 2.54

def kg_to_lb(kg):
    return kg * 2.20462262185

def lb_to_kg(lb):
    return lb / 2.20462262185

# ---- Currency rate fetcher (exchangerate.host free API) ----
def fetch_usd_inr_rate():
    """
    Fetches latest USD -> INR rate using exchangerate.host.
    Returns (rate, source_message). On failure returns (None, error_message).
    """
    try:
        # Using exchangerate.host free endpoint
        resp = requests.get("https://api.exchangerate.host/latest", params={"base": "USD", "symbols": "INR"}, timeout=6)
        resp.raise_for_status()
        data = resp.json()
        rate = data.get("rates", {}).get("INR")
        if rate is None:
            return None, "API did not return INR rate."
        return float(rate), f"Live rate from exchangerate.host (base=USD) — fetched successfully."
    except Exception as e:
        return None, f"Could not fetch live rate: {e}"

# ---- Streamlit UI ----
st.set_page_config(page_title="Unit Converter 🔄", page_icon="🔁", layout="centered")

st.title("Unit Converter 🔄")
st.caption("Currency (INR ↔ USD), Temperature (°C ↔ °F), Length (cm ↔ in), Weight (kg ↔ lb) — real-time updates")

# --- Currency section ---
st.header("Currency: INR ↔ USD")

# Attempt to fetch live rate, but allow manual override
rate, msg = fetch_usd_inr_rate()

# sensible default if fetch fails (value observed approx Nov 19, 2025)
DEFAULT_RATE = 88.52  # an observed approximate USD->INR value (used only as fallback/default)

if rate is None:
    st.warning("Live rate fetch failed. Using fallback default rate. (" + msg + ")")
    rate = DEFAULT_RATE
    st.info(f"Fallback default rate used: 1 USD = {rate:.4f} INR")
else:
    st.success(msg)
    st.write(f"1 USD = {rate:.6f} INR (live)")

# Let user override the rate
user_rate = st.number_input("Exchange rate (INR per 1 USD) — edit to override", value=float(rate), format="%.6f")

col1, col2 = st.columns(2)
with col1:
    usd_amount = st.number_input("USD amount", value=1.0, step=0.01, format="%.4f", key="usd")
    usd_to_inr_result = usd_to_inr(usd_amount, user_rate)
    st.write(f"→ INR: ₹{usd_to_inr_result:,.4f}")

with col2:
    inr_amount = st.number_input("INR amount", value=1.0, step=1.0, format="%.4f", key="inr")
    inr_to_usd_result = inr_to_usd(inr_amount, user_rate)
    st.write(f"→ USD: ${inr_to_usd_result:,.4f}")

st.divider()

# --- Temperature section ---
st.header("Temperature: °C ↔ °F")
temp_mode = st.radio("Choose conversion direction", ("Celsius → Fahrenheit", "Fahrenheit → Celsius"), index=0)

if temp_mode == "Celsius → Fahrenheit":
    c_val = st.number_input("°C", value=25.0, step=0.1, format="%.2f", key="c")
    f_val = c_to_f(c_val)
    st.write(f"→ °F: {f_val:.2f} °F")
else:
    f_val = st.number_input("°F", value=77.0, step=0.1, format="%.2f", key="f")
    c_val = f_to_c(f_val)
    st.write(f"→ °C: {c_val:.2f} °C")

st.divider()

# --- Length section ---
st.header("Length: cm ↔ inch")
length_mode = st.radio("Direction", ("cm → inch", "inch → cm"), index=0)

if length_mode == "cm → inch":
    cm_val = st.number_input("cm", value=30.0, step=0.1, format="%.3f", key="cm")
    inch_val = cm_to_inch(cm_val)
    st.write(f"→ inch: {inch_val:.4f} in")
else:
    inch_val = st.number_input("inch", value=12.0, step=0.1, format="%.3f", key="inch")
    cm_val = inch_to_cm(inch_val)
    st.write(f"→ cm: {cm_val:.3f} cm")

st.divider()

# --- Weight section ---
st.header("Weight: kg ↔ lb")
weight_mode = st.radio("Direction", ("kg → lb", "lb → kg"), index=0)

if weight_mode == "kg → lb":
    kg_val = st.number_input("kg", value=70.0, step=0.1, format="%.3f", key="kg")
    lb_val = kg_to_lb(kg_val)
    st.write(f"→ lb: {lb_val:.4f} lb")
else:
    lb_val = st.number_input("lb", value=154.324, step=0.1, format="%.3f", key="lb")
    kg_val = lb_to_kg(lb_val)
    st.write(f"→ kg: {kg_val:.4f} kg")

st.markdown("---")
st.caption("Tip: change any input and the results update immediately. The currency rate is fetched live from exchangerate.host; you may override the rate manually.")
