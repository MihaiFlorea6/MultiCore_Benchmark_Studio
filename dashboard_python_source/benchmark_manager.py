import streamlit as st
import subprocess
import pandas as pd
import json
import os
import psutil
import cpuinfo
import matplotlib.pyplot as plt
import time


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXE_C = os.path.join(BASE_DIR, "bench_c", "bench_c", "x64", "Release", "bench_c.exe")
EXE_RS = os.path.join(BASE_DIR, "bench_rs", "target", "release", "bench_rs.exe")
OUT_FILE = os.path.join(BASE_DIR, "results", "results.jsonl")


st.set_page_config(page_title="MultiCore Hardware Lab v2.1", layout="wide", initial_sidebar_state="expanded")


@st.cache_data
def get_static_cpu_info():
    return cpuinfo.get_cpu_info()


info = get_static_cpu_info()


st.title(" MultiCore Hardware Lab & Benchmark Studio")
st.markdown(f"""
**Sistem detectat:** {info['brand_raw']} | **Arhitectură:** {info['arch']} 
| **Nuclee:** {psutil.cpu_count(logical=False)} Fizice / {psutil.cpu_count(logical=True)} Logice
""")


st.sidebar.header("⚙️ Setări Benchmark")
input_size = st.sidebar.number_input("Dimensiune Date (Size)", value=1000000, step=100000)
num_runs = st.sidebar.slider("Număr de Rulări (pentru medie)", 1, 10, 3)
thread_seq = st.sidebar.multiselect("Secvență Thread-uri", [1, 2, 4, 8, 12, 16, 32], default=[1, 2, 4, 8])

algs_meta = {
    "Sum Squares": {"id": 1, "unit": "ALU (Integer)", "desc": "Calcul aritmetic simplu, test de throughput."},
    "Matrix Multiply": {"id": 2, "unit": "FPU & RAM",
                        "desc": "Înmulțire de matrice, solicită lățimea de bandă a memoriei."},
    "Monte Carlo": {"id": 3, "unit": "FPU (Float)", "desc": "Calcul numeric intensiv (estimare PI)."},
    "Merge Sort": {"id": 4, "unit": "Cache & RAM", "desc": "Sortare paralelă, test de latență și acces memorie."},
    "FFT": {"id": 5, "unit": "FPU & Interconnect", "desc": "Transformată Fourier, model de acces 'butterfly'."}
}
selected_names = st.sidebar.multiselect("Algoritmi de inclus", list(algs_meta.keys()), default=list(algs_meta.keys()))

if st.sidebar.button("🚀 PORNEȘTE SESIUNEA DE ANALIZĂ"):
    if not selected_names or not thread_seq:
        st.error("Selectează cel puțin un algoritm și un număr de thread-uri!")
    else:
        st.info("Benchmark în desfășurare... Consolele externe rulează în fundal.")

        core_placeholder = st.empty()

        start_session_time = time.time()

        os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
        if os.path.exists(OUT_FILE):
            os.remove(OUT_FILE)

        progress_bar = st.progress(0)
        total_steps = len(selected_names) * len(thread_seq)
        step = 0

        for name in selected_names:
            alg_id = algs_meta[name]['id']
            for t in thread_seq:
                commands = [
                    [EXE_C, "--alg", str(alg_id), "--threads", str(t), "--runs", str(num_runs), "--size",
                     str(input_size), "--out", OUT_FILE],
                    [EXE_RS, "--alg", str(alg_id), "--threads", str(t), "--runs", str(num_runs), "--size",
                     str(input_size), "--out", OUT_FILE]
                ]

                for cmd in commands:

                    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


                    while process.poll() is None:
                        with core_placeholder.container():
                            st.write(
                                f"⚙️ Se execută: **{name}** ({'C' if 'bench_c' in cmd[0] else 'Rust'}) | Threads: {t}")
                            cpu_usage = psutil.cpu_percent(percpu=True)
                            cols = st.columns(4)
                            for i, usage in enumerate(cpu_usage):
                                with cols[i % 4]:
                                    st.progress(usage / 100)
                                    st.caption(f"Core {i}: {usage}%")
                        time.sleep(0.1)

                step += 1
                progress_bar.progress(step / total_steps)

        end_session_time = time.time()
        total_duration = end_session_time - start_session_time


        st.success(f"Sesiune finalizată cu succes în {total_duration:.2f} seconds! Datele au fost colectate.")



st.divider()
col_hw1, col_hw2 = st.columns([2, 1])

with col_hw1:
    st.subheader("📊 Core Utilization Map (Real-Time)")
    cpu_usage_per_core = psutil.cpu_percent(percpu=True)
    hw_cols = st.columns(4)
    for i, usage in enumerate(cpu_usage_per_core):
        with hw_cols[i % 4]:
            st.write(f"**Core {i}**")
            st.progress(usage / 100)
            st.caption(f"Load: {usage}%")

with col_hw2:
    st.subheader("🔍 Specificații Arhitectură")
    with st.expander("Detalii Procesor & Cache", expanded=True):
        st.write(f"**Frecvență:** {info.get('hz_actual_friendly', 'N/A')}")
        st.write(f"**L2 Cache:** {info.get('l2_cache_size', 'N/A')}")
        st.write(f"**L3 Cache:** {info.get('l3_cache_size', 'N/A')}")
        st.write(f"**Flags:** {', '.join(info.get('flags', [])[:8])}...")
        ram = psutil.virtual_memory()
        st.write(f"**RAM Total:** {ram.total // (1024 ** 3)} GB")
        st.write(f"**RAM Liber:** {ram.available // (1024 ** 2)} MB")


st.divider()
st.subheader("🧠 Impactul Algoritmilor asupra Unităților de Calcul")
c_al, c_fp, c_mem = st.columns(3)

with c_al:
    st.info(
        "### ALU (Integer)\n**Sum Squares** utilizează unitatea aritmetică pentru calcule întregi și operații de acumulare.")
with c_fp:
    st.success(
        "### FPU (Float)\n**Monte Carlo & FFT** solicită unitatea de virgulă mobilă pentru calcule de precizie și funcții trigonometrice.")
with c_mem:
    st.warning(
        "### Cache/RAM\n**Matrix Multiply & Merge Sort** testează latența cache-ului și lățimea de bandă a controller-ului de memorie.")


if os.path.exists(OUT_FILE):
    st.divider()
    st.subheader("📈 Rezultate Scalabilitate (Speedup Factor)")


    data = []
    with open(OUT_FILE, 'r') as f:
        for line in f:
            if line.strip(): data.append(json.loads(line))

    if data:
        df = pd.DataFrame(data)
        df_avg = df.groupby(['language', 'alg', 'threads'])['seconds'].mean().reset_index()


        tabs = st.tabs(selected_names)

        for i, name in enumerate(selected_names):
            with tabs[i]:
                alg_id = algs_meta[name]['id']
                st.write(f"**Analiză:** {algs_meta[name]['desc']}")
                st.write(f"**Unitate Hardware vizată:** {algs_meta[name]['unit']}")

                col_graph, col_data = st.columns([2, 1])

                subset = df_avg[df_avg['alg'] == alg_id]

                with col_graph:
                    fig, ax = plt.subplots(figsize=(10, 5))

                    for lang in subset['language'].unique():
                        lang_data = subset[subset['language'] == lang].sort_values('threads')


                        t1_row = lang_data[lang_data['threads'] == 1]
                        if not t1_row.empty:
                            t1 = t1_row['seconds'].values[0]
                            speedup = t1 / lang_data['seconds'].values
                            ax.plot(lang_data['threads'], speedup, marker='o', label=f"Speedup {lang.upper()}")
                        else:

                            ax.plot(lang_data['threads'], lang_data['seconds'], marker='x',
                                    label=f"Time {lang.upper()} (s)")
                            ax.set_ylabel("Timp (secunde)")


                    if not subset[subset['threads'] == 1].empty:
                        max_threads = subset['threads'].max()
                        ax.plot([1, max_threads], [1, max_threads], 'k--', alpha=0.5, label="Scalabilitate Ideală")
                        ax.set_ylabel("Factor Speedup (S)")

                    ax.set_xlabel("Număr de Thread-uri (p)")
                    ax.set_title(f"Scalabilitate: {name}")
                    ax.legend()
                    ax.grid(True, alpha=0.3)
                    st.pyplot(fig)

                with col_data:
                    st.write("Media timpilor (s):")
                    st.dataframe(subset[['language', 'threads', 'seconds']].sort_values('threads'))
    else:
        st.warning("Fișierul de rezultate este gol. Rulează benchmark-ul.")
else:
    st.warning("Nu s-au găsit date. Configurează parametrii din stânga și apasă 'Execute'.")


st.caption("MultiCore Hardware Lab v2.1 | 2026 Academic Project | Focus: Architecture Specifics (ALU/FPU/Cache)")