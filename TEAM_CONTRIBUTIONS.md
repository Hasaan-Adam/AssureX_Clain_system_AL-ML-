# Team Contribution Record

**Project:** AssureX Claim Engine

### 1. Ahmed Bilal Khan (Team Lead / ML Engineer)
- **Assigned Modules:** Dataset Generation, Python Classification Model (XGBoost), Dual-Model Synthesis Logic.
- **Contributions:** Led the project architecture. Engineered the synthetic dataset with 8% realistic noise to prevent data leakage. Trained and tuned the XGBoost model to achieve 90.11% accuracy. Developed the `prediction_service.py` logic to compare GTM and Python confidence scores.

### 2. Bushra Khalid (Backend Developer)
- **Assigned Modules:** FastAPI Backend, Database Architecture, OCR Integration.
- **Contributions:** Designed the SQLite/PostgreSQL relational schema. Developed asynchronous RESTful API endpoints for claim submission and user authentication. Integrated Tesseract OCR to automatically extract dates and amounts from uploaded receipts.

### 3. Komal Mubeen (Frontend Developer)
- **Assigned Modules:** React.js UI, Claim Wizard, Dashboard Components.
- **Contributions:** Built the responsive frontend Single Page Application using React and TailwindCSS. Developed the intuitive Claim Wizard for users to upload documents. Designed the visual Claim Summary Card UI for reviewers to quickly assess AI predictions.

### 4. Areeb Mughal (QA & Rule Engine Engineer)
- **Assigned Modules:** Deterministic Rule Engine, Google Teachable Machine Training, Testing & Documentation.
- **Contributions:** Built the deterministic Warranty Rule Engine to instantly reject expired or duplicate claims based on document hashes. Trained the MobileNetV2 vision model using Google Teachable Machine. Authored the functional test cases and compiled the final project documentation and reports.
