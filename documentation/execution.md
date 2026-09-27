# AssureX Claim Engine — Execution & Operations Manual 🏃

---

## 1. Pipeline Execution Workflow

The complete end-to-end operation of the AssureX Claim Engine comprises four primary execution stages:

```
[ 1. Init Database ] ──► [ 2. Train Models ] ──► [ 3. Run Benchmark Reports ] ──► [ 4. Launch FastAPI ]
```

---

## 2. Command Reference

### Stage 1: Database Initialization & Seeding
Initializes the SQLite database schema and creates admin/adjuster demo accounts.
```bash
python -m src.scripts.init_db
```

### Stage 2: Tabular Model Training & Selection Pipeline
Trains candidate algorithms, benchmarks validation accuracy against the $\ge 85\%$ SRS target, and serializes the winning model.
```bash
python -m src.ml.train --train data/train/claims_train.csv --val data/validation/claims_validation.csv --version v1.0.0
```

### Stage 3: Generate Model Comparison Report (36 Unseen Claims)
Evaluates held-out test claims, computes dual-model confidence deltas, and outputs `reports/model_comparison_report.csv`.
```bash
python scripts/generate_model_comparison_report.py
```

### Stage 4: Launch Web Server & Adjuster Portal
Starts the high-performance asynchronous FastAPI server:
```bash
uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```

- **Interactive API Documentation:** Open browser at `http://127.0.0.1:8000/docs`
- **Adjuster Portal UI:** Open browser at `http://127.0.0.1:8000/`

---

## 3. Running Demo Scenarios

You can evaluate any of the 11 demo scenarios via curl or python:

```bash
# Evaluate Demo Scenario 01 (Valid Claim)
curl -X POST "http://127.0.0.1:8000/api/v1/claims/evaluate" \
     -H "Content-Type: application/json" \
     -d @sample_claims/01_valid_claim/claim.json
```