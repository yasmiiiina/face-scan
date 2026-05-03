import cv2
import time
import numpy as np
import csv
import threading
import queue
from datetime import datetime

from face_detection import FaceDetector
from signal_extraction import SignalExtractor
from signal_processing import SignalProcessor
from feature_engineering import FeatureExtractor
from scoring import ScoreCalculator
from classification import Classifier
from pdf_report import PDFReport

class RPPGSystem:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.detector = FaceDetector()
        self.extractor = SignalExtractor()
        self.processor = SignalProcessor()
        self.features = FeatureExtractor()
        self.scorer = ScoreCalculator()
        self.classifier = Classifier()
        
        self.fps_target = 30
        self.acquisition_time = 35 # seconds
        self.buffer_size = self.acquisition_time * self.fps_target
        self.raw_signal_buffer = []
        self.time_buffer = []
        
        # Files d'attente pour le multithreading
        self.frame_queue = queue.Queue(maxsize=3)
        self.result_queue = queue.Queue(maxsize=3)
        self.running = True
        
        self.csv_file = open("results.csv", "w", newline="")
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(["Timestamp", "HR", "HRV", "RR", "Score", "Classification"])
        
        # Biomarkers
        self.current_hr = 0.0
        self.current_hrv = 0.0
        self.current_rr = 0.0
        self.current_score = 0.0
        self.current_state = "Init"
        self.current_state_color = (150, 150, 150)
        self.current_sqi_warning = False
        self.current_stress = ("Calcul...", (150, 150, 150))
        self.current_stress_idx = 0.0
        
        # Placeholders
        self.current_bp = "120/80" # Placeholder based on pulse transit
        self.current_workload = 0.0
        self.current_bmi = 22.5 # Input-based placeholder
        
        self.filtered_signal = []
        
        # UI State
        self.is_acquiring = True

    def camera_thread(self):
        """Thread 1: Capture vidéo fluide."""
        while self.running:
            ret, frame = self.cap.read()
            if not ret: continue
            
            # Ne garder que la dernière frame pour éviter le retard
            if self.frame_queue.full():
                try:
                    self.frame_queue.get_nowait()
                except queue.Empty:
                    pass
            self.frame_queue.put((time.time(), frame))

    def processing_thread(self):
        """Thread 2: Inférence Mediapipe et Traitement de signal lourd."""
        while self.running:
            try:
                timestamp, frame = self.frame_queue.get(timeout=0.1)
            except queue.Empty:
                continue
                
            face_found, rois, display_frame, bbox = self.detector.get_rois(frame)
            
            if face_found:
                green_val, low_light = self.extractor.extract_green_from_rois(frame, rois)
                self.current_sqi_warning = low_light
                
                self.raw_signal_buffer.append(green_val)
                self.time_buffer.append(timestamp)
                
                if len(self.raw_signal_buffer) > self.buffer_size:
                    self.raw_signal_buffer.pop(0)
                    self.time_buffer.pop(0)
                    
                elapsed = self.time_buffer[-1] - self.time_buffer[0]
                fps = len(self.time_buffer) / elapsed if elapsed > 0 else 30.0
                
                if len(self.raw_signal_buffer) >= int(fps * 5):
                    c_sig, r_sig = self.processor.process(self.raw_signal_buffer, fps)
                    self.filtered_signal = c_sig
                    
                    hr, hrv = self.features.extract_features(c_sig, fps)
                    rr = self.features.extract_rr(r_sig, fps)
                    
                    self.current_hr = hr
                    self.current_hrv = hrv
                    self.current_rr = rr
                    self.current_score = self.scorer.count_score(hr, hrv)
                    self.current_state, self.current_state_color = self.classifier.get_bpm_state(hr)
                    self.current_stress = self.classifier.get_stress_level(hrv)
                    
                    # Compute Workload and Stress Index placeholders
                    systolic = 120 # From BP placeholder
                    self.current_workload = (hr * systolic) / 100.0 if hr > 0 else 0.0
                    
                    # Simple stress index mapping: 0 to 100 based on HRV
                    if hrv > 0:
                        self.current_stress_idx = max(0, min(100, 100 - (hrv / 100.0) * 100))
                    else:
                        self.current_stress_idx = 0.0
                    
                    if len(self.time_buffer) % int(max(1, fps)) == 0:
                        state_score = self.classifier.classify_state_by_score(self.current_score)
                        t_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        self.csv_writer.writerow([t_str, f"{hr:.2f}", f"{hrv:.2f}", f"{rr:.2f}", f"{self.current_score:.2f}", state_score])
                        self.csv_file.flush()
                        
            # Transfert du frame préparé au main thread
            if self.result_queue.full():
                try:
                    self.result_queue.get_nowait()
                except queue.Empty:
                    pass
            self.result_queue.put((display_frame, face_found, bbox if face_found else None, fps if face_found else 30.0))

    def run(self):
        """Main Thread: UI (OpenCV imshow DOIT tourner sur le Main Thread)."""
        t_cam = threading.Thread(target=self.camera_thread)
        t_proc = threading.Thread(target=self.processing_thread)
        t_cam.start()
        t_proc.start()
        
        while self.running:
            try:
                display_frame, face_found, bbox, fps = self.result_queue.get(timeout=0.1)
            except queue.Empty:
                continue
                
            buffer_ratio = len(self.raw_signal_buffer) / self.buffer_size if self.buffer_size > 0 else 0
            
            # Determine state
            if buffer_ratio < 1.0:
                self.is_acquiring = True
            else:
                self.is_acquiring = False
            
            if face_found:
                # Face ID UI Overlay (Coins ciblés)
                if bbox is not None:
                    x1, y1, x2, y2 = bbox
                    c_len = max(10, int((x2 - x1) * 0.15)) # 15% de largeur
                    
                    # Color based on state
                    if self.is_acquiring:
                        color = (0, 165, 255) # Orange during acquisition
                    else:
                        color = (0, 255, 100) # Vert fluo médical
                    thick = 3
                    
                    # Top-Left
                    cv2.line(display_frame, (x1, y1), (x1 + c_len, y1), color, thick, cv2.LINE_AA)
                    cv2.line(display_frame, (x1, y1), (x1, y1 + c_len), color, thick, cv2.LINE_AA)
                    # Top-Right
                    cv2.line(display_frame, (x2, y1), (x2 - c_len, y1), color, thick, cv2.LINE_AA)
                    cv2.line(display_frame, (x2, y1), (x2, y1 + c_len), color, thick, cv2.LINE_AA)
                    # Bottom-Left
                    cv2.line(display_frame, (x1, y2), (x1 + c_len, y2), color, thick, cv2.LINE_AA)
                    cv2.line(display_frame, (x1, y2), (x1, y2 - c_len), color, thick, cv2.LINE_AA)
                    # Bottom-Right
                    cv2.line(display_frame, (x2, y2), (x2 - c_len, y2), color, thick, cv2.LINE_AA)
                    cv2.line(display_frame, (x2, y2), (x2, y2 - c_len), color, thick, cv2.LINE_AA)
                    
                # Dashboard
                self.draw_dashboard(display_frame, buffer_ratio, fps)
                                    
                if len(self.filtered_signal) > 0 and not self.is_acquiring:
                    display_len = min(len(self.filtered_signal), int(fps * 4))
                    self.draw_graph(display_frame, self.filtered_signal[-display_len:])
            else:
                self.draw_dashboard(display_frame, buffer_ratio, fps, face_missing=True)
                                    
            cv2.imshow("PEREN AI - Medical SaaS", display_frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                self.running = False
                break
            elif key == ord('s'):
                print("Generation du PDF en cours...")
                self.csv_file.flush() # Force write before reading
                reporter = PDFReport()
                reporter.generate()
                
        self.running = False
        t_cam.join()
        t_proc.join()
        self.cap.release()
        cv2.destroyAllWindows()
        self.csv_file.close()

    def draw_dashboard(self, frame, buffer_ratio, fps, face_missing=False):
        h, w = frame.shape[:2]
        panel_w = 400
        
        overlay = frame.copy()
        # Dark Theme Background for Dashboard Panel
        cv2.rectangle(overlay, (w - panel_w, 0), (w, h), (20, 20, 25), -1)
        cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)
        
        # Digital Twin Concept / Camera feed separation line
        cv2.line(frame, (w - panel_w, 0), (w - panel_w, h), (50, 50, 60), 2)
        
        x_m = w - panel_w + 20
        y_cursor = 40
        
        # Header
        cv2.putText(frame, "PEREN AI", (x_m, y_cursor), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, "Medical SaaS Scanner", (x_m, y_cursor + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1, cv2.LINE_AA)
        cv2.line(frame, (x_m, y_cursor + 40), (w - 20, y_cursor + 40), (80, 80, 80), 1)
        
        y_cursor += 70
        
        # Acquisition Phase
        if self.is_acquiring:
            cv2.putText(frame, "PHASE D'ACQUISITION", (x_m, y_cursor), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 1, cv2.LINE_AA)
            y_cursor += 25
            cv2.putText(frame, "Veuillez garder une position de repos", (x_m, y_cursor), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1, cv2.LINE_AA)
            cv2.putText(frame, "pendant 35 a 60 secondes.", (x_m, y_cursor + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1, cv2.LINE_AA)
            
            y_cursor += 45
            # Progress Bar
            bar_w = panel_w - 40
            cv2.rectangle(frame, (x_m, y_cursor), (x_m + bar_w, y_cursor + 8), (50, 50, 50), -1)
            if buffer_ratio > 0:
                cv2.rectangle(frame, (x_m, y_cursor), (x_m + int(bar_w * buffer_ratio), y_cursor + 8), (0, 200, 255), -1)
            
            # Digital Twin Placeholder (During Acquisition)
            y_cursor += 40
            cv2.rectangle(frame, (x_m, y_cursor), (w - 20, y_cursor + 180), (30, 30, 35), -1)
            cv2.rectangle(frame, (x_m, y_cursor), (w - 20, y_cursor + 180), (70, 70, 80), 1)
            cv2.putText(frame, "[ Jumeau Digital / Digital Twin ]", (x_m + 30, y_cursor + 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 110), 1, cv2.LINE_AA)
            cv2.putText(frame, "Scan en cours...", (x_m + 100, y_cursor + 115), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (100, 100, 110), 1, cv2.LINE_AA)
            
        else:
            # Metrics 3x2 Grid
            cv2.putText(frame, "BIOMARKERS", (x_m, y_cursor), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1, cv2.LINE_AA)
            y_cursor += 20
            
            grid_w = (panel_w - 60) // 2
            grid_h = 75
            
            metrics = [
                {"name": "Blood Pressure", "value": self.current_bp, "unit": "mmHg", "status": (255, 100, 100) if self.current_bp == "120/80" else (100, 200, 255)}, # Blue normally
                {"name": "Heart Rate", "value": f"{self.current_hr:.0f}" if not face_missing else "--", "unit": "BPM", "status": self.current_state_color},
                {"name": "Breathing Rate", "value": f"{self.current_rr:.1f}" if not face_missing else "--", "unit": "RPM", "status": (255, 150, 50) if self.current_rr > 20 else (100, 255, 100)},
                {"name": "Card. Workload", "value": f"{self.current_workload:.1f}" if not face_missing else "--", "unit": "%", "status": (100, 255, 100)},
                {"name": "Stress Index", "value": f"{self.current_stress_idx:.0f}" if not face_missing else "--", "unit": "/100", "status": self.current_stress[1]},
                {"name": "BMI", "value": f"{self.current_bmi:.1f}", "unit": "kg/m2", "status": (200, 200, 200)}
            ]
            
            for i, metric in enumerate(metrics):
                col = i % 2
                row = i // 2
                x_card = x_m + col * (grid_w + 20)
                y_card = y_cursor + row * (grid_h + 15)
                
                # Card Background
                cv2.rectangle(frame, (x_card, y_card), (x_card + grid_w, y_card + grid_h), (30, 30, 35), -1)
                # Status dot
                cv2.circle(frame, (x_card + grid_w - 15, y_card + 15), 4, metric["status"], -1, cv2.LINE_AA)
                
                # Metric Name
                cv2.putText(frame, metric["name"], (x_card + 10, y_card + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1, cv2.LINE_AA)
                # Metric Value
                cv2.putText(frame, metric["value"], (x_card + 10, y_card + 50), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1, cv2.LINE_AA)
                # Metric Unit
                cv2.putText(frame, metric["unit"], (x_card + 10, y_card + 65), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (120, 120, 120), 1, cv2.LINE_AA)

        # Bottom section: Warnings and Footer
        y_bottom = h - 60
        
        if self.current_sqi_warning:
            cv2.rectangle(frame, (x_m, y_bottom - 35), (w - 20, y_bottom - 10), (0, 0, 200), -1)
            cv2.putText(frame, "LOW LIGHT - MOVE TO BRIGHTER AREA", (x_m + 15, y_bottom - 18), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1, cv2.LINE_AA)
            
        cv2.line(frame, (x_m, y_bottom), (w - 20, y_bottom), (80, 80, 80), 1)
        
        # Disclaimer
        disclaimer_text = "Precision a valider par des modeles IA entraines sur un jeu de donnees massif."
        cv2.putText(frame, disclaimer_text, (x_m, y_bottom + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.28, (120, 120, 120), 1, cv2.LINE_AA)
        
        cv2.putText(frame, "Traitement On-Device | Video Sans-Contact", (x_m, y_bottom + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (150, 150, 150), 1, cv2.LINE_AA)
        cv2.putText(frame, f"FPS: {fps:.1f} | 's': Export", (x_m, y_bottom + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (100, 100, 100), 1, cv2.LINE_AA)

    def draw_graph(self, frame, signal, width=380, height=80):
        # Anchor graph to the bottom left part of the screen, below camera feed
        h, w = frame.shape[:2]
        x_offset = 20
        y_offset = h - height - 40
        
        if len(signal) < 2: return
        s_min, s_max = np.min(signal), np.max(signal)
        if s_max - s_min < 1e-5:
            normalized_signal = np.zeros(len(signal))
        else:
            normalized_signal = (signal - s_min) / (s_max - s_min) * height
            
        window = min(5, len(normalized_signal))
        smooth_signal = np.convolve(normalized_signal, np.ones(window)/window, mode='valid') if window > 2 else normalized_signal
            
        cv2.rectangle(frame, (x_offset, y_offset), (x_offset + width, y_offset + height), (30, 30, 35), -1)
        cv2.rectangle(frame, (x_offset, y_offset), (x_offset + width, y_offset + height), (60, 60, 70), 1)
        
        for i in range(1, 4):
            y_line = y_offset + int((i / 4.0) * height)
            cv2.line(frame, (x_offset, y_line), (x_offset + width, y_line), (50, 50, 60), 1, cv2.LINE_AA)
            
        cv2.putText(frame, "PULSE WAVEFORM (PPG)", (x_offset, y_offset - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1, cv2.LINE_AA)
        
        step_x = width / max(1, len(smooth_signal) - 1)
        pts = []
        for i, s_val in enumerate(smooth_signal):
            pts.append((int(x_offset + i * step_x), int(y_offset + height - s_val)))
            
        pts = np.array(pts, np.int32).reshape((-1, 1, 2))
        cv2.polylines(frame, [pts], False, (0, 255, 150), 2, cv2.LINE_AA)

if __name__ == "__main__":
    sys = RPPGSystem()
    sys.run()
