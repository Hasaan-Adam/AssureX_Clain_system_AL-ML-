# Our AI Transparency Statement

We used Gemini/ChatGPT to help write boilerplate code, but we manually fixed many bugs it introduced. 

For example, we used AI to help brainstorm the edge cases for our synthetic dataset, but we had to write the Python generation scripts ourselves to get the distributions right. We also used ChatGPT to generate the initial component structure for our frontend and it helped debug some frustrating FastAPI middleware CORS issues when we were stuck. 

We did not use LLMs to generate our core business logic or machine learning models. The ML models were trained using standard scikit-learn and Google Teachable Machine.

Overall, AI was a helpful tool, but we had to verify and rewrite a lot of its output because it sometimes generated code that didn't match our actual database schema or used outdated library versions.

## AI Tool Usage Declaration (Late Stage Fixes)

* **Name of the AI tool:** Google Antigravity Agent
* **Purpose of use:** Deep Code Audit and Integrity Bug Fixing
* **Prompt or type of assistance requested:** Deep analyze the project against Aptech SRS
* **Files or modules affected:** dataset_generator/stratified_split.py, src/services/prediction_service.py, src/services/tm_service.py
* **Modifications performed by the team:** Fixed dataset splitting ratio to exactly 70/15/15. Replaced static/mocked TM visual inference with genuine numpy vector operations against trained weights. Removed data leakage in the dual-model adjudication process.
* **Testing completed by the team:** Ran pytest test suite. Regenerated dataset via Python CLI. Retrained XGBoost machine learning model.
* **Name of the team member who verified the output:** Ahmed Bilal Khan

## AI Tool Usage Declaration (Role-Based Features Implementation)
* **Name of the AI tool:** Google Antigravity Agent
* **Purpose of use:** Swarm Auditing and Feature Completion for Role-Based Access
* **Prompt or type of assistance requested:** Deploy 5 mini-agents to verify Customer, Staff, Reviewer, and Admin workflows.
* **Files or modules affected:** src/api/v1/claims.py, src/api/v1/repairs.py, frontend/src/pages/PoliciesPage.jsx, frontend/src/pages/AuditLogsPage.jsx, frontend/src/components/claim/RepairModal.jsx
* **Modifications performed by the team:** Added Service Staff Repair History UI and backend APIs. Implemented Global Audit Explorer and Warranty Policy UI for Administrators. Modified Claim creation to allow staff to submit on behalf of customers. Added Request Info action for reviewers.
* **Testing completed by the team:** End-to-end frontend rendering checks and backend route validation.
* **Name of the team member who verified the output:** Ahmed Bilal Khan

