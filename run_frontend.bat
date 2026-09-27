@echo off
echo Starting AssureX Frontend Server...
cd frontend
if not exist node_modules (
    echo Installing frontend dependencies...
    npm install
)
npm run dev -- --port 5173
pause
