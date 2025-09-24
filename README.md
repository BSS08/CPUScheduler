# Process Scheduling Simulator (FCFS / SJF / SRTF)

Interactive Streamlit app to simulate classic CPU scheduling algorithms and visualize results:
- FCFS (First-Come First-Served)
- SJF (Shortest Job First, non-preemptive)
- SRTF (Shortest Remaining Time First, preemptive)

Outputs: Gantt charts, per-time animations, and tables (CT, TAT, WT) with averages.

---

## Quickstart (local)

Requirements: Python 3.11

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
streamlit run app.py
```

The app starts at http://localhost:8501

---

## Using the app
- Sidebar: upload CSV or edit the table (columns: pid, arrival, burst). Optional `priority` accepted (not used yet).
- Leave pid empty to auto-label (`P1`, `P2`, ...).
- Rules: arrival ≥ 0, burst > 0.
- App auto-runs all algorithms and shows metrics & charts.

---

## Deploy on Streamlit Community Cloud
1) Push this project to GitHub with these files at repo root:
   - `app.py`
   - `requirements.txt` (use `pip freeze > requirements.txt`)
   - `runtime.txt` (contains: `python-3.11`)
   - `.gitignore`
2) Go to https://share.streamlit.io and sign in with GitHub.
3) Click New app → select your repo and branch.
4) Main file path: `app.py` → Deploy.
5) If you change dependencies, push updates and then use App menu → Reboot and clear cache.

Your app URL will look like:
```
https://<github-username>-<repo>-<branch>.streamlit.app
```

---

## Project structure
```
.
├─ app.py
├─ requirements.txt
├─ runtime.txt
└─ .gitignore
```

---

## Troubleshooting
- ModuleNotFoundError on Cloud → add the package to `requirements.txt`, push, then reboot cache.
- Blank Gantt → ensure arrival/burst are numeric and valid; apply edits in the data editor.
- Wrong entry point → set `app.py` as the main file in the deploy form.

---

## Roadmap
- Round Robin and Priority scheduling
- Context switch overhead
- Export tables and charts

---

## License
Choose a license (e.g., MIT) and add it to the repo.
