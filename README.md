# AssureX Claim Engine 🚀

An AI-powered, Web-based warranty claim validation application that helps manufacturers and service centers evaluate claims accurately and efficiently using a Dual-Model AI approach (Python XGBoost + Google Teachable Machine).

---

## 🔗 Live Deployment URLs
- **Frontend (Vercel):** [Insert your Vercel URL here]
- **Backend API (Ngrok):** `https://unworthy-squishy-knelt.ngrok-free.dev`
- **Technical Blog:** https://abkbloggers.blogspot.com/2026/09/claim-engine-comprehensive-technical.html
- **Demonstration Video:** [Insert your YouTube/Drive link here]

### Evaluator Login Credentials
- **Admin:** `admin@assurex.com` / `admin123`
- **Reviewer:** `reviewer@assurex.com` / `review123`
- **Customer:** `customer@assurex.com` / `cust123`

---

## 💻 Installation Instructions

### Prerequisites
- Operating System: Windows 10/11, macOS, or Linux
- Python Version: Python 3.10+
- Node.js Version: v18+

### Complete Project Setup
1. **Clone the final repository:** `git clone https://github.com/bkhanzaza551-a11y/AssureX_Clain_system_AL-ML-.git`
2. **Navigate to the main directory:** `cd AssureX_Clain_system_AL-ML-`

### Backend Setup
1. **Create a virtual environment:** `python -m venv .venv`
4. **Activate the virtual environment:** 
   - Windows: `.venv\Scripts\activate`
   - Mac/Linux: `source .venv/bin/activate`
5. **Install dependencies:** `pip install -r requirements.txt`
6. **Initialize Database:** The SQLite database `assurex.db` will be auto-generated on the first run.
7. **Environment Variables:** Create a `.env` file containing your secret keys.
8. **Run Backend:** `uvicorn src.main:app --host 0.0.0.0 --port 8000` (or double-click `run_backend.bat`).

### Frontend Setup
1. **Navigate to the frontend directory:** `cd frontend`
2. **Install dependencies:** `npm install`
4. **Configure Environment:** Create a `.env` file and set `VITE_API_URL=http://localhost:8000/api/v1` (or your Ngrok URL).
5. **Run Frontend:** `npm run dev` (or double-click `run_frontend.bat`).

---

## ⚙️ Execution Instructions

1. **Register/Login:** Navigate to the homepage and log in using the credentials provided above.
2. **Register a Product:** Go to 'My Products' -> 'Add Product'. Fill in the serial number and purchase details.
3. **Submit a Claim:** Click 'File a Claim'. You will be prompted to upload a receipt and images of the damaged product.
4. **OCR Extraction:** The system will automatically extract text from your uploaded receipt via Tesseract. Review the extracted data.
5. **AI Evaluation:** Upon submission, the backend triggers the XGBoost model for structured data evaluation, while the frontend/backend invokes the GTM Vision model for image evaluation.
6. **Reviewer Dashboard:** Log in as a Reviewer. Navigate to the 'Review Queue' to see claims flagged due to Model Contradiction or Rule Violation (e.g., duplicate serial numbers).
7. **Admin Dashboard:** Log in as an Admin to view analytics, system health, and overall claim resolution rates.

---

## 🛑 Known Limitations & Assumptions
- **OCR Accuracy:** Highly dependent on the lighting and quality of the uploaded receipt. Crumpled receipts may result in partial text extraction.
- **Model Variance:** The Python model is trained on a synthetic dataset (with 8% realistic noise). It simulates real-world behavior but is limited to the statistical boundaries of the generated data.
- **Assumption:** Teachable Machine models run best on desktop browsers with sufficient RAM.

## 📄 Documentation
All project reports, UML diagrams, test cases, and model comparison reports are located in the `documentation/` directory.

---
*Developed for the Aptech NextWave AI and ML Competition.*