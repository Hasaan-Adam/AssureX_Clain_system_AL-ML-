# AssureX Claim Engine — Installation & Environment Setup Guide 💻

---

## 1. System Requirements

### Hardware Requirements
- **CPU:** Dual-core 2.0 GHz or higher (Quad-core recommended for model training)
- **RAM:** Minimum 4 GB (8 GB recommended for Computer Vision training)
- **Disk Space:** 2 GB free disk space

### Software Prerequisites
- **Operating System:** Windows 10/11, macOS 12+, or Ubuntu Linux 20.04+
- **Python:** Python 3.11.x or 3.12.x
- **Package Manager:** `pip` (v23.0+)
- **Git Version Control**

---

## 2. Step-by-Step Installation

### Step 1: Clone Repository
```bash
git clone https://github.com/AssureX-Engine/AssureX-Claim-Engine.git
cd AssureX-Claim-Engine
```

### Step 2: Set Up Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Core Dependencies
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Step 4: Verify Environment Installation
```bash
python -c "import fastapi, sklearn, PIL; print('AssureX Environment Ready!')"
```