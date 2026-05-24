"""
Interactive Dataplex Rule Builder UI.

Built with Streamlit to provide a visual interface for creating data quality rules.
Fetches real-time BigQuery schemas and exports rules to a structured CSV format.
"""

import os
import json
import streamlit as st
import pandas as pd
from google.cloud import bigquery

# --- Page Config ---
st.set_page_config(page_title="Dataplex Rule Builder", layout="wide", page_icon="🛠️")

# --- Technical Constraints: Proxy Setup ---
def setup_proxy():
    """Configures system proxies within the Streamlit session state."""
    if 'proxy_setup_done' not in st.session_state:
        st.session_state.proxy_setup_done = False

    if not st.session_state.proxy_setup_done:
        with st.sidebar.expander("🌐 Proxy Settings", expanded=True):
            proxy_url = st.text_input("Proxy URL (e.g., proxy.co.com:8080)", "").strip()
            use_creds = st.checkbox("Use Proxy Credentials?")
            if use_creds:
                user = st.text_input("Username")
                password = st.text_input("Password", type="password")
                if st.button("Apply Proxy"):
                    proxy = f"http://{user}:{password}@{proxy_url}"
                    os.environ['HTTP_PROXY'] = proxy
                    os.environ['HTTPS_PROXY'] = proxy
                    st.session_state.proxy_setup_done = True
                    st.success("Proxy Applied")
            elif proxy_url:
                if st.button("Apply Proxy"):
                    proxy = f"http://{proxy_url}"
                    os.environ['HTTP_PROXY'] = proxy
                    os.environ['HTTPS_PROXY'] = proxy
                    st.session_state.proxy_setup_done = True
                    st.success("Proxy Applied")
            else:
                if st.button("Skip Proxy"):
                    st.session_state.proxy_setup_done = True
                    st.info("No proxy set.")

# --- BigQuery Helper ---
@st.cache_resource
def get_bq_client():
    """Initializes and caches the BigQuery client."""
    return bigquery.Client()

def get_projects(client):
    """Lists all accessible project IDs."""
    return [p.project_id for p in client.list_projects()]

def get_datasets(client, project):
    """Lists all datasets within a specific project."""
    return [d.dataset_id for d in client.list_datasets(project=project)]

def get_tables(client, project, dataset):
    """Lists all tables within a specific dataset."""
    return [t.table_id for t in client.list_tables(f"{project}.{dataset}")]

def get_columns(client, project, dataset, table):
    """Extracts column names from a BigQuery table schema."""
    table_ref = f"{project}.{dataset}.{table}"
    table_obj = client.get_table(table_ref)
    return [f.name for f in table_obj.schema]

# --- Main App ---
def main():
    """Main Streamlit application logic."""
    st.title("🛠️ Dataplex Rule Builder")
    st.markdown("Build your verified rules file interactively by fetching schemas directly from BigQuery.")

    setup_proxy()
    if not st.session_state.get('proxy_setup_done'):
        st.warning("Please complete Proxy Settings in the sidebar to continue.")
        return

    try:
        client = get_bq_client()
    except Exception as error: # pylint: disable=broad-except
        st.error(f"Failed to initialize BigQuery Client: {error}")
        return

    if 'rules_list' not in st.session_state:
        st.session_state.rules_list = []

    # --- Step 1: Resource Selection ---
    st.header("1. Identify Data Sources")
    col_src, col_hist = st.columns(2)

    with col_src:
        st.subheader("🔹 Source Data")
        src_project = st.selectbox("Source Project", get_projects(client), key="src_p")
        src_dataset = st.selectbox("Source Dataset", get_datasets(client, src_project), key="src_d")
        src_table = st.selectbox("Source Table", get_tables(client, src_project, src_dataset), key="src_t")
        src_cols = get_columns(client, src_project, src_dataset, src_table)

    with col_hist:
        st.subheader("📜 Historic Data (Optional)")
        hist_project = st.selectbox("Historic Project", ["None"] + get_projects(client), key="hist_p")
        if hist_project != "None":
            hist_dataset = st.selectbox("Historic Dataset", get_datasets(client, hist_project), key="hist_d")
            hist_table = st.selectbox("Historic Table", get_tables(client, hist_project, hist_dataset), key="hist_t")
        else:
            hist_dataset = hist_table = ""

    # --- Step 2: Rule Definition ---
    st.header("2. Define Rule Logic")
    with st.form("rule_form", clear_on_submit=True):
        f_c1, f_c2, f_c3 = st.columns(3)
        with f_c1:
            col_target = st.selectbox("Target Column", ["(Table Level)"] + src_cols)
            dimension = st.selectbox("Dimension", ["COMPLETENESS", "UNIQUENESS", "VALIDITY", "TIMELINESS", "ACCURACY", "VOLUME", "CONSISTENCY"])
            rule_type = st.selectbox("Rule Type", ["NonNull", "Uniqueness", "Range", "Set", "Regex", "SqlAssertion"])
        with f_c2:
            logic = st.text_area("Rule Logic (Plain English)", placeholder="e.g. Total sales should match historic average")
            threshold = st.number_input("Threshold (0.0 - 1.0)", 0.0, 1.0, 1.0, 0.01)
            ignore_null = st.checkbox("Ignore Nulls?")
        with f_c3:
            scan_id = st.text_input("Scan ID", value=f"{src_table}-dq-scan")
            display_name = st.text_input("Display Name", value=f"{src_table.capitalize()} Quality Scan")
            inc_field = st.selectbox("Incremental Field", ["None"] + src_cols)
            email = st.text_input("Notification Email")

        m_c1, m_c2, m_c3 = st.columns(3)
        with m_c1: location = st.text_input("Location", value="us-central1")
        with m_c2: cron = st.text_input("Schedule (Cron)", value="0 0 * * *")
        with m_c3: labels = st.text_input("Labels (k=v)", value="env=prod")

        if st.form_submit_button("➕ Add Rule"):
            st.session_state.rules_list.append({
                "Source_Project": src_project, "Source_Dataset": src_dataset, "Source_Table": src_table,
                "Historic_Project": hist_project if hist_project != "None" else "",
                "Historic_Dataset": hist_dataset, "Historic_Table": hist_table,
                "Location": location, "Scan_ID": scan_id, "Display_Name": display_name,
                "Scan_Description": f"DQ Scan for {src_table}", "Schedule_Cron": cron,
                "Incremental_Field": inc_field if inc_field != "None" else "", "Labels": labels,
                "Sampling_Percent": 100, "Row_Filter": "", "Column_Name": col_target if col_target != "(Table Level)" else "",
                "Dimension": dimension, "Rule_Type": rule_type, "Rule_Logic": logic,
                "Threshold": threshold, "Ignore_Null": str(ignore_null).upper(), "Notification_Email": email
            })
            st.success(f"Added rule for {col_target}")

    # --- Step 3: View & Export ---
    if st.session_state.rules_list:
        st.header("3. Review & Export")
        df_rules = pd.DataFrame(st.session_state.rules_list)
        st.dataframe(df_rules)

        e_c1, e_c2 = st.columns(2)
        with e_c1:
            fname = st.text_input("Filename", value="final_rules.csv")
        with e_c2:
            if st.button("💾 Save to Folder"):
                save_dir = os.path.dirname(os.path.abspath(__file__))
                path = os.path.join(save_dir, fname)
                df_rules.to_csv(path, index=False)
                st.success(f"Saved to {path}")

        st.download_button("📥 Download CSV", df_rules.to_csv(index=False).encode('utf-8'), fname, 'text/csv')
        if st.button("🗑️ Clear All Rules"):
            st.session_state.rules_list = []
            st.rerun()

if __name__ == "__main__":
    main()
