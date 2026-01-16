# execute to permission: chmod +x run-dev.sh
uv run uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload