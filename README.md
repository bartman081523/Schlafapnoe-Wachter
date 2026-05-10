# SleepApnea-Monitor

SleepApnea-Monitor is a concept study and implementation of an Edge-AI-based Android application for real-time detection of Obstructive Sleep Apnea (OSAS) using acoustic analysis.

## Project Overview

The system uses the smartphone as a non-invasive sensor to record breathing sounds during sleep and analyze them locally on the device (Edge Computing). Upon detecting an apnea event (breathing pause > 10s), the app intervenes with an acoustic warning tone to wake the patient or trigger a change in sleeping position.

### Core Technologies
- **Machine Learning:** Python, TensorFlow, TensorFlow Hub (YAMNet), Librosa (Audio-Preprocessing).
- **Edge Deployment:** TensorFlow Lite (TFLite) with Dynamic Range Quantization and XNNPack-Optimization.
- **Android App:** Native development (Kotlin), Foreground Services, AudioRecord API, AudioAttributes (DND-Override).

### Advanced Features
- **Storage-Efficient AAC Logging:** The app records the night in the highly efficient AAC (.m4a) format, saving hundreds of megabytes per night while still running ML analysis on the raw PCM data stream.
- **Autonomous Self-Optimization Brain:** The app learns from each night. It records the active settings alongside the sleep data, detects if it was too sensitive or insensitive, and auto-adjusts its parameters (RMS thresholds, trigger duration) dynamically to find the user's "sweet spot".
- **Interactive Morning Questionnaire:** Guided flow to optimize parameters based on qualitative user feedback (e.g., if the user woke up too often or if the alarm was too loud), dynamically adjusting ML label weights for subsequent nights.
- **Adaptive Aesthetics:** Deep Night Dark Mode and seamless Light Mode integration to follow system settings and ease usage in bedroom environments.
- **DND-Override:** The app forces audibility using `USAGE_ALARM` and Critical Alert policies to guarantee intervention even in the deepest "Do Not Disturb" profiles.

## Architecture

The project consists of two main pillars:
1. **Python ML Pipeline:** For preprocessing training data (heuristics, FFT, RMS analysis) and generating the optimized TFLite model via Transfer Learning (YAMNet).
2. **Android Application:** Designed for resource-efficient continuous operation using a Cascade-Architecture (lightweight RMS check triggering deep ML inference only upon suspicious patterns).

## Setup & Deployment
The app leverages CI/CD for automated testing and releases. It supports seamless self-updating via the GitHub Releases API.

*Note: This project is an experimental prototype intended for research and concept validation, not as a replacement for clinical polysomnography (PSG).*
