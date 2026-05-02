import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import os
import urllib.request

class ROITracker:
    def __init__(self, alpha=0.3):
        self.alpha = alpha
        self.smoothed_pts = None

    def update(self, current_pts):
        if self.smoothed_pts is None:
            self.smoothed_pts = np.array(current_pts, dtype=np.float32)
        else:
            self.smoothed_pts = self.alpha * np.array(current_pts, dtype=np.float32) + (1.0 - self.alpha) * self.smoothed_pts
        return self.smoothed_pts.astype(np.int32)

class FaceDetector:
    """
    Module pour la détection du visage et l'extraction des régions d'intérêt (ROIs) 
    (front et joues) à l'aide de MediaPipe Face Landmarker (Nouvelle API Tasks).
    Intègre une stabilisation des régions (EMA Tracker).
    """
    def __init__(self):
        # Téléchargement du modèle s'il n'existe pas localement (Requis pour la nouvelle API MediaPipe)
        self.model_path = 'face_landmarker.task'
        if not os.path.exists(self.model_path):
            print("Téléchargement du modèle MediaPipe Face Landmarker...")
            url = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
            urllib.request.urlretrieve(url, self.model_path)
            print("Modèle téléchargé.")

        # Configuration de la nouvelle API
        base_options = python.BaseOptions(model_asset_path=self.model_path)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_faces=1,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5
        )
        self.detector = vision.FaceLandmarker.create_from_options(options)
        
        # Indices MediaPipe pour les ROIs approximatives (Front et Pommettes)
        self.forehead_pts = [103, 67, 109, 10, 338, 297, 332, 284, 298, 297, 296, 336, 9, 107, 66, 68, 71]
        self.left_cheek_pts = [118, 119, 100, 126, 198, 134, 51, 5, 4, 48, 115, 215]
        self.right_cheek_pts = [347, 348, 329, 355, 420, 363, 281, 285, 274, 278, 344, 435]
        
        # Trackers pour lisser les saccades de mouvement
        self.f_tracker = ROITracker(alpha=0.3)
        self.lc_tracker = ROITracker(alpha=0.3)
        self.rc_tracker = ROITracker(alpha=0.3)

    def get_rois(self, frame):
        """
        Détecte le visage et extrait les masques pour le front et les joues.
        """
        # Convertir en RGB et en format Image MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        results = self.detector.detect(mp_image)
        
        h, w, _ = frame.shape
        rois = {}
        
        if not results.face_landmarks:
            return False, None, frame, None

        face_landmarks = results.face_landmarks[0]
        
        def get_raw_pts(indices):
            return np.array([(int(face_landmarks[i].x * w), int(face_landmarks[i].y * h)) for i in indices], dtype=np.int32)
            
        def create_mask(pts):
            mask = np.zeros((h, w), dtype=np.uint8)
            if len(pts) > 0:
                cv2.fillConvexPoly(mask, pts, 255)
            return mask

        # Récupération et Lissage
        f_pts = self.f_tracker.update(get_raw_pts(self.forehead_pts))
        lc_pts = self.lc_tracker.update(get_raw_pts(self.left_cheek_pts))
        rc_pts = self.rc_tracker.update(get_raw_pts(self.right_cheek_pts))

        rois['forehead'] = create_mask(f_pts)
        rois['left_cheek'] = create_mask(lc_pts)
        rois['right_cheek'] = create_mask(rc_pts)
        
        # Bounding box globals pour le FaceID Overlay
        all_pts = np.vstack([f_pts, lc_pts, rc_pts])
        x_min, y_min = np.min(all_pts, axis=0)
        x_max, y_max = np.max(all_pts, axis=0)
        
        # Expand box slightly
        pad = 20
        bbox = (max(0, x_min - pad), max(0, y_min - pad * 2), min(w, x_max + pad), min(h, y_max + pad))
        
        return True, rois, frame.copy(), bbox
