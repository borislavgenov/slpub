import streamlit as st

st.set_page_config(page_title="🧾 Recommended Retail Price", layout="wide", initial_sidebar_state="collapsed")

st.title("🧾 Final Retail Price (Based on Fixed Markups)")
st.markdown("Enter your partner (wholesale) price without VAT to calculate all fixed markups and the final recommended retail price with VAT.")

st.divider()

base_price = st.number_input("Partner price (excl. VAT):", min_value=0.01, value=10.0, step=0.5, format="%.2f")

if base_price:
    components = [
        ("Wholesale markup", 0.02),
        ("Stock handling (intake, shelving, storage)", 0.02),
        ("Shrinkage reserve", 0.03),
        ("Operating costs (salaries etc.)", 0.04),
        ("Pharmacy/store profit", 0.10),
    ]

    st.subheader("📊 Markup Components:")
    subtotal = base_price
    for label, percent in components:
        value = base_price * percent
        subtotal += value
        markup = subtotal - base_price
        st.markdown(f"- **{label} ({percent*100:.0f}%):** `{value:.2f} BGN`")
    st.markdown(f"**Total markup:** `{markup:.2f} BGN`")
    st.markdown(f"**Total before VAT:** `{subtotal:.2f} BGN`")

    final_price = subtotal * 1.2
    st.markdown(f"### 💰 Final retail price with VAT: `{final_price:.2f} BGN`")

st.divider()
st.info("💡 All markups are fixed according to internal policy: 21% total markup + 20% VAT.")
