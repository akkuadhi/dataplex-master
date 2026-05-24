# Dataplex Master Hub 🚀

An end-to-end, user-agnostic ecosystem designed to simplify and automate the creation of Google Cloud Dataplex Data Quality Scans. 

This system guides you from initial data discovery to final production-ready configuration, ensuring every technical step is verified against your business intent.

---

## 🏗️ Project Architecture

The system is organized into a 4-phase pipeline, all managed through a centralized **Master Orchestrator UI**.

1.  **Phase 0: Rule Building** (Interactive UI/CLI for creating rules).
2.  **Phase 1: Discovery** (BigQuery metadata and schema fetching).
3.  **Phase 2: Verification** (Matching rules against actual data headers).
4.  **Phase 3: Generation** (NL-to-SQL translation and config generation).

---

## ✨ Key Features

-   **Interactive Hub**: Run the entire pipeline from a single Streamlit interface (`master_hub_ui.py`).
-   **NL-to-SQL Translation**: Describe your data quality logic in plain English; the agent handles the BigQuery SQL.
-   **Zero-Assumption Policy**: Every agent is hard-coded to explain its interpretation and wait for human confirmation.
-   **User-Agnostic**: Dynamic path resolution ensures portability across any system or user profile.
-   **Structured Outputs**: All artifacts (YAMLs, Batch scripts, Schemas) are organized into table-specific folders.
-   **Full Audit Logging**: Every execution step is recorded in timestamped logs for total traceability.
-   **Corporate Ready**: Integrated support for HTTP/HTTPS proxies with credential handling and CA certificate support.

---

## 🛠️ Getting Started

### **Prerequisites**
-   **Python 3.7+**
-   **GCloud CLI** (authenticated with `gcloud auth application-default login`)
-   **Dependencies**: 
    ```powershell
    pip install streamlit pandas google-cloud-bigquery pyyaml
    ```

### **Running the Hub**
Navigate to the root directory and launch the Master Orchestrator:
```powershell
streamlit run master_hub_ui.py
```

---

## 📁 Directory Structure

-   **`/Schema`**: Tools for BigQuery metadata discovery.
-   **`/Verification`**: Agents for rule-to-data consistency checking.
-   **`/Rule creator`**: The logic translation and config generation engine.
-   **`/outputs`**: (Auto-generated) Structured table-specific artifacts.
-   **`/logs`**: (Auto-generated) Audit logs for every run.

---

## ⚖️ Technical Constraints & Compliance
-   **Authentication**: Uses default `gcloud` credentials.
-   **Environment**: Operates within the default Python environment.
-   **Security**: Adheres to system CA certificates and supports secure proxy configurations.

---

## 📜 Documentation
Each sub-folder contains its own detailed `README.md` and `agent.md` for granular instructions on individual components. Refer to `DATAPLEX_MASTER.md` for a visual workflow diagram.
