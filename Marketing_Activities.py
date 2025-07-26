import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd
import crud_marketing as crud_mkt
import crud_activities as crud_act
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="Marketing Activities", layout="wide", initial_sidebar_state="collapsed")
st.title("📢 Marketing Activities by Month & Pharmacy")

templates = crud_act.get_all_activity_templates()

with sqlite3.connect("pharmacy.db") as conn:
    cursor = conn.cursor()
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS activity_templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        notes TEXT
    );

    CREATE TABLE IF NOT EXISTS assigned_activities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pharmacy_id INTEGER NOT NULL,
        month TEXT NOT NULL,
        activity_id INTEGER NOT NULL,
        FOREIGN KEY (pharmacy_id) REFERENCES pharmacies(id),
        FOREIGN KEY (activity_id) REFERENCES activity_templates(id)
    );

    CREATE TABLE IF NOT EXISTS activity_attached_products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        activity_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        FOREIGN KEY (activity_id) REFERENCES assigned_activities(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    );
    """)


def get_month_options(start="2023-01"):
    start_date = datetime.strptime(start, "%Y-%m")
    current = datetime.today()
    return [
        (current - relativedelta(months=i)).strftime("%Y-%m")
        for i in range((current.year - start_date.year) * 12 + current.month - start_date.month + 1)
    ]

months = get_month_options()


current_month = datetime.now().strftime("%Y-%m")
selected_month = st.selectbox("📅 Select Month (YYYY-MM):", months)

pharmacies = crud_mkt.get_all_pharmacies()
pharmacy_map = {p["name"]: p["id"] for p in pharmacies}
selected_pharmacy_name = st.selectbox("🏪 Select Pharmacy:", list(pharmacy_map.keys()))
selected_pharmacy_id = pharmacy_map[selected_pharmacy_name]

st.divider()
st.subheader("📋 Assign Activities")
activity_names = [a["name"] for a in templates]
assigned_ids = crud_act.get_assigned_activity_ids(selected_pharmacy_id, selected_month)
selected_activities = st.multiselect("Select activities for this month & pharmacy:",
                                     activity_names,
                                     default=[a["name"] for a in templates if a["id"] in assigned_ids])

if st.button("💾 Save Assigned Activities"):
    selected_ids = [a["id"] for a in templates if a["name"] in selected_activities]
    with sqlite3.connect("pharmacy.db") as conn:
        cursor = conn.cursor()
        for activity_id in selected_ids:
            cursor.execute("SELECT COUNT(*) FROM assigned_activities WHERE pharmacy_id = ? AND month = ? AND activity_id = ?",
                           (selected_pharmacy_id, selected_month, activity_id))
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO assigned_activities (pharmacy_id, month, activity_id) VALUES (?, ?, ?)",
                               (selected_pharmacy_id, selected_month, activity_id))
        conn.commit()
    st.success("Activities added.")
    st.rerun()

st.divider()
st.subheader("📦 Attach Products to Assigned Activities")
with sqlite3.connect("pharmacy.db") as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT aa.id, at.name FROM assigned_activities aa JOIN activity_templates at ON aa.activity_id = at.id WHERE aa.pharmacy_id = ? AND aa.month = ?", (selected_pharmacy_id, selected_month))
    assignments = cursor.fetchall()
    cursor.execute("SELECT id, name FROM products ORDER BY name")
    product_map = {pid: name for pid, name in cursor.fetchall()}

for assignment_id, activity_name in assignments:
    st.markdown(f"**🧩 {activity_name}**")
    with sqlite3.connect("pharmacy.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT product_id FROM activity_attached_products WHERE activity_id = ?", (assignment_id,))
        current_ids = [row[0] for row in cursor.fetchall()]
    selected_names = [product_map[pid] for pid in current_ids if pid in product_map]

    selected = st.multiselect(f"Attach products to '{activity_name}'", options=list(product_map.values()),
                              default=selected_names, key=f"p_{assignment_id}")

    if st.button(f"💾 Save Products for {activity_name}", key=f"s_{assignment_id}"):
        with sqlite3.connect("pharmacy.db") as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM activity_attached_products WHERE activity_id = ?", (assignment_id,))
            for pid, name in product_map.items():
                if name in selected:
                    cursor.execute("INSERT INTO activity_attached_products (activity_id, product_id) VALUES (?, ?)", (assignment_id, pid))
            conn.commit()
        st.success("Products saved.")
        st.rerun()

st.divider()
st.subheader("📊 Activity Overview")

with st.expander("🔍 Filters", expanded=False):
    with sqlite3.connect("pharmacy.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT month FROM assigned_activities ORDER BY month DESC")
        months = [row[0] for row in cursor.fetchall()]

    pharmacy_names = [p["name"] for p in pharmacies]
    activity_names = [a["name"] for a in templates]
    product_names = list(product_map.values())

    f_month = st.selectbox("Month", months)
    f_pharmacy = st.selectbox("Pharmacy", ["All"] + pharmacy_names)
    f_activity = st.selectbox("Activity", ["All"] + activity_names)
    f_product = st.selectbox("Product", ["All"] + product_names)

query = """
SELECT 
    aa.id,
    aa.month,
    p.name AS pharmacy,
    at.name AS activity,
    GROUP_CONCAT(pr.name, ', ') AS products
FROM assigned_activities aa
JOIN pharmacies p ON aa.pharmacy_id = p.id
JOIN activity_templates at ON aa.activity_id = at.id
LEFT JOIN activity_attached_products ap ON aa.id = ap.activity_id
LEFT JOIN products pr ON ap.product_id = pr.id
WHERE aa.month = ?
GROUP BY aa.id
"""
with sqlite3.connect("pharmacy.db") as conn:
    df = pd.read_sql_query(query, conn, params=[f_month])

if f_pharmacy != "All":
    df = df[df["pharmacy"] == f_pharmacy]
if f_activity != "All":
    df = df[df["activity"] == f_activity]
if f_product != "All":
    df = df[df["products"].str.contains(f_product, na=False)]

if not df.empty:
    st.dataframe(df, use_container_width=True)

    with st.expander("⚙️ Manage Assigned Activities", expanded=False):
        for _, row in df.iterrows():
            aid = row["id"]
            existing = [p for p in product_map.values() if p in (row["products"] or "")]
            selected = st.multiselect(
                f"Edit attached products for {row['activity']} ({row['pharmacy']})",
                options=list(product_map.values()),
                default=existing, key=f"edit_{aid}")
            col1, col2 = st.columns(2)
            if col1.button("💾 Save", key=f"u_{aid}"):
                with sqlite3.connect("pharmacy.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM activity_attached_products WHERE activity_id = ?", (aid,))
                    for pid, name in product_map.items():
                        if name in selected:
                            cursor.execute("INSERT INTO activity_attached_products (activity_id, product_id) VALUES (?, ?)", (aid, pid))
                    conn.commit()
                st.success("Updated.")
                st.rerun()
            if col2.button("🗑️ Delete", key=f"d_{aid}"):
                with sqlite3.connect("pharmacy.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM activity_attached_products WHERE activity_id = ?", (aid,))
                    cursor.execute("DELETE FROM assigned_activities WHERE id = ?", (aid,))
                    conn.commit()
                st.warning("Deleted.")
                st.rerun()
else:
    st.info("No data found.")
    
#pharmacy management
st.divider()
with st.expander("🏪 Manage Pharmacies", expanded=False):
    pharmacies = crud_mkt.get_all_pharmacies()
    if pharmacies:
        pharmacy_names = [p["name"] for p in pharmacies]
        selected = st.selectbox("Select pharmacy to edit or delete", pharmacy_names)
        selected_id = next(p["id"] for p in pharmacies if p["name"] == selected)

        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            new_name = st.text_input("Rename to:", value=selected, key="rename_input")
        with col2:
            if st.button("💾 Save"):
                if new_name.strip() and new_name.strip() != selected:
                    crud_mkt.rename_pharmacy(selected_id, new_name.strip())
                    st.success("Pharmacy renamed.")
                    st.rerun()
        with col3:
            if st.button("🗑️ Delete"):
                confirm = st.text_input("Type DELETE to confirm", key="confirm_delete")
                if confirm == "DELETE":
                    crud_mkt.delete_pharmacy(selected_id)
                    st.warning("Pharmacy deleted.")
                    st.rerun()

    st.markdown("### ➕ Add New Pharmacy")
    with st.form("add_pharmacy_form"):
        new_ph_name = st.text_input("New Pharmacy Name:")
        add_submit = st.form_submit_button("💾 Add Pharmacy")
        if add_submit:
            if new_ph_name.strip():
                crud_mkt.create_pharmacy(new_ph_name.strip())
                st.success("Pharmacy added.")
                st.rerun()

st.divider()
with st.expander("⚙️ Manage Activity Templates", expanded=False):
    templates = crud_act.get_all_activity_templates()
    template_map = {a["name"]: a["id"] for a in templates}

    with st.form("add_template"):
        name = st.text_input("Activity Name")
        notes = st.text_area("Notes")
        if st.form_submit_button("➕ Add Activity") and name.strip():
            crud_act.create_activity_template(name.strip(), notes.strip())
            st.success("Activity added.")
            st.rerun()

    if templates:
        selected_template = st.selectbox("Edit Activity", list(template_map.keys()))
        activity = next(a for a in templates if a["name"] == selected_template)
        new_name = st.text_input("Rename", value=activity["name"])
        new_notes = st.text_area("Edit Notes", value=activity["notes"])
        col1, col2 = st.columns([1, 1])
        if col1.button("💾 Save Changes"):
            crud_act.update_activity_template(activity["id"], new_name, new_notes)
            st.success("Updated.")
            st.rerun()
        if col2.button("🗑️ Delete Activity"):
            if st.text_input("Type DELETE to confirm") == "DELETE":
                crud_act.delete_activity_template(activity["id"])
                st.warning("Deleted.")
                st.rerun()