import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="🧾 Invoice Tracking", layout="wide", initial_sidebar_state="collapsed")
st.title("🧾 Monthly Invoice Tracking")

conn = sqlite3.connect("invoice_tracking.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS counterparties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
)
""")
conn.commit()

def get_month_options(start="2023-01"):
    start_date = datetime.strptime(start, "%Y-%m")
    current = datetime.today()
    return [
        (current - relativedelta(months=i)).strftime("%Y-%m")
        for i in range((current.year - start_date.year) * 12 + current.month - start_date.month + 1)
    ]

months = get_month_options()
selected_month = st.selectbox("Select Month", months)

companies = [row[0] for row in cursor.execute("SELECT name FROM counterparties ORDER BY name").fetchall()]


df = pd.read_sql_query("SELECT * FROM invoices WHERE month = ? ORDER BY invoice_date", conn, params=(selected_month,))
invoice_map = {f"{row['invoice_number']} ({row['company']})": row["id"] for _, row in df.iterrows()}
invoice_labels = list(invoice_map.keys())

selected_label = st.selectbox("🧾 Select an Invoice to Edit", ["➕ Add New Invoice"] + invoice_labels)
editing_mode = selected_label != "➕ Add New Invoice"
current_id = invoice_map[selected_label] if editing_mode else None
row = df[df["id"] == current_id].iloc[0] if editing_mode else {}

st.markdown("### ✏️ Invoice Form")

with st.form("invoice_form"):
    invoice_number = st.text_input("Invoice Number", value=row.get("invoice_number", "") if editing_mode else "")
    invoice_date = st.date_input("Invoice Date", value=datetime.strptime(row["invoice_date"], "%Y-%m-%d") if editing_mode else datetime.today())
    received_date = st.date_input("Date Received", value=datetime.strptime(row["received_date"], "%Y-%m-%d") if editing_mode else datetime.today())

    selected_company = st.selectbox("Company", companies, index=companies.index(row["company"]) if editing_mode and row["company"] in companies else 0) if companies else ""
    
    amount = st.number_input("Amount (BGN)", min_value=0.0, step=0.01, value=row.get("amount", 0.0) if editing_mode else 0.0)
    due_date = st.date_input("Due Date", value=datetime.strptime(row["due_date"], "%Y-%m-%d") if editing_mode else datetime.today())
    status = st.selectbox("Status", ["Unpaid", "Paid", "Partially Paid"], index=["Unpaid", "Paid", "Partially Paid"].index(row["status"]) if editing_mode else 0)
    paid_date = st.date_input("Date Paid", value=datetime.strptime(row["paid_date"], "%Y-%m-%d") if editing_mode and row["paid_date"] else datetime.today() if status == "Paid" else datetime.today())

    col1, col2 = st.columns([3, 1])
    with col1:
        submitted = st.form_submit_button("🔄 Update Invoice" if editing_mode else "💾 Save Invoice")
    with col2:
        delete_confirmed = st.checkbox("Confirm Delete")
        delete_clicked = st.form_submit_button("🗑 Delete")

    if submitted:
        invoice_month = invoice_date.strftime("%Y-%m")
        if invoice_month != selected_month:
            st.error("❌ Invoice date must be within the selected month.")
        elif status == "Paid" and not paid_date:
            st.error("❌ Paid status requires a payment date.")
        else:
            paid_val = paid_date.strftime("%Y-%m-%d") if paid_date else None
            if editing_mode:
                cursor.execute("""
                    UPDATE invoices SET
                        invoice_number = ?, invoice_date = ?, received_date = ?, company = ?,
                        amount = ?, due_date = ?, paid_date = ?, status = ?
                    WHERE id = ?
                """, (
                    invoice_number, invoice_date.strftime("%Y-%m-%d"), received_date.strftime("%Y-%m-%d"),
                    selected_company, amount, due_date.strftime("%Y-%m-%d"), paid_val, status, current_id
                ))
                conn.commit()
                st.success("✅ Invoice updated successfully.")
            else:
                cursor.execute("""
                    INSERT INTO invoices (
                        month, invoice_number, invoice_date, received_date,
                        company, amount, due_date, paid_date, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    selected_month, invoice_number, invoice_date.strftime("%Y-%m-%d"),
                    received_date.strftime("%Y-%m-%d"), selected_company, amount,
                    due_date.strftime("%Y-%m-%d"), paid_val, status
                ))
                conn.commit()
                st.success("✅ Invoice saved successfully.")
            st.rerun()

    if editing_mode and delete_clicked:
        if delete_confirmed:
            cursor.execute("DELETE FROM invoices WHERE id = ?", (current_id,))
            conn.commit()
            st.success("🗑 Invoice deleted.")
            st.rerun()
        else:
            st.warning("☑️ Please confirm deletion before proceeding.")

with st.expander("➕ Add a new company"):
    new_company_name = st.text_input("New company name")
    if st.button("Add Company"):
        if new_company_name:
            cursor.execute("INSERT OR IGNORE INTO counterparties (name) VALUES (?)", (new_company_name,))
            conn.commit()
            st.success(f"✅ '{new_company_name}' added.")
            st.rerun()
        else:
            st.warning("Please enter a company name.")

st.markdown("---")
st.markdown(f"### 📋 Invoices for {selected_month}")


def highlight_status(val):
    color = ""
    if val == "Unpaid":
        color = "#ff0000"
    elif val == "Paid":
        color = "#00ff00"
    elif val == "Partially Paid":
        color = "#bdbd00"
    return f"background-color: {color}"

if not df.empty:
    df = pd.read_sql_query("SELECT * FROM invoices WHERE month = ? ORDER BY invoice_date", conn, params=(selected_month,))
    styled_df = df.style.applymap(highlight_status, subset=["status"])
    st.dataframe(styled_df, use_container_width=True)
else:
    st.info("No invoices found for this month.")


st.markdown("### 📤 Export")
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("📥 Download CSV", csv, file_name=f"invoices_{selected_month}.csv", mime="text/csv")

conn.close()

import streamlit as st
import sqlite3
from datetime import datetime


conn = sqlite3.connect("invoice_tracking.db", check_same_thread=False)
cursor = conn.cursor()

st.markdown("---")
st.markdown("### 🛠 Manage Companies")


companies = [row[0] for row in cursor.execute("SELECT name FROM counterparties ORDER BY name").fetchall()]
if not companies:
    st.info("No companies found.")
    conn.close()
    st.stop()

selected_company = st.selectbox("Select a company to edit or delete", companies)

tab1, tab2 = st.columns(2)


with tab1:
    st.subheader("✏️ Rename Company")
    new_name = st.text_input("New name", value=selected_company)
    if st.button("Rename"):
        if new_name and new_name != selected_company:
            cursor.execute("UPDATE counterparties SET name = ? WHERE name = ?", (new_name, selected_company))
            cursor.execute("UPDATE invoices SET company = ? WHERE company = ?", (new_name, selected_company))
            conn.commit()
            st.success(f"✅ '{selected_company}' renamed to '{new_name}'. Please refresh the page to update list.")
        else:
            st.warning("Enter a different name to update.")


with tab2:
    st.subheader("🗑 Delete Company")
    invoice_count = cursor.execute("SELECT COUNT(*) FROM invoices WHERE company = ?", (selected_company,)).fetchone()[0]
    st.info(f"This company is linked to {invoice_count} invoice(s).")

    with st.form("delete_form", clear_on_submit=True):
        confirm_delete = st.checkbox("I understand and want to delete this company.")
        delete_clicked = st.form_submit_button("Delete Company")

        if delete_clicked:
            if confirm_delete:
                cursor.execute("DELETE FROM counterparties WHERE name = ?", (selected_company,))
                conn.commit()
                st.success(f"🗑 '{selected_company}' deleted from company list.")
            else:
                st.warning("Please confirm deletion before proceeding.")

conn.close()
