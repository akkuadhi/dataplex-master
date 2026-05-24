## **Phase 0: Rule Building**
You can create your rules file using either a web-based UI or a standalone terminal-based CLI.

### **Option A: Streamlit UI (Web Interface)**
Provides a dynamic, visual interface with live schema fetching.
```powershell
streamlit run rule_builder_ui.py
```

### **Option B: Standalone CLI (Terminal Interface)**
Provides a purely interactive terminal experience, ideal for users without a browser or Streamlit.
```powershell
python rule_builder_cli.py
```

## **Phase 3: Dataplex Rule Creator Agent (@rule-creator)**

## **How it Works**
1. **Logic Translation**: 
   - Reads your "Rule_Logic" (Natural Language descriptions).
   - Translates them into BigQuery SQL assertions or Dataplex spec expectations.
2. **Configuration Sorting**:
   - Maps parameters to the correct file type.
   - **YAML**: Notifications, thresholds, and DQ rules.
   - **Batch**: Incremental columns, schedules, and CLI flags.
3. **Multi-Source Support**: Automatically handles comparisons between `Source_Table` and `Historic_Table` using SQL joins/subqueries.

## **Verification Checkpoints**
- **SQL Review**: **MANDATORY.** The agent will present every generated SQL statement and mapping logic to you in the chat.
- **Final Confirmation**: You must review the technical translation and say "Confirm" before the `.yaml` and `.bat` files are written to the `generated_configs/` directory.

## **How to Invoke**
In your CLI chat, simply type:
```text
@rule-creator
```
Provide the path to your **Verified Rules File** (from Phase 2) when prompted.
