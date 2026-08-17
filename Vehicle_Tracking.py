"""
Vehicle_Tracking.py
-------------------
Advanced real-time vehicle detection, classification, tracking, and counting
using YOLO + ByteTrack.

Features:
    - Cross-platform (no OS-specific dependencies)
    - Class-specific confidence thresholds
    - Robust track-ID -> class reconciliation (handles flickering predictions)
    - Bounded trail history (memory-safe for long videos)
    - Headless mode support (no display required, e.g. Colab / servers)
    - JSON/CSV export of final counts
    - Structured logging + graceful error handling
    - CLI configurable via argparse

Usage:
    python vehicle_tracker.py --video test5.mp4 --model yolo11n.pt --conf 0.5
    python vehicle_tracker.py --video test5.mp4 --headless --export-format json
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import random
import sys
from collections import defaultdict, deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Deque, Dict, Optional, Tuple

import cv2
import numpy as np
from ultralytics import YOLO

try:
    from tqdm import tqdm

    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False


# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

DEFAULT_VEHICLE_LABELS = {"car", "truck", "bus", "motorcycle", "bicycle"}

# Per-class confidence thresholds — smaller/harder-to-detect classes get a
# lower bar, larger/easier classes get a stricter one to reduce false positives.
DEFAULT_CLASS_THRESHOLDS: Dict[str, float] = {
    "car": 0.55,
    "truck": 0.50,
    "bus": 0.50,
    "motorcycle": 0.40,
    "bicycle": 0.35,
}

MAX_TRAIL_LENGTH = 40  # max points kept per object's movement trail


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("vehicle_tracker")


# --------------------------------------------------------------------------- #
# Data structures
# --------------------------------------------------------------------------- #

@dataclass
class TrackState:
    """Holds per-track-ID bookkeeping."""

    current_class: str
    color: Tuple[int, int, int]
    trail: Deque[Tuple[int, int]] = field(
        default_factory=lambda: deque(maxlen=MAX_TRAIL_LENGTH)
    )


# --------------------------------------------------------------------------- #
# Core tracker class
# --------------------------------------------------------------------------- #

class VehicleTracker:
    """Encapsulates detection, tracking, class-count reconciliation, and I/O."""

    def __init__(
        self,
        video_path: Path,
        model_path: str,
        output_path: Path,
        vehicle_labels: set = DEFAULT_VEHICLE_LABELS,
        class_thresholds: Dict[str, float] = None,
        headless: bool = False,
        device: Optional[str] = None,
    ) -> None:
        self.video_path = video_path
        self.output_path = output_path
        self.vehicle_labels = vehicle_labels
        self.class_thresholds = class_thresholds or DEFAULT_CLASS_THRESHOLDS
        self.headless = headless
        self.device = device

        self.model = self._load_model(model_path)
        self.cap = self._open_video(video_path)
        self.writer = self._build_writer(output_path)

        self.track_states: Dict[int, TrackState] = {}
        self.vehicle_counts: Dict[str, int] = defaultdict(int)

    # ----- setup helpers ---------------------------------------------------- #

    def _load_model(self, model_path: str) -> YOLO:
        try:
            model = YOLO(model_path)
            logger.info("Model loaded: %s", model_path)
            return model
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to load model '%s': %s", model_path, exc)
            sys.exit(1)

    def _open_video(self, video_path: Path) -> cv2.VideoCapture:
        if not video_path.exists():
            logger.error("Video file not found: %s", video_path)
            sys.exit(1)

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            logger.error("OpenCV could not open video: %s", video_path)
            sys.exit(1)

        logger.info("Video opened: %s", video_path)
        return cap

    def _build_writer(self, output_path: Path) -> cv2.VideoWriter:
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = self.cap.get(cv2.CAP_PROP_FPS) or 25.0

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

        if not writer.isOpened():
            logger.warning(
                "VideoWriter failed to open with mp4v codec; trying 'avc1' fallback."
            )
            fourcc = cv2.VideoWriter_fourcc(*"avc1")
            writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

        return writer

    # ----- core logic --------------------------------------------------------- #

    def _get_color_for_id(self, obj_id: int) -> Tuple[int, int, int]:
        random.seed(obj_id)  # deterministic color per ID across runs
        return (
            random.randint(60, 255),
            random.randint(60, 255),
            random.randint(60, 255),
        )

    def _reconcile_class(self, obj_id: int, label: str) -> None:
        """
        Updates vehicle_counts so that a track ID's class flip (a common
        YOLO flickering artifact) doesn't inflate the totals: the previous
        class count is decremented and the new one incremented.
        """
        if obj_id not in self.track_states:
            self.track_states[obj_id] = TrackState(
                current_class=label, color=self._get_color_for_id(obj_id)
            )
            self.vehicle_counts[label] += 1
            return

        state = self.track_states[obj_id]
        if state.current_class != label:
            self.vehicle_counts[state.current_class] -= 1
            self.vehicle_counts[label] += 1
            state.current_class = label

    def _passes_threshold(self, label: str, conf: float) -> bool:
        threshold = self.class_thresholds.get(label, 0.5)
        return conf >= threshold

    def _draw_frame(self, frame: np.ndarray, results) -> np.ndarray:
        if results.boxes.id is None:
            return frame

        boxes = results.boxes.xyxy.cpu().numpy()
        ids = results.boxes.id.int().cpu().tolist()
        classes = results.boxes.cls.int().cpu().tolist()
        confs = results.boxes.conf.cpu().tolist()

        for box, obj_id, cls_idx, conf in zip(boxes, ids, classes, confs):
            label = self.model.names[int(cls_idx)]

            if label not in self.vehicle_labels or not self._passes_threshold(label, conf):
                continue

            self._reconcile_class(obj_id, label)
            state = self.track_states[obj_id]

            x1, y1, x2, y2 = map(int, box)
            color = state.color

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(
                frame,
                f"{label.upper()} ID:{obj_id} ({conf:.2f})",
                (x1, max(y1 - 8, 0)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                color,
                2,
            )

            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            state.trail.append((cx, cy))
            for i in range(1, len(state.trail)):
                cv2.line(frame, state.trail[i - 1], state.trail[i], color, 2)

        self._draw_counts_overlay(frame)
        return frame

    def _draw_counts_overlay(self, frame: np.ndarray) -> None:
        y_offset = 35
        for vehicle_type, count in sorted(self.vehicle_counts.items()):
            if count <= 0:
                continue
            cv2.putText(
                frame,
                f"{vehicle_type.upper()}: {count}",
                (20, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 0, 255),
                3,
            )
            y_offset += 35

    # ----- main loop ------------------------------------------------------ #

    def run(self) -> Dict[str, int]:
        total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)) or None
        progress = (
            tqdm(total=total_frames, desc="Processing", unit="frame")
            if TQDM_AVAILABLE
            else None
        )

        logger.info("Tracking started (headless=%s)...", self.headless)

        try:
            while True:
                ok, frame = self.cap.read()
                if not ok:
                    break

                results = self.model.track(
                    frame,
                    persist=True,
                    conf=min(self.class_thresholds.values()),
                    verbose=False,
                    device=self.device,
                )[0]

                frame = self._draw_frame(frame, results)
                self.writer.write(frame)

                if not self.headless:
                    cv2.imshow("Vehicle Tracking + Counting", frame)
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        logger.info("Interrupted by user ('q' pressed).")
                        break

                if progress:
                    progress.update(1)

        except KeyboardInterrupt:
            logger.warning("Interrupted via Ctrl+C.")
        finally:
            self._cleanup()
            if progress:
                progress.close()

        logger.info("Done. Output saved to: %s", self.output_path)
        return dict(self.vehicle_counts)

    def _cleanup(self) -> None:
        self.cap.release()
        self.writer.release()
        if not self.headless:
            cv2.destroyAllWindows()


# --------------------------------------------------------------------------- #
# Export helpers
# --------------------------------------------------------------------------- #

def export_results(
    counts: Dict[str, int], output_dir: Path, fmt: str, source_video: Path
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    if fmt == "json":
        payload = {"source_video": str(source_video), "counts": counts}
        out_file = output_dir / "vehicle_counts.json"
        out_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        logger.info("Counts exported to %s", out_file)

    elif fmt == "csv":
        out_file = output_dir / "vehicle_counts.csv"
        with out_file.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["vehicle_class", "count"])
            for cls, count in counts.items():
                writer.writerow([cls, count])
        logger.info("Counts exported to %s", out_file)


# --------------------------------------------------------------------------- #
# CLI entry point
# --------------------------------------------------------------------------- #

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Advanced vehicle detection, tracking, and counting with YOLO."
    )
    parser.add_argument("--video", type=str, required=True, help="Path to input video.")
    parser.add_argument(
        "--model", type=str, default="yolo11n.pt", help="Path or name of YOLO model."
    )
    parser.add_argument(
        "--output", type=str, default="output.mp4", help="Path to output video."
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=None,
        help="Global confidence threshold override (applies to all classes).",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run without a display window (required for Colab/servers).",
    )
    parser.add_argument(
        "--device",
        type=str,
        default=None,
        help="Inference device, e.g. 'cuda:0' or 'cpu'. Auto-detected if omitted.",
    )
    parser.add_argument(
        "--export-format",
        type=str,
        choices=["json", "csv", "none"],
        default="json",
        help="Format for exporting final vehicle counts.",
    )
    parser.add_argument(
        "--export-dir",
        type=str,
        default="results",
        help="Directory to write exported count files.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    class_thresholds = dict(DEFAULT_CLASS_THRESHOLDS)
    if args.conf is not None:
        class_thresholds = {cls: args.conf for cls in class_thresholds}

    tracker = VehicleTracker(
        video_path=Path(args.video),
        model_path=args.model,
        output_path=Path(args.output),
        class_thresholds=class_thresholds,
        headless=args.headless,
        device=args.device,
    )

    final_counts = tracker.run()

    logger.info("Final counts: %s", final_counts)

    if args.export_format != "none":
        export_results(
            final_counts, Path(args.export_dir), args.export_format, Path(args.video)
        )


if __name__ == "__main__":
    main()
