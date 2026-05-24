# Dataplex Rule Creation Workflow

This folder is used for generating the configuration files (YAML and Batch) required to set up Dataplex DataScans in Google Cloud.

## The Rule Creator Agent

We have a specialized sub-agent for this task: `@rule-creator`.

### **Capabilities:**
- Reads your **Verified Rules File** (CSV/Excel).
- Generates **YAML files** for each table containing:
    - Data Quality rules.
    - **Notification Email** (as per project requirements).
- Generates **Batch files** (`.bat`) containing `gcloud` commands with:
    - **Incremental Column** details passed as command-line parameters.

### **How to Use:**
1. Ensure your rules file has been verified (you can use `@data-verifier` for this).
2. Invoke the agent in the chat:
   ```text
   @rule-creator
   ```
3. Provide the path to your rules file when prompted.
4. The agent will generate a `generated_configs` folder with all the output files.

### **Field Mapping Standards:**
- **YAML Files:** Reserved for static metadata and rule definitions (includes email notifications).
- **Batch Files:** Reserved for execution parameters and environment-specific flags (includes incremental column logic).
