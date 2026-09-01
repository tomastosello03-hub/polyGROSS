# polyGROSS

**polyGROSS** is a professional surveying and geomatics mobile application designed for closed traverse analysis, high-precision closure verification, and automated gross angular error detection using dual forward/backward vector ray intersection.

---

## 📌 Features

- **Dual Traverse Vector Path (Adelante / Atrás)**:
  - Computes forward ($V_1 \to V_n$) and backward ($V_1 \to V_n \to \dots \to V_2$) paths to visually and mathematically pinpoint the exact station where gross angular errors occurred.
- **Topographic Closure & Tolerances**:
  - Linear closure calculation ($e_L$, $e_X$, $e_Y$).
  - Angular closure error calculation ($e_\alpha$).
  - Rigorous angular tolerance computation based on the direction observation method: $T_\alpha = a \cdot \sqrt{2n}$.
  - Linear tolerance computation based on instrument precision: $T_L = \frac{p_{cm}}{100} \cdot \sqrt{n}$.
- **Project True North Alignment**:
  - Configurable initial reference azimuth ($V_1 \to V_2$) to align coordinates and graphics with the project coordinate system.
- **Sorted Vertex Separation Table**:
  - Euclidean distance comparison between forward and backward computed coordinates for each station, sorted from smallest to largest separation.
- **Built for Mobile**:
  - Responsive, dark-themed UI optimized for Android and iOS touchscreens powered by Flet & Flutter.

---

## 🚀 Automated APK Build

This repository includes a GitHub Actions CI/CD workflow (`.github/workflows/build_apk.yml`) that automatically compiles standalone Android APKs without requiring local Android Studio or Flutter installation.

---

## 🛠 Tech Stack

- **Python 3.11+**
- **Flet / Flutter**
- **FastAPI / Uvicorn**
