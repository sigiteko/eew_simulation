# EEW Simulation Framework

## Overview
This repository provides a **simulation framework for Earthquake Early Warning (EEW)**.  
It models earthquake sources, computes lead times, and evaluates the usefulness of alerts in reducing seismic risk.  

The **case study focuses on West Sumatra, Indonesia**, where strong earthquakes originate from:  
- **Sumatra Fault** (crustal events)  
- **Mentawai Subduction Zone** (megathrust events)  

By leveraging real-time event detection from **TEAM** (Transformer Earthquake Alerting Model) and source parameter updates from **TEAM-Location & Magnitude (TEAM-LM)**, this framework simulates how alerts could be issued and how much time communities have to take protective actions.

---

## Features
- Ingest **TEAM** detections and **TEAM-LM** source parameters (lat, lon, depth, Mw).  
- Travel-time calculation for P- and S-waves → estimate warning window.  
- Ground-motion prediction (PGA thresholds, e.g., 0.05 g, 0.1 g).  
- Lead-time statistics: minimum, median, maximum across sites.  
- Population exposure & blind-zone mapping.  
- Adaptable to other regions with configurable source models and hazard data.  

---

## Data Sources
- **TEAM**: earthquake detection alerts.  
- **TEAM-LM**: source location & magnitude refinements.  
- **Velocity model**: 1-D/3-D crustal model (e.g., CRUST1.0 or regional).  
- **VS30 / site conditions** (optional): for site amplification.  
- **Population data** (optional): e.g., LandScan or WorldPop.  

---

## Methods
The EEW simulation follows five steps (adapted from [Cremen et al., 2022](https://doi.org/10.1038/s41467-021-27807-2)):  

1. **Event Detection**: ingest TEAM detections.  
2. **Source Characterization**: update location & magnitude using TEAM-LM.  
3. **Travel-Time Modeling**: compute P- and S-wave arrivals at stations and sites.  
4. **Ground-Motion Estimation**: predict PGA.  
5. **Lead-Time**: calculate available lead time.  

---

## Citation
When using the implementation of **TEAM** or **TEAM-LM**, please cite the associated software and key publications:  

```bibtex
@misc{munchmeyer2021softwareteam,
  doi       = {10.5880/GFZ.2.4.2021.003},
  author    = {M{"u}nchmeyer, Jannes and Bindi, Dino and Leser, Ulf and Tilmann, Frederik},
  title     = {TEAM – The transformer earthquake alerting model},
  publisher = {GFZ Data Services},
  year      = {2021},
  note      = {v1.0},
  copyright = {GPLv3}
}

@article{munchmeyer2020team,
  title   = {The transformer earthquake alerting model: A new versatile approach to earthquake early warning},
  author  = {M{"u}nchmeyer, Jannes and Bindi, Dino and Leser, Ulf and Tilmann, Frederik},
  journal = {Geophysical Journal International},
  year    = {2020},
  doi     = {10.1093/gji/ggaa609}
}

@article{munchmeyer2021teamlm,
  title   = {Earthquake magnitude and location estimation from real time seismic waveforms with a transformer network},
  author  = {M{"u}nchmeyer, Jannes and Bindi, Dino and Leser, Ulf and Tilmann, Frederik},
  journal = {Geophysical Journal International},
  year    = {2021},
  doi     = {10.1093/gji/ggab139}
}
```

---

⚠️ **Note:** This repository is a research prototype, not an operational EEW system.  
