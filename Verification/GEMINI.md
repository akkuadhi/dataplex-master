# Data Verification Workflow

This folder is dedicated to verifying and correcting data files (CSV/Excel) based on defined rule sets.

## The Data Verifier Agent

We have a specialized sub-agent for this task: `@data-verifier`.

### **Capabilities:**
- Reads column rules from CSV or Excel files.
- Checks target data files for header mismatches (Case, Spaces, Missing columns).
- Automatically corrects headers in the target file (CSV or Excel) without requiring you to run external scripts.

### **How to Use:**
To start a verification task, simply invoke the agent in your chat:

```text
@data-verifier
```

Then follow the prompts to provide:
1. The path to your **Rules File**.
2. The path to your **Target File**.

### **Verification Standards:**
- **Case Sensitivity:** `ColumnName` != `columnname`.
- **Space Matching:** `Column Name` != `ColumnName`.
- **Integrity:** The agent only modifies the header row (or specific column names) and preserves all underlying data.
