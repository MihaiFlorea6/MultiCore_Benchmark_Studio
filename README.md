# MultiCore Benchmark Studio  
# Technical Description  
A multi-language benchmarking framework designed to evaluate and compare the parallel execution performance of multicore architectures. This project demonstrates a decoupled hardware-software analytical system, orchestrating high-performance native compute engines (C and Rust) through a real-time Python/Streamlit telemetry dashboard.  

<div align="center">
  <video src="https://github.com/user-attachments/assets/5b8fc884-e90c-4d10-9f79-5251c540f975
" width="800" controls></video>
</div>  

# Architecture and logic control  
The architecture separates the analytical frontend from the computational backends. A Python/Streamlit dashboard acts as the orchestrator, dispatching command-line arguments (algorithm type, thread count, input size, iterations) to native C and Rust executables.  
Results are asynchronously logged into an append-only `results.jsonl` (JSON Lines) file, ensuring robust data persistence and preventing corruption during highly intensive multi-threaded workloads.  

# Objectives  
The primary objective was to build a reliable profiling suite capable of exposing hardware limitations by:  
* **Hardware Profiling:** Stress-testing specific CPU subsystems, including the ALU, FPU, and Cache/RAM hierarchy, using mathematically tailored algorithms.
* **Concurrency Evaluation:** Comparing traditional explicit thread management in C against Rust's high-level `rayon` work-stealing thread pool.
* **Scalability Metrics:** Automatically calculating and visualizing Speedup ($S_p$) factors relative to ideal scalability limits based on Amdahl's Law.
* **Live Telemetry:** Tracking per-core hardware utilization mapping and architectural specifications dynamically during execution using `psutil` and `cpuinfo`.

 # System Logic & Hardware  
 ## 1. Algorithmic Workloads (Hardware-Targeted)  
   The native engines implement 5 distinct computational algorithms, carefully chosen to measure specific scaling bottlenecks:  
* **SquareSum (ALU):** Direct parallelization with minimal memory access, highlighting raw integer throughput and thread-management overhead.
* **Monte Carlo PI (FPU):** Computationally intensive floating-point operations evaluating math co-processor scaling.
* **Matrix Multiplication & Merge Sort (Cache/RAM):** Workloads dominated by memory access patterns, demonstrating bandwidth saturation, cache latency, and "memory wall" constraints.
* **FFT (Interconnect):** "Butterfly" data access patterns that severely stress inter-core synchronization and cache line transfers.  

## 2. Decoupled Data Pipeline & Analysis  
* **Fault-Tolerant Logging:** Native C/Rust workers append execution metrics (language, algorithm, threads, time) directly to the JSONL file.   
<img width="1920" height="1080" alt="Dashboard8" src="https://github.com/user-attachments/assets/31b8bef0-8ecf-43e1-8826-8a7d1427c6c2" />

* **Dynamic Visualization:** The Python backend parses the JSON data on the fly, plotting multi-threaded speedup curves using Matplotlib and presenting raw run-times in structured Pandas DataFrames for deep architectural analysis.  
<img width="1920" height="1036" alt="Dashboard3" src="https://github.com/user-attachments/assets/6a3ecbd9-1c15-4e6f-abbb-11b67eff191d" />

# Skills  
This project demonstrates proficiency in:  
**→ `Systems Programming (C/Rust)` focusing on low-level memory management and hardware-software interaction.**    
**→ `Concurrent Execution`, mastering both explicit OS threading and advanced work-stealing paradigms.**   
**→ `Computer Architecture Analysis`, interpreting CPU caching effects, ALU/FPU bottlenecks, and Amdahl's theoretical limits.**   
**→ `Data Pipeline Engineering`, bridging compiled native languages with Python for automated telemetry and structured JSON parsing.**  
**→ `Full-Stack Telemetry`, using Streamlit to build reactive UI dashboards for live process monitoring.**  

# Testing  
The framework was extensively tested and benchmarked on an Intel Core i5-10300H (x86-64, 4 physical / 8 logical cores, 15GB RAM).  
Experimental results accurately mapped theoretical limits, showing near-ideal speedup for compute-heavy algorithms (like Monte Carlo) until physical cores were saturated and successfully identifying memory-bandwidth bottlenecks for Matrix Multiplication.  

# Key Technologies  
`C`, `Rust (Rayon)`, `Python 3`, `Streamlit`, `Pandas`, `Matplotlib`, `JSON Lines (JSONL)`, `psutil`, `x86-64 Architecture Analysis`.






