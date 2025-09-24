import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dataclasses import dataclass
from typing import List, Dict, Tuple

st.set_page_config(layout="wide", page_title="Process Scheduling Simulator (FCFS / SJF / SRTF)")

# -------------------------
# Utilities / Data classes
# -------------------------
@dataclass
class Process:
    pid: str
    arrival: int
    burst: int
    priority: int = 0  # not used but kept for extensibility

def parse_df_to_processes(df: pd.DataFrame) -> List[Process]:
    """Parse DataFrame to Process objects with validation."""
    if df.empty:
        return []
    
    df2 = df.copy()
    df2 = df2.fillna(0)
    
    # Validate required columns
    required_cols = ['arrival', 'burst']
    missing_cols = [col for col in required_cols if col not in df2.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # ensure pid column exists
    if 'pid' not in df2.columns:
        df2.insert(0, 'pid', [f'P{i+1}' for i in range(len(df2))])
    
    # Select relevant columns
    df2 = df2[['pid','arrival','burst','priority']] if 'priority' in df2.columns else df2[['pid','arrival','burst']]
    
    procs = []
    for _, r in df2.iterrows():
        try:
            pid = str(r['pid'])
            arrival = int(r['arrival'])
            burst = int(r['burst'])
            priority = int(r['priority']) if 'priority' in r.index else 0
            
            # Validate values
            if arrival < 0:
                raise ValueError(f"Arrival time must be non-negative for process {pid}")
            if burst <= 0:
                raise ValueError(f"Burst time must be positive for process {pid}")
            
            procs.append(Process(pid=pid, arrival=arrival, burst=burst, priority=priority))
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid data for process {r.get('pid', 'unknown')}: {e}")
    
    return procs

# -------------------------
# Scheduling Algorithms
# -------------------------
def fcfs_scheduler(proc_list: List[Process]) -> Tuple[List[Dict], pd.DataFrame, List[Dict]]:
    """First Come First Served scheduler implementation."""
    if not proc_list:
        return [], pd.DataFrame(), []
    
    procs = sorted(proc_list, key=lambda p: p.arrival)
    time = 0
    gantt = []
    results = []
    timeline = []  # per-time-unit for animation
    
    for p in procs:
        start = max(time, p.arrival)
        # idle time
        if start > time:
            # CPU idle from time -> start
            for t in range(time, start):
                timeline.append({"time": t, "running": "IDLE"})
            time = start
        finish = start + p.burst
        gantt.append({"pid": p.pid, "start": start, "finish": finish})
        for t in range(start, finish):
            timeline.append({"time": t, "running": p.pid})
        ct = finish
        tat = ct - p.arrival
        wt = tat - p.burst
        results.append({"pid": p.pid, "AT": p.arrival, "BT": p.burst, "CT": ct, "TAT": tat, "WT": wt})
        time = finish
    
    return gantt, pd.DataFrame(results), timeline

def sjf_nonpreemptive_scheduler(proc_list: List[Process]) -> Tuple[List[Dict], pd.DataFrame, List[Dict]]:
    """Shortest Job First (non-preemptive) scheduler implementation."""
    if not proc_list:
        return [], pd.DataFrame(), []
    
    procs = sorted(proc_list, key=lambda p: (p.arrival, p.burst))
    time = 0
    gantt = []
    results = []
    timeline = []
    ready = []
    remaining = procs.copy()
    
    while remaining or ready:
        # move arrived processes to ready
        while remaining and remaining[0].arrival <= time:
            ready.append(remaining.pop(0))
        if not ready:
            # idle until next arrival
            if remaining:
                for t in range(time, remaining[0].arrival):
                    timeline.append({"time": t, "running": "IDLE"})
                time = remaining[0].arrival
            continue
        # choose shortest burst among ready
        ready.sort(key=lambda p: p.burst)
        p = ready.pop(0)
        start = time
        finish = start + p.burst
        gantt.append({"pid": p.pid, "start": start, "finish": finish})
        for t in range(start, finish):
            timeline.append({"time": t, "running": p.pid})
        ct = finish
        tat = ct - p.arrival
        wt = tat - p.burst
        results.append({"pid": p.pid, "AT": p.arrival, "BT": p.burst, "CT": ct, "TAT": tat, "WT": wt})
        time = finish
    
    return gantt, pd.DataFrame(results), timeline

def srtf_scheduler(proc_list: List[Process]) -> Tuple[List[Dict], pd.DataFrame, List[Dict]]:
    """Shortest Remaining Time First (preemptive) scheduler implementation."""
    if not proc_list:
        return [], pd.DataFrame(), []
    
    procs = sorted(proc_list, key=lambda p: p.arrival)
    n = len(procs)
    remaining_burst = {p.pid: p.burst for p in procs}
    arrival_map = {p.pid: p.arrival for p in procs}
    completed = {}
    timeline = []
    time = 0
    gantt_segments = []  # list of dicts with pid,start,finish to merge later
    
    while len(completed) < n:
        # find available processes
        available = [p for p in procs if arrival_map[p.pid] <= time and p.pid not in completed]
        if not available:
            # idle
            timeline.append({"time": time, "running": "IDLE"})
            time += 1
            continue
        # choose process with shortest remaining time
        available.sort(key=lambda p: remaining_burst[p.pid])
        cur = available[0]
        # run for 1 time unit (preemptive at each time unit)
        timeline.append({"time": time, "running": cur.pid})
        remaining_burst[cur.pid] -= 1
        time += 1
        if remaining_burst[cur.pid] == 0:
            completed[cur.pid] = time  # completion time
    
    # build Gantt segments from timeline by merging contiguous same pid intervals
    if timeline:
        cur_pid = timeline[0]['running']
        seg_start = timeline[0]['time']
        for entry in timeline[1:]:
            if entry['running'] != cur_pid:
                seg_end = entry['time']
                # only append CPU segments (not idle) to gantt
                if cur_pid != "IDLE":
                    gantt_segments.append({"pid": cur_pid, "start": seg_start, "finish": seg_end})
                cur_pid = entry['running']
                seg_start = entry['time']
        # last segment
        seg_end = timeline[-1]['time'] + 1
        if cur_pid != "IDLE":
            gantt_segments.append({"pid": cur_pid, "start": seg_start, "finish": seg_end})
    
    # results table using completion times
    results = []
    for p in procs:
        ct = completed[p.pid]
        tat = ct - p.arrival
        wt = tat - p.burst
        results.append({"pid": p.pid, "AT": p.arrival, "BT": p.burst, "CT": ct, "TAT": tat, "WT": wt})
    
    return gantt_segments, pd.DataFrame(results), timeline

# -------------------------
# Visualization Helpers
# -------------------------
def make_gantt_figure(gantt_list: List[Dict], title: str) -> go.Figure:
    """Create Gantt chart figure from gantt data."""
    if not gantt_list:
        fig = go.Figure()
        fig.update_layout(title=title, height=300, margin=dict(l=20,r=20,t=30,b=20))
        return fig
    
    try:
        # Create figure using go.Figure for better control
        fig = go.Figure()
        
        # Define colors for different processes
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        
        # Add a bar for each process
        for i, gantt_item in enumerate(gantt_list):
            duration = gantt_item['finish'] - gantt_item['start']
            fig.add_trace(go.Bar(
                name=gantt_item['pid'],
                x=[duration],  # duration (width of the bar)
                y=[gantt_item['pid']],  # process name (y-axis position)
                orientation='h',  # horizontal bars
                base=gantt_item['start'],  # start time (base position)
                marker_color=colors[i % len(colors)],
                showlegend=True,
                hovertemplate=f"<b>{gantt_item['pid']}</b><br>" +
                             f"Start: {gantt_item['start']}<br>" +
                             f"Finish: {gantt_item['finish']}<br>" +
                             f"Duration: {duration}<br>" +
                             "<extra></extra>"
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Time",
            yaxis_title="Process",
            height=300,
            margin=dict(l=20,r=20,t=30,b=20),
            barmode='overlay'  # Allow bars to overlap if needed
        )
        
        return fig
    except Exception as e:
        st.error(f"Error creating Gantt chart: {e}")
        fig = go.Figure()
        fig.update_layout(title=f"{title} (Error)", height=300, margin=dict(l=20,r=20,t=30,b=20))
        return fig

def make_animation_figure(timeline: List[Dict], title: str) -> go.Figure:
    """Create animation figure from timeline data."""
    if not timeline:
        fig = go.Figure()
        fig.update_layout(title=title, height=350, margin=dict(l=20,r=20,t=30,b=20))
        return fig
    
    try:
        df = pd.DataFrame(timeline)
        if df.empty:
            fig = go.Figure()
            fig.update_layout(title=title, height=350, margin=dict(l=20,r=20,t=30,b=20))
            return fig
        
        # Ensure times start at 0 and are contiguous frames
        df_sorted = df.sort_values('time').reset_index(drop=True)
        # For animation, create a count column and pivot to have a single bar per frame
        # We'll display a single bar showing the running process name (as category)
        # Map processes to numeric heights to plot as a single bar
        df_sorted['proc_label'] = df_sorted['running']
        # To make bars visible, create a 'value' column = 1 when running is not IDLE else 0.5
        df_sorted['value'] = df_sorted['proc_label'].apply(lambda x: 0.8 if x != 'IDLE' else 0.2)
        # We create a frame per time unit
        fig = px.bar(df_sorted, x='proc_label', y='value', animation_frame='time',
                     labels={'proc_label':'Running Process', 'value':'CPU Occupied'}, title=title)
        fig.update_layout(yaxis=dict(range=[0,1.2]), showlegend=False, height=350, margin=dict(l=20,r=20,t=30,b=20))
        return fig
    except Exception as e:
        st.error(f"Error creating animation chart: {e}")
        fig = go.Figure()
        fig.update_layout(title=f"{title} (Error)", height=350, margin=dict(l=20,r=20,t=30,b=20))
        return fig

def results_table_with_metrics(df_results: pd.DataFrame) -> Tuple[pd.DataFrame, float, float]:
    """Calculate metrics from results DataFrame with proper error handling."""
    if df_results.empty:
        return df_results, 0.0, 0.0
    
    try:
        avg_tat = df_results['TAT'].mean()
        avg_wt = df_results['WT'].mean()
        df_sorted = df_results.sort_values('pid').reset_index(drop=True)
        return df_sorted, avg_tat, avg_wt
    except KeyError as e:
        st.error(f"Missing required column in results: {e}")
        return df_results, 0.0, 0.0
    except Exception as e:
        st.error(f"Error calculating metrics: {e}")
        return df_results, 0.0, 0.0

# -------------------------
# App UI
# -------------------------
st.title("🧠 Process Scheduling Simulator — FCFS, SJF, SRTF")

st.markdown("""
**Features**
- Upload CSV or edit processes manually.
- App automatically runs **FCFS**, **SJF (non-preemptive)** and **SRTF (preemptive)** on the same input.
- Shows interactive Gantt, per-time animations, tables, and comparison of Avg TAT / Avg WT.
""")

# Left column: Input
with st.sidebar:
    st.header("Input Processes")
    st.markdown("Provide process data via CSV upload or edit the table below.")
    uploaded = st.file_uploader("Upload CSV (columns: pid, arrival, burst, [priority])", type=['csv'])
    if uploaded:
        try:
            df_input = pd.read_csv(uploaded)
            st.success("CSV loaded.")
        except Exception as e:
            st.error(f"Couldn't parse CSV: {e}")
            df_input = pd.DataFrame(columns=['pid','arrival','burst'])
    else:
        # default example
        df_input = pd.DataFrame([
            {"pid":"P1","arrival":0,"burst":5},
            {"pid":"P2","arrival":1,"burst":3},
            {"pid":"P3","arrival":2,"burst":8},
            {"pid":"P4","arrival":3,"burst":6},
        ])
    st.markdown("You can edit the table values below. Leave PID blank to auto label.")
    try:
        # try using data editor if available
        edited = st.data_editor(df_input, num_rows="dynamic")
        df_input = edited
    except Exception:
        st.write("Editable table not supported in this Streamlit version — using static table. Use CSV to customize.")
        st.dataframe(df_input)
    run_button = st.button("Run Schedulers")

# If user did not press run yet, run automatically (makes UI smoother)
if not run_button:
    run_button = True

if run_button:
    # Validate and parse input
    try:
        procs = parse_df_to_processes(df_input)
        if not procs:
            st.error("No processes provided.")
            st.stop()
    except Exception as e:
        st.error(f"Error parsing processes: {e}")
        st.stop()

    # Run all algorithms
    fcfs_gantt, fcfs_res, fcfs_timeline = fcfs_scheduler(procs)
    sjf_gantt, sjf_res, sjf_timeline = sjf_nonpreemptive_scheduler(procs)
    srtf_gantt, srtf_res, srtf_timeline = srtf_scheduler(procs)

    # Make figures
    fig_fcfs_gantt = make_gantt_figure(fcfs_gantt, "FCFS - Gantt Chart")
    fig_sjf_gantt = make_gantt_figure(sjf_gantt, "SJF (Non-preemptive) - Gantt Chart")
    fig_srtf_gantt = make_gantt_figure(srtf_gantt, "SRTF (Preemptive) - Gantt Chart")

    fig_fcfs_anim = make_animation_figure(fcfs_timeline, "FCFS - Per-time Animation")
    fig_sjf_anim = make_animation_figure(sjf_timeline, "SJF - Per-time Animation")
    fig_srtf_anim = make_animation_figure(srtf_timeline, "SRTF - Per-time Animation")

    # Results and metrics
    fcfs_table, fcfs_avg_tat, fcfs_avg_wt = results_table_with_metrics(fcfs_res)
    sjf_table, sjf_avg_tat, sjf_avg_wt = results_table_with_metrics(sjf_res)
    srtf_table, srtf_avg_tat, srtf_avg_wt = results_table_with_metrics(srtf_res)

    # Top: comparison charts
    st.header("Comparison: Average Turnaround Time & Waiting Time")
    comp_df = pd.DataFrame({
        "Algorithm": ["FCFS", "SJF", "SRTF"],
        "Avg_TAT": [fcfs_avg_tat, sjf_avg_tat, srtf_avg_tat],
        "Avg_WT": [fcfs_avg_wt, sjf_avg_wt, srtf_avg_wt]
    })
    col1, col2 = st.columns(2)
    with col1:
        fig_comp_tat = px.bar(comp_df, x='Algorithm', y='Avg_TAT', title="Avg Turnaround Time")
        st.plotly_chart(fig_comp_tat, use_container_width=True)
    with col2:
        fig_comp_wt = px.bar(comp_df, x='Algorithm', y='Avg_WT', title="Avg Waiting Time")
        st.plotly_chart(fig_comp_wt, use_container_width=True)

    st.markdown("---")

    # Layout: For each algorithm, show Gantt + animation + table side-by-side
    def render_algorithm_section(name, gantt_fig, anim_fig, results_df):
        st.subheader(name)
        col_a, col_b = st.columns([2,1])
        with col_a:
            st.plotly_chart(gantt_fig, use_container_width=True)
            st.plotly_chart(anim_fig, use_container_width=True)
        with col_b:
            st.markdown("**Results**")
            st.dataframe(results_df.style.format({'AT': '{:.0f}', 'BT':'{:.0f}','CT':'{:.0f}','TAT':'{:.0f}','WT':'{:.0f}'}))
            avg_tat = results_df['TAT'].mean()
            avg_wt = results_df['WT'].mean()
            st.markdown(f"**Avg TAT:** {avg_tat:.2f}  \n**Avg WT:** {avg_wt:.2f}")

    render_algorithm_section("FCFS", fig_fcfs_gantt, fig_fcfs_anim, fcfs_table)
    st.markdown("---")
    render_algorithm_section("SJF (Non-preemptive)", fig_sjf_gantt, fig_sjf_anim, sjf_table)
    st.markdown("---")
    render_algorithm_section("SRTF (Preemptive)", fig_srtf_gantt, fig_srtf_anim, srtf_table)

    st.markdown("---")
    st.info("Notes: \n- Gantt chart shows CPU allocation blocks. \n- Animation shows per-time-unit which process is running (IDLE if CPU idle). \n- Algorithms are run automatically on the same input. \n- You can extend this app to add Round Robin or Priority easily by implementing their scheduler functions and hooking them into the UI.")
