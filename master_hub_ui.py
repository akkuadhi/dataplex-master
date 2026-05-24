"""
Dataplex Master Hub Orchestrator.

A comprehensive Streamlit UI to manage the end-to-end Dataplex scan creation pipeline:
Discovery, Verification, and Generation. Supports structured outputs and full logging.
"""

import os
import json
import subprocess
from datetime import datetime
import streamlit as st
import pandas as pd
import yaml
from google.cloud import bigquery

# --- Page Config ---
st.set_page_config(page_title="Dataplex Master Hub", layout="wide", page_icon="🚀")

# --- Constants & Dir Setup ---
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUTS_BASE = os.path.join(ROOT_DIR, "outputs")
LOGS_DIR = os.path.join(ROOT_DIR, "logs")

for directory in [OUTPUTS_BASE, LOGS_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_table_dir(proj, ds, tbl):
    """Creates and returns a table-specific output directory."""
    path = os.path.join(OUTPUTS_BASE, f"{proj}_{ds}_{tbl}")
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def log_step(phase, table_name, message, details=None):
    """Logs an execution step to a timestamped file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOGS_DIR, f"{timestamp}_{phase}_{table_name}.log")
    with open(log_file, "a", encoding="utf-8") as file:
        file.write(f"[{datetime.now()}] {message}\n")
        if details:
            file.write(f"Details: {json.dumps(details, indent=2)}\n")
    return log_file

# --- Global Style ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    .stStep { font-weight: bold; color: #007bff; }
    </style>
    """, unsafe_allow_html=True)

# --- Shared State ---
if 'proxy_configured' not in st.session_state:
    st.session_state.proxy_configured = False
if 'rules_df' not in st.session_state:
    st.session_state.rules_df = None

# --- Header ---
st.title("🚀 Dataplex Master Hub")
st.markdown("Centralized Orchestrator for Dataplex Scan Creation (Structured & Logged)")

# --- Sidebar: Technical Configuration ---
with st.sidebar:
    st.header("⚙️ System Config")
    with st.expander("🌐 Proxy Settings", expanded=not st.session_state.proxy_configured):
        proxy_url = st.text_input("Proxy Host:Port", placeholder="proxy.company.com:8080")
        if st.checkbox("Custom Proxy Credentials?"):
            p_user = st.text_input("Proxy User")
            p_pass = st.text_input("Proxy Pass", type="password")
            p_string = f"http://{p_user}:{p_pass}@{proxy_url}"
        else:
            p_string = f"http://{proxy_url}"
        
        if st.button("Apply Proxy Settings") and proxy_url:
            os.environ['HTTP_PROXY'] = p_string
            os.environ['HTTPS_PROXY'] = p_string
            st.session_state.proxy_configured = True
            log_step("Setup", "Global", f"Proxy configured: {proxy_url}")
            st.success("Proxy Applied")
    
    st.info("💡 **Tip:** Ensure `gcloud auth application-default login` has been run.")

# --- BigQuery Client ---
@st.cache_resource
def get_bq_client():
    """Initializes BigQuery client."""
    return bigquery.Client()

# --- Main Tabs ---
tabs = st.tabs(["📂 Build Rules", "🔍 Discover Schema", "✅ Verify Columns", "🛠️ Generate Configs"])

# --- Tab 0: Build Rules ---
with tabs[0]:
    st.header("Phase 0: Rule Building")
    st.info("Use the interactive Rule Builder to create your rules CSV.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Launch Web-based Rule Builder"):
            log_step("P0", "Builder", "Launched Streamlit Rule Builder")
            script_path = os.path.join(ROOT_DIR, "Rule creator", "rule_builder_ui.py")
            subprocess.Popen(["streamlit", "run", script_path])
    with col2:
        cli_path = os.path.join(ROOT_DIR, 'Rule creator', 'rule_builder_cli.py')
        st.code(f"python \"{cli_path}\"")

# --- Tab 1: Discover Schema ---
with tabs[1]:
    st.header("Phase 1: BigQuery Schema Discovery")
    if st.button("Refresh Projects"):
        try:
            client = get_bq_client()
            st.session_state.projects = [p.project_id for p in client.list_projects()]
            st.success("Projects Loaded")
        except Exception as error: # pylint: disable=broad-except
            st.error(f"BQ Error: {error}")

    if 'projects' in st.session_state:
        target_p = st.selectbox("Project", st.session_state.projects)
        datasets = [d.dataset_id for d in get_bq_client().list_datasets(project=target_p)]
        target_d = st.selectbox("Dataset", datasets)
        tables = [t.table_id for t in get_bq_client().list_tables(f"{target_p}.{target_d}")]
        target_t = st.selectbox("Table", tables)
        
        if st.button("Fetch & Review Schema"):
            table_ref = f"{target_p}.{target_d}.{target_t}"
            table_obj = get_bq_client().get_table(table_ref)
            schema_data = [{"Name": f.name, "Type": f.field_type, "Mode": f.mode} for f in table_obj.schema]
            
            t_dir = get_table_dir(target_p, target_d, target_t)
            with open(os.path.join(t_dir, "schema_discovered.json"), 'w', encoding="utf-8") as f:
                json.dump(schema_data, f, indent=2)
            
            log_step("P1", target_t, f"Fetched schema from {table_ref}", {"schema": schema_data})
            st.dataframe(pd.DataFrame(schema_data))
            st.success(f"Artifacts saved in {t_dir}")

# --- Tab 2: Verify Columns ---
with tabs[2]:
    st.header("Phase 2: Rules File Verification")
    r_file = st.file_uploader("Upload Rules CSV", type=["csv"])
    d_file = st.file_uploader("Upload Target Data File", type=["csv", "xlsx"])
    
    if r_file and d_file:
        rules_df = pd.read_csv(r_file)
        headers = list(pd.read_csv(d_file, nrows=0).columns) if d_file.name.endswith('.csv') else list(pd.read_excel(d_file, nrows=0).columns)
        
        mismatches = []
        for col in rules_df['Column_Name'].dropna().unique():
            status = "✅ OK" if col in headers else "❌ Missing"
            sugg = next((h for h in headers if h.strip().lower() == col.strip().lower()), "") if status == "❌ Missing" else ""
            mismatches.append({"Rule Column": col, "Status": status, "Suggestion": sugg})
        
        st.table(pd.DataFrame(mismatches))
        if st.button("Save Verification Report"):
            for _, row in rules_df.iterrows():
                t_dir = get_table_dir(row['Source_Project'], row['Source_Dataset'], row['Source_Table'])
                pd.DataFrame(mismatches).to_csv(os.path.join(t_dir, "verification_report.csv"), index=False)
                log_step("P2", row['Source_Table'], "Generated verification report")
            st.success("Reports saved.")
            st.session_state.rules_df = rules_df

# --- Tab 3: Generate Configs ---
with tabs[3]:
    st.header("Phase 3: Config Generation")
    if st.session_state.rules_df is not None:
        df_final = st.session_state.rules_df
        for table_id, group in df_final.groupby(['Source_Project', 'Source_Dataset', 'Source_Table']):
            p, d, t = table_id
            t_dir = get_table_dir(p, d, t)
            st.write(f"### Table: {p}.{d}.{t}")
            
            yaml_content = {
                "description": f"DQ Scan for {t}",
                "labels": {"notification_email": group.iloc[0]['Notification_Email'].replace('@', '_at_')},
                "samplingPercent": float(group.iloc[0]['Sampling_Percent']),
                "rowFilter": group.iloc[0]['Row_Filter'],
                "dataQualitySpec": {"rules": []}
            }
            
            for index, row in group.iterrows():
                st.info(f"🧠 **What I Understood:** I will ensure '{row['Column_Name']}' meets the {row['Rule_Type']} expectation for '{row['Rule_Logic']}'.")
                rule = {"dimension": row['Dimension'], "column": row['Column_Name'], "threshold": float(row['Threshold']), "ignoreNull": row['Ignore_Null'] == "TRUE"}
                if row['Rule_Type'] == "NonNull": rule["nonNullExpectation"] = {}
                elif row['Rule_Type'] == "Uniqueness": rule["uniquenessExpectation"] = {}
                elif row['Rule_Type'] == "SqlAssertion":
                    sql_val = st.text_input(f"Confirm SQL for: {row['Rule_Logic']}", value="SELECT ...", key=f"sql_{table_id}_{index}")
                    # 2026 Standard: sqlAssertionExpectation fails if rows are returned
                    rule["sqlAssertionExpectation"] = {"sqlStatement": sql_val}
                yaml_content["dataQualitySpec"]["rules"].append(rule)

            if st.button(f"Generate & Log for {t}", key=f"gen_btn_{t}"):
                with open(os.path.join(t_dir, "dq_spec.yaml"), 'w', encoding="utf-8") as f: yaml.dump(yaml_content, f)
                # 2026 Standard URI: //bigquery.googleapis.com/projects/...
                cmd = f"gcloud dataplex datascans create data-quality {group.iloc[0]['Scan_ID']} ^\n" \
                      f"    --location={group.iloc[0]['Location']} ^\n" \
                      f"    --data-source-resource=\"//bigquery.googleapis.com/projects/{p}/datasets/{d}/tables/{t}\" ^\n" \
                      f"    --data-quality-spec-file=\"dq_spec.yaml\" ^\n" \
                      f"    --incremental-field=\"{group.iloc[0]['Incremental_Field']}\""
                with open(os.path.join(t_dir, "create_scan.bat"), "w", encoding="utf-8") as f: f.write("@echo off\n" + cmd)
                log_step("P3", t, "Generated Configuration", {"yaml": yaml_content, "batch": cmd})
                st.success(f"Saved to {t_dir}")

if __name__ == "__main__":
    main()
