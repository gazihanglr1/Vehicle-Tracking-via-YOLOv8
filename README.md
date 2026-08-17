<div align="center">

# 🚦 RoadSight Pro

### Real-Time Vehicle Detection, Classification, Tracking & Counting

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![YOLO](https://img.shields.io/badge/Model-YOLO11-00FFFF.svg)](https://docs.ultralytics.com/models/yolo11/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green.svg)](https://opencv.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

<br>

<img src="assets/sample_tracking.png" alt="Sample Tracking Output" width="720"/>

</div>

---

## Overview

A CLI tool for real-time vehicle detection, classification, tracking, and per-class counting using YOLO11 and ByteTrack. Handles track-ID class flickering to keep counts accurate, and supports headless execution for servers and Colab.

**Features:**
- Per-class confidence thresholds
- ByteTrack-based tracking with class-flicker reconciliation
- Accurate per-class unique vehicle counting
- Bounded trail history (memory-safe on long videos)
- Headless mode (no display required)
- JSON/CSV result export
- Fully configurable via CLI

---

## Demo

<div align="center">

| Detection + Tracking | Counting Overlay |
|:---:|:---:|
| <img src="assets/tracking_demo.gif" width="380"/> | <img src="assets/counting_overlay.png" width="380"/> |

</div>

---

## Results

| Metric | Value |
|---|---|
| Avg. FPS (GPU) | `PLACEHOLDER` |
| Avg. FPS (CPU) | `PLACEHOLDER` |
| Test video length | `PLACEHOLDER` |
| Total vehicles counted | `PLACEHOLDER` |

---

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/roadsight-pro.git
cd roadsight-pro
pip install -r requirements.txt
```

---

## Usage

```bash
# Local run with display
python vehicle_tracker.py --video test5.mp4 --model yolo11n.pt

# Headless (Colab / server)
python vehicle_tracker.py --video test5.mp4 --headless --export-format json

# Force GPU
python vehicle_tracker.py --video test5.mp4 --device cuda:0
```

| Argument | Description | Default |
|---|---|---|
| `--video` | Input video path (required) | — |
| `--model` | YOLO model path/name | `yolo11n.pt` |
| `--output` | Output video path | `output.mp4` |
| `--conf` | Global confidence override | per-class |
| `--headless` | Run without display window | `False` |
| `--device` | `cuda:0` / `cpu` | auto |
| `--export-format` | `json` / `csv` / `none` | `json` |
| `--export-dir` | Export directory | `results` |

---

## Project Structure

```
roadsight-pro/
├── vehicle_tracker.py
├── README.md
├── PROJECT_REPORT.md
├── requirements.txt
├── LICENSE
├── .gitignore
├── results/
└── assets/
```

---

## Roadmap

- [ ] Line-crossing / zone-based counting
- [ ] Speed estimation
- [ ] RTSP / live stream support
- [ ] Unit tests
- [ ] Docker image

---

## References

- [Ultralytics YOLO11 Documentation](https://docs.ultralytics.com/models/yolo11/)
- Zhang, Y. et al. *ByteTrack: Multi-Object Tracking by Associating Every Detection Box*, 2022.

---

## License

[MIT](LICENSE)

---

<div align="center">

**`PLACEHOLDER — Your Name / GitHub / LinkedIn`**

</div>
