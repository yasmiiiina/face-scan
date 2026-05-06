import os
import uuid
from datetime import datetime

import cv2
import pandas as pd
from flask import Flask, jsonify, render_template, request, send_from_directory

from classification import Classifier
from face_detection import FaceDetector
from feature_engineering import FeatureExtractor
from pdf_report import PDFReport
from scoring import ScoreCalculator
from signal_extraction import SignalExtractor
from signal_processing import SignalProcessor


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

for folder in (UPLOAD_DIR, RESULTS_DIR, REPORTS_DIR):
    os.makedirs(folder, exist_ok=True)


app = Flask(__name__)


def _safe_fps(fps_value):
    if fps_value is None or fps_value <= 0 or fps_value > 240:
        return 30.0
    return float(fps_value)


def run_rppg_pipeline(video_path, scan_id):
    detector = FaceDetector()
    extractor = SignalExtractor()
    processor = SignalProcessor()
    features = FeatureExtractor()
    scorer = ScoreCalculator()
    classifier = Classifier()

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError("Impossible d'ouvrir la video envoyee.")

    fps = _safe_fps(cap.get(cv2.CAP_PROP_FPS))
    raw_signal = []
    times = []
    rows = []
    frame_idx = 0
    stride = max(1, int(round(fps)))

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        face_ok, rois, _, _ = detector.get_rois(frame)
        if not face_ok or not rois:
            frame_idx += 1
            continue

        green_val, low_light = extractor.extract_green_from_rois(frame, rois)
        if low_light or green_val <= 0:
            frame_idx += 1
            continue

        raw_signal.append(float(green_val))
        times.append(frame_idx / fps)

        # Produire des mesures periodiques pour obtenir un historique utilisable dans le PDF.
        if len(raw_signal) >= int(10 * fps) and frame_idx % stride == 0:
            try:
                c_signal, r_signal = processor.process(raw_signal, fps)
                hr, hrv = features.extract_features(c_signal, fps)
                rr = features.extract_rr(r_signal, fps)
                score = scorer.count_score(hr, hrv)
                rows.append(
                    {
                        "timestamp_s": round(times[-1], 2),
                        "HR": round(hr, 2),
                        "HRV": round(hrv, 2),
                        "RR": round(rr, 2),
                        "Score": round(score, 2),
                    }
                )
            except Exception:
                # Ignorer les echantillons invalides intermediaires; la sortie finale controle la validite.
                pass

        frame_idx += 1

    cap.release()

    if len(raw_signal) < int(10 * fps):
        raise RuntimeError("Signal insuffisant: visage non detecte assez longtemps.")

    c_signal, r_signal = processor.process(raw_signal, fps)
    hr, hrv = features.extract_features(c_signal, fps)
    rr = features.extract_rr(r_signal, fps)
    score = scorer.count_score(hr, hrv)
    wellness_state = classifier.classify_state_by_score(score)
    bpm_state, _ = classifier.get_bpm_state(hr)
    stress_state, _ = classifier.get_stress_level(hrv)

    if not rows:
        rows.append(
            {
                "timestamp_s": 0.0,
                "HR": round(hr, 2),
                "HRV": round(hrv, 2),
                "RR": round(rr, 2),
                "Score": round(score, 2),
            }
        )
        rows.append(
            {
                "timestamp_s": 1.0,
                "HR": round(hr, 2),
                "HRV": round(hrv, 2),
                "RR": round(rr, 2),
                "Score": round(score, 2),
            }
        )

    csv_path = os.path.join(RESULTS_DIR, f"results_{scan_id}.csv")
    pd.DataFrame(rows).to_csv(csv_path, index=False)

    report_path = os.path.join(REPORTS_DIR, f"PEREN_Report_{scan_id}.pdf")
    report = PDFReport(csv_file=csv_path)
    generated = report.generate(output_path=report_path)
    if not generated:
        raise RuntimeError("Generation du rapport PDF echouee.")

    return {
        "scan_id": scan_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "hr": round(hr, 2),
        "hrv": round(hrv, 2),
        "rr": round(rr, 2),
        "score": round(score, 2),
        "wellness_state": wellness_state,
        "bpm_state": bpm_state,
        "stress_state": stress_state,
        "pdf_filename": os.path.basename(report_path),
    }


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/process_scan", methods=["POST"])
def process_scan():
    if "video" not in request.files:
        return jsonify({"status": "error", "message": "Aucun fichier video recu."}), 400

    video_file = request.files["video"]
    if not video_file or video_file.filename == "":
        return jsonify({"status": "error", "message": "Nom de fichier video invalide."}), 400

    scan_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:8]
    extension = os.path.splitext(video_file.filename)[1] or ".webm"
    upload_path = os.path.join(UPLOAD_DIR, f"{scan_id}{extension}")
    video_file.save(upload_path)

    try:
        result = run_rppg_pipeline(upload_path, scan_id)
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc), "scan_id": scan_id}), 500

    return jsonify(
        {
            "status": "success",
            "scan_id": result["scan_id"],
            "metrics": {
                "hr": result["hr"],
                "hrv": result["hrv"],
                "rr": result["rr"],
                "score": result["score"],
            },
            "states": {
                "wellness": result["wellness_state"],
                "heart_rate": result["bpm_state"],
                "stress": result["stress_state"],
            },
            "pdf_url": f"/reports/{result['pdf_filename']}",
            "timestamp": result["timestamp"],
        }
    )


@app.route("/reports/<path:filename>", methods=["GET"])
def download_report(filename):
    return send_from_directory(REPORTS_DIR, filename, as_attachment=True)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port, debug=True)
