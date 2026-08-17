# Real-time Vehicle Tracking and Counting using YOLO + OpenCV

## Project Overview

This project uses **YOLO11** for real-time vehicle detection, tracking, and counting. It detects vehicles (cars, trucks, buses, motorcycles, and bicycles) from a video stream, tracks their movements across frames, and counts how many vehicles of each type are detected — with automatic correction for class-label flickering between frames.

The system works by processing each frame of the video, identifying vehicles, assigning them persistent track IDs, and keeping a running per-class count in real time.

## 📊 Sample Traffic Video

`PLACEHOLDER — test video file name, e.g. test5.mp4`

`PLACEHOLDER — link to sample input video`

## 🧠 AI Model (YOLO11)

The model used for vehicle detection is **YOLO11** (`yolo11n.pt` by default, configurable via `--model`). It detects and classifies vehicles into the following classes: car, truck, bus, motorcycle, and bicycle.

👉 `PLACEHOLDER — link to your trained/downloaded model weights, if hosted separately`

## 🛠️ How It Works

1. **Video Input:** A video file is processed frame by frame.
2. **Vehicle Detection:** YOLO11 detects vehicles within each frame, applying per-class confidence thresholds.
3. **Tracking & Counting:** ByteTrack assigns each detected vehicle a persistent ID across frames. If a track's predicted class changes between frames, the count is reconciled so the same vehicle is never counted twice under two classes.

## 💻 Tech Stack

- **Python:** YOLO11, OpenCV, NumPy
- **AI Model:** Ultralytics YOLO11
- **Tracking:** ByteTrack
- **Vehicle Counting:** Custom logic based on track IDs and reconciled class labels
- **Libraries:** `cv2`, `ultralytics`, `numpy`, `tqdm`

## 🚀 How to Run

1. Install Python libraries:
```bash
pip install -r requirements.txt
```

2. Place your input video in the project folder.

3. Run the script:
```bash
python vehicle_tracker.py --video test5.mp4 --model yolo11n.pt
```

4. The output will be saved as `output.mp4` and displayed in a window showing vehicle tracking and counts (use `--headless` to skip the display window).

**Sample Output**

`PLACEHOLDER — link or embedded preview of output_demo.mp4`

## Project Structure

```
roadsight-pro/
├── vehicle_tracker.py
├── README.md
├── PROJECT_REPORT.md
├── requirements.txt
├── LICENSE
└── .gitignore
```

## License

[MIT](LICENSE)
