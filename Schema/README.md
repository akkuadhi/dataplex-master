# Phase 1: BigQuery Schema Discovery Agent

This agent is the first step in the Dataplex pipeline. It ensures that the rules you create are based on the actual "Ground Truth" of your BigQuery tables.

## **How it Works**
1. **Authentication**: Uses your Google Cloud credentials to scan accessible projects.
2. **Discovery**: 
   - Prompts for table names you are interested in.
   - Automatically scans all projects and datasets to find those specific tables.
   - Filters the list to show *only* the locations where the tables exist.
3. **Extraction**: Once a location is selected, it pulls the official schema (Column Name, Data Type, Mode) directly from BigQuery.

## **Verification Checkpoints**
- **Location Confirmation**: The agent presents the list of Project/Dataset matches and asks you to select the correct one.
- **Metadata Review**: After fetching the schema, it displays the columns and types for your review. This prevents creating rules for columns that don't exist or have been renamed.

## **Setup & Execution**
1. Navigate to `Dataplex Master/Schema/`.
2. Run `python bq_schema_agent.py`.
3. Follow the interactive prompts to identify your target tables.
