# Phase 2: Data Verification Agent (`@data-verifier`)

This agent is responsible for cleaning and validating your Rules File against your actual target data files (CSV/Excel).

## **How it Works**
1. **Rule Parsing**: Reads your business rules from your CSV/Excel rules file.
2. **Data Inspection**: Reads the headers of your target data files.
3. **Mismatched Identification**: 
   - Checks for **Case Sensitivity** (e.g., `UserID` vs `userid`).
   - Checks for **Exact Spacing** (e.g., `User ID` vs `UserID`).
   - Identifies columns defined in rules that are missing in the data.

## **Verification Checkpoints**
- **Mismatch Report**: Before making any changes, the agent provides a detailed list of every discrepancy found.
- **Correction Approval**: **Crucial Step.** The agent will propose a specific correction (e.g., "Rename 'User ID' to 'user_id'"). It will NOT modify the file until you provide explicit confirmation.

## **How to Invoke**
In your CLI chat, simply type:
```text
@data-verifier
```
The agent will then prompt you for the paths to your Rules File and Target File.
