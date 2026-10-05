# Start here

1. Extract this ZIP.
2. Open Terminal and change into the extracted doctoral-advising-workspace folder.
3. Run:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8001
```

4. Open http://127.0.0.1:8001.
5. Select a role; demo password is `demo-research`.
6. Start as the researcher, submit the topic, then switch to Advisor and University to complete approvals.

Keep the terminal open while using the app. Ctrl+C stops it. README.md has the full walkthrough.

Local portfolio demo only. No real student records or public deployment with demo credentials. No email is sent by this application.
