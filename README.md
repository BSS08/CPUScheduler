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

## License
MIT License

Copyright (c) 2025 Aayushmaan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.



