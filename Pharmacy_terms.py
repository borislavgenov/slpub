import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime


st.set_page_config(page_title="Pharmacy Terms", layout="wide", initial_sidebar_state="collapsed")
st.title("📋 Monthly Pharmacy Terms")

conn = sqlite3.connect("pharmacy.db")
cursor = conn.cursor()

cursor.execute("SELECT name FROM pharmacies ORDER BY name")
pharmacy_list = [row[0] for row in cursor.fetchall()]


st.subheader("Enter Terms for This Month")

pharmacy = st.selectbox("Pharmacy", pharmacy_list)
from datetime import datetime
from dateutil.relativedelta import relativedelta


def generate_past_months(start="2023-01"):
    start_date = datetime.strptime(start, "%Y-%m")
    current_date = datetime.today()
    months = []
    while current_date >= start_date:
        months.append(current_date.strftime("%Y-%m"))
        current_date -= relativedelta(months=1)
    return months


month_options = generate_past_months()


month = st.selectbox("Month", month_options, index=0)



existing = cursor.execute("""
    SELECT * FROM pharmacy_terms WHERE pharmacy_name = ? AND month = ?
""", (pharmacy, month)).fetchone()

sell_in_discount = st.number_input("Sell-In Discount (%)", min_value=0.0, step=0.1, value=existing[3] if existing else 0.0)
sell_out_pct = st.number_input("Sell-Out Incentive (%)", min_value=0.0, step=0.1, value=existing[4] if existing else 0.0)
sell_out_bgn = st.number_input("Sell-Out Incentive (BGN)", min_value=0.0, step=0.01, value=existing[5] if existing else 0.0)
marketing_spend = st.number_input("Monthly Marketing Spend (BGN)", min_value=0.0, step=1.0, value=existing[6] if existing else 0.0)
notes = st.text_area("Notes", value=existing[7] if existing else "")

if st.button("💾 Save Terms"):
    if existing:
        cursor.execute("""
            UPDATE pharmacy_terms
            SET sell_in_discount_pct = ?, sell_out_fee_pct = ?, sell_out_fee_bgn = ?, marketing_spend_bgn = ?, notes = ?
            WHERE pharmacy_name = ? AND month = ?
        """, (
            sell_in_discount, sell_out_pct, sell_out_bgn, marketing_spend, notes, pharmacy, month
        ))
        st.success("✅ Terms updated successfully.")
    else:
        cursor.execute("""
            INSERT INTO pharmacy_terms (
                pharmacy_name, month, sell_in_discount_pct,
                sell_out_fee_pct, sell_out_fee_bgn, marketing_spend_bgn, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            pharmacy, month, sell_in_discount,
            sell_out_pct, sell_out_bgn, marketing_spend, notes
        ))
        st.success("✅ Terms saved successfully.")
    conn.commit()


st.markdown("---")
st.subheader("📅 View All Saved Terms")

records = cursor.execute("""
    SELECT pharmacy_name, month, sell_in_discount_pct,
           sell_out_fee_pct, sell_out_fee_bgn, marketing_spend_bgn, notes
    FROM pharmacy_terms
    ORDER BY month DESC, pharmacy_name
""").fetchall()




header_cols = st.columns([2, 2, 1.5, 1.5, 1.5, 1.5, 2, 1])
headers = ["Pharmacy", "Month", "Sell-In (%)", "Sell-Out (%)", "Sell-Out (BGN)", "Marketing Spend", "Notes", ""]
for col, header in zip(header_cols, headers):
    col.markdown(f"**{header}**")


records = cursor.execute("""
    SELECT rowid, pharmacy_name, month, sell_in_discount_pct,
           sell_out_fee_pct, sell_out_fee_bgn, marketing_spend_bgn, notes
    FROM pharmacy_terms
    ORDER BY month DESC, pharmacy_name
""").fetchall()

for record in records:
    rowid, pharmacy, month, sell_in, sell_out_pct, sell_out_bgn, marketing, notes = record
    cols = st.columns([2, 2, 1.5, 1.5, 1.5, 1.5, 2, 1])
    cols[0].markdown(pharmacy)
    cols[1].markdown(month)
    cols[2].markdown(f"{sell_in:.2f}")
    cols[3].markdown(f"{sell_out_pct:.2f}")
    cols[4].markdown(f"{sell_out_bgn:.2f}")
    cols[5].markdown(f"{marketing:.2f}")
    cols[6].markdown(notes)

    with cols[7]:
        with st.form(key=f"delete_form_{rowid}", clear_on_submit=True):
            delete_btn = st.form_submit_button("🗑️")
            if delete_btn:
                cursor.execute("DELETE FROM pharmacy_terms WHERE rowid = ?", (rowid,))
                conn.commit()
                st.warning(f"❌ Deleted terms for {pharmacy} ({month})")
                st.rerun()


st.markdown("💡 **Tip:** If you want to add, edit, or delete pharmacies, go to the *Marketing Activities* page.")


conn.close()
