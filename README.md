# MediQueue AI — Smart Hospital Queue System

A beginner-friendly Streamlit demonstration for patient registration,
appointment scheduling, queue management and estimated waiting times.

## Deploy on Streamlit Community Cloud

1. Create a GitHub repository named `MediQueue-AI`.
2. Upload `app.py`, `database.py`, `predictor.py`, and `requirements.txt`.
3. Open https://share.streamlit.io/ and sign in with GitHub.
4. Select **Create app**.
5. Choose your repository and branch.
6. Set **Main file path** to `app.py`.
7. Select **Deploy**.

Streamlit will install dependencies from `requirements.txt` and launch the app.

## Run locally

```bash
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

## Important limitations

This is an educational prototype, not a certified hospital information system.
The waiting-time estimator is a simple baseline based on average completed
service durations, not a trained or validated AI model. Queue priority must
be assigned by qualified clinical staff. Never use this app as the sole basis
for emergency triage or clinical decisions.

The SQLite database is stored in the app's local filesystem. On Streamlit
Community Cloud, local files may not be durable across restarts, redeployments
or infrastructure changes. For real use, connect a managed persistent database,
add authentication and role-based permissions, encryption, audit logs, backups,
privacy/legal review, security testing and clinical validation. Use fictional
data only in this public demo.
