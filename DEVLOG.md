# AssureX Claim Engine — Development Log

**Project:** AssureX Claim Engine
**Timeline:** 4 Weeks

---

## Week 1: Scoping, Requirements & Database
- Spent the first few days arguing over requirements and finalizing the system bounds.
- Decided on the dual-AI approach (rules + tabular ML + vision).
- Designed the SQLite/SQLAlchemy schema. 
- **Struggles:** Had a lot of trouble with SQLAlchemy circular imports between `claims` and `audit_logs`. Finally figured out how to decouple them by moving audit logs to a separate service file.

## Week 2: Synthetic Data & Visual Card Generation
- Wrote scripts to generate 1,500 fake claims for testing (we couldnt get real warranty data obviously).
- Added edge cases like serial mismatches, out of date claims, etc.
- Used Python Pillow to generate 224x224 RGB image cards.
- **Struggles:** We accidentally messed up the timestamp logic in the synthetic data and had to regenerate the whole dataset becuase the dates were in the future lol.

## Week 3: Tabular ML Engine & Rule Pipeline
- Built the feature engineering pipeline (23 features).
- Tested a few models (Logistic Regression, Random Forest). 
- **Struggles:** Model initial accuracy was 71% — had to retrain with better features and fix some bugs in our data splits to finally get it working well.
- Built the deterministic rule engine to catch obvious policy violations before the ML model even runs.

## Week 4: Teachable Machine & FastAPI Integration
- Trained Google Teachable Machine on the claim cards.
- Built the FastAPI backend to tie it all together and the frontend dashboard.
- **Struggles:** CORS issues took 2 days to debug when connecting the frontend to FastAPI. Also, React Router v6 gave us trouble because the syntax changed a lot since the tutorials we watched. Finally got the dashboard working.

Overall, we barely finished in time but the demo works great!