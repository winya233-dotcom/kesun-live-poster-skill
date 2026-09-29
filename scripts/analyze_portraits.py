from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

try:
    import mediapipe as mp
except ImportError:  # MediaPipe currently has no wheel for some Python versions.
    mp = None


SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = SKILL_DIR / "assets" / "kesun-blue-manifest.json"
MODEL_DIR = SKILL_DIR / "assets" / "models"


def runtime_model(name: str) -> Path:
    """MediaPipe's Windows loader can fail on non-ASCII installation paths."""
    source = MODEL_DIR / name
    target_dir = Path(tempfile.gettempdir()) / "live-poster-generator-models"
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / name
    if not target.exists() or target.stat().st_size != source.stat().st_size:
        shutil.copy2(source, target)
    return target


def load_trimmed(path: Path, output_path: Path) -> tuple[Image.Image, np.ndarray, tuple[int, int, int, int]]:
    image = Image.open(path).convert("RGBA")
    box = image.getchannel("A").getbbox()
    if box is None:
        raise RuntimeError(f"No visible pixels in {path}")
    trimmed = image.crop(box)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    trimmed.save(output_path)
    rgb = Image.new("RGB", trimmed.size, (238, 241, 246))
    rgb.paste(trimmed, mask=trimmed.getchannel("A"))
    return trimmed, np.asarray(rgb), box


def detect_face_opencv(rgb: np.ndarray) -> dict[str, object]:
    cascade_path = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(str(cascade_path))
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    faces = detector.detectMultiScale(gray, scaleFactor=1.08, minNeighbors=5, minSize=(40, 40))
    if len(faces) == 0:
        raise RuntimeError("OpenCV did not detect a face")
    x, y, width, height = max(faces, key=lambda box: int(box[2]) * int(box[3]))
    return {
        "x": int(x),
        "y": int(y),
        "width": int(width),
        "height": int(height),
        "keypoints": [],
        "detector": "opencv-haar",
    }


def detect_face(rgb: np.ndarray) -> dict[str, object]:
    if mp is None:
        return detect_face_opencv(rgb)
    options = mp.tasks.vision.FaceDetectorOptions(
        base_options=mp.tasks.BaseOptions(
            model_asset_path=str(runtime_model("blaze_face_short_range.tflite"))
        ),
        min_detection_confidence=0.45,
    )
    with mp.tasks.vision.FaceDetector.create_from_options(options) as detector:
        result = detector.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb))
    if not result.detections:
        raise RuntimeError("MediaPipe did not detect a face")
    detection = max(result.detections, key=lambda d: d.bounding_box.width * d.bounding_box.height)
    box = detection.bounding_box
    return {
        "x": int(box.origin_x),
        "y": int(box.origin_y),
        "width": int(box.width),
        "height": int(box.height),
        "keypoints": [{"x": float(p.x), "y": float(p.y)} for p in detection.keypoints],
        "detector": "mediapipe",
    }


def detect_pose(rgb: np.ndarray) -> dict[str, object] | None:
    if mp is None:
        return None
    options = mp.tasks.vision.PoseLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(
            model_asset_path=str(runtime_model("pose_landmarker_lite.task"))
        ),
        running_mode=mp.tasks.vision.RunningMode.IMAGE,
        min_pose_detection_confidence=0.35,
        min_pose_presence_confidence=0.35,
    )
    with mp.tasks.vision.PoseLandmarker.create_from_options(options) as detector:
        result = detector.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb))
    if not result.pose_landmarks:
        return None
    points = result.pose_landmarks[0]
    width, height = rgb.shape[1], rgb.shape[0]

    def point(index: int) -> dict[str, float]:
        item = points[index]
        return {
            "x": round(float(item.x) * width, 2),
            "y": round(float(item.y) * height, 2),
            "visibility": round(float(item.visibility or 0), 4),
        }

    return {
        "left_shoulder": point(11),
        "right_shoulder": point(12),
        "left_elbow": point(13),
        "right_elbow": point(14),
        "left_hip": point(23),
        "right_hip": point(24),
    }


def eye_y(face: dict[str, object], image_height: int) -> float:
    keypoints = face["keypoints"]
    if len(keypoints) >= 2:
        return ((keypoints[0]["y"] + keypoints[1]["y"]) / 2) * image_height
    return float(face["y"]) + float(face["height"]) * 0.43


def place(metrics: dict[str, object], face_height: float, center_x: float, target_eye_y: float) -> dict[str, object]:
    face = metrics["face"]
    scale = face_height / float(face["height"])
    width = float(metrics["width"]) * scale
    height = float(metrics["height"]) * scale
    face_center_x = (float(face["x"]) + float(face["width"]) / 2) * scale
    left = center_x - face_center_x
    top = target_eye_y - float(metrics["eye_y"]) * scale
    return {
        "asset": metrics["trimmed_asset"],
        "left": round(left, 1),
        "top": round(top, 1),
        "width": round(width, 1),
        "height": round(height, 1),
        "center_x": round(left + width / 2, 1),
        "center_y": round(top + height / 2, 1),
        "face_box": {
            "left": round(left + float(face["x"]) * scale, 1),
            "top": round(top + float(face["y"]) * scale, 1),
            "width": round(float(face["width"]) * scale, 1),
            "height": round(float(face["height"]) * scale, 1),
        },
    }


def intersects(a: dict[str, float], b: dict[str, float]) -> bool:
    return not (
        a["left"] + a["width"] <= b["left"]
        or b["left"] + b["width"] <= a["left"]
        or a["top"] + a["height"] <= b["top"]
        or b["top"] + b["height"] <= a["top"]
    )


def label_height(text: str, size: float, tracking: float, padding: float) -> float:
    return len(text) * size + max(0, len(text) - 1) * tracking + padding * 2


def make_labels(people: list[dict[str, object]], canvas_width: int, top: float, style: dict[str, object]) -> list[dict[str, object]]:
    factor = canvas_width / 1080
    name_w = float(style["name_width"]) * factor
    role_w = float(style["role_width"]) * factor
    labels: list[dict[str, object]] = []
    count = len(people)
    if count == 1:
        pairs = [(canvas_width - (name_w + role_w + 63 * factor), "right")]
    elif count == 2:
        pairs = [(65 * factor, "left"), (877 * factor, "right")]
    else:
        pairs = [(35 * factor, "left"), (canvas_width / 2 + 85 * factor, "right"), (canvas_width - 203 * factor, "right")]

    for person, (x, side) in zip(people, pairs):
        name = str(person["name"])
        role = str(person["role"])
        if side == "left":
            role_x, name_x = x, x + role_w - 2 * factor
        else:
            name_x, role_x = x, x + name_w - 2 * factor
        labels.extend([
            {
                "person_id": person["id"], "kind": "name", "text": name,
                "left": round(name_x, 1), "top": round(top + 48 * factor, 1),
                "width": round(name_w, 1),
                "height": round(label_height(name, float(style["name_font_size"]) * factor, float(style["name_tracking"]) * factor, float(style["vertical_padding"]) * factor), 1),
            },
            {
                "person_id": person["id"], "kind": "role", "text": role,
                "left": round(role_x, 1), "top": round(top, 1),
                "width": round(role_w, 1),
                "height": round(label_height(role, float(style["role_font_size"]) * factor, float(style["role_tracking"]) * factor, float(style["vertical_padding"]) * factor), 1),
            },
        ])
    return labels


def build_layout(template: dict[str, object], people: list[dict[str, object]], metrics: dict[str, object], qa: dict[str, object], style: dict[str, object]) -> dict[str, object]:
    width, height = template["canvas"]
    mode = {1: "single", 2: "double", 3: "triple"}[len(people)]
    rule = template["portrait_layout"][mode]
    centers = [float(value) for value in rule["face_centers_x"]]
    face_height = float(rule["face_height"])
    eye_line = float(rule["eye_y"])
    safe_min = float(qa["outer_margin_1080"][0]) * width / 1080
    max_span = float(qa["max_visible_span_ratio"]) * width

    for _ in range(30):
        placements = [place(metrics[p["id"]], face_height, centers[i], eye_line) for i, p in enumerate(people)]
        left = min(float(p["left"]) for p in placements)
        right = max(float(p["left"]) + float(p["width"]) for p in placements)
        if left >= safe_min and width - right >= safe_min and right - left <= max_span:
            break
        face_height *= 0.975

    labels = make_labels(people, width, float(template["label_top"]), style)
    collisions: list[str] = []
    expansion = float(qa["face_exclusion_expansion"])
    for person, placement in zip(people, placements):
        face = placement["face_box"]
        expanded = {
            "left": face["left"] - face["width"] * expansion,
            "top": face["top"] - face["height"] * expansion,
            "width": face["width"] * (1 + expansion * 2),
            "height": face["height"] * (1 + expansion * 2),
        }
        for label in labels:
            if intersects(expanded, label):
                collisions.append(f"{person['id']}:{label['person_id']}:{label['kind']}")

    left = min(float(p["left"]) for p in placements)
    right = max(float(p["left"]) + float(p["width"]) for p in placements)
    edge_ok = left >= safe_min and width - right >= safe_min and right - left <= max_span
    return {
        "canvas": {"width": width, "height": height},
        "face_height": round(face_height, 1),
        "eye_y": eye_line,
        "people": {person["id"]: placement for person, placement in zip(people, placements)},
        "labels": labels,
        "checks": {
            "left_margin": round(left, 1),
            "right_margin": round(width - right, 1),
            "visible_span_ratio": round((right - left) / width, 4),
            "collisions": collisions,
            "passes": edge_ok and not collisions,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="MediaPipe/OpenCV portrait layout analysis")
    parser.add_argument("request", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--allow-fail", action="store_true")
    args = parser.parse_args()

    request = json.loads(args.request.read_text(encoding="utf-8"))
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    people = request.get("people", [])
    if not 1 <= len(people) <= 3:
        raise ValueError("The blue template supports one to three people")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    metrics: dict[str, object] = {}
    for person in people:
        person_id = person["id"]
        source = Path(person.get("cutout_path") or person["portrait_path"])
        trimmed_path = args.output_dir / f"{person_id}-trimmed.png"
        trimmed, rgb, alpha_box = load_trimmed(source, trimmed_path)
        face = detect_face(rgb)
        metrics[person_id] = {
            "source": str(source.resolve()),
            "trimmed_asset": str(trimmed_path.resolve()),
            "alpha_box": list(alpha_box),
            "width": trimmed.width,
            "height": trimmed.height,
            "face": face,
            "eye_y": round(eye_y(face, trimmed.height), 2),
            "pose": detect_pose(rgb),
        }

    template_ids = ["poster"]
    if request["suite_type"] == "enterprise_wechat":
        template_ids.append("enterprise_cover_1080")
    else:
        template_ids.append("wechat_channels_cover")

    layouts = {}
    failed = []
    for template_id in template_ids:
        layout = build_layout(
            manifest["templates"][template_id], people, metrics,
            manifest["qa"], manifest["label_style"],
        )
        layouts[template_id] = layout
        if not layout["checks"]["passes"]:
            failed.append(template_id)

    output = args.output_dir / "portrait-layout.json"
    output.write_text(json.dumps({"metrics": metrics, "layouts": layouts}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(output.resolve())
    if failed and not args.allow_fail:
        print("Failed layouts: " + ", ".join(failed))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
