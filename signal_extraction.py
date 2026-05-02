import numpy as np

class SignalExtractor:
    """
    Module pour l'extraction du signal rPPG brut depuis le canal vert.
    Le sang absorbe particulièrement bien la lumière verte, ce qui fait
    varier l'intensité des pixels verts au rythme du pouls.
    """
    def __init__(self):
        pass

    def extract_green_from_rois(self, frame, rois):
        """
        Extrait la moyenne de l'intensité du canal vert dans les zones cibles.
        Retourne aussi un indicateur de qualité du signal (SQI).
        
        Args:
            frame: Image BGR OpenCV
            rois: Dictionnaire des masques généré par face_detection.py
            
        Returns:
            mean_val (float): Intensité moyenne du canal vert
            low_light (bool): True si le niveau de lumière est trop faible
        """
        # OpenCV charge les images en BGR, le vert est l'indice 1
        green_channel = frame[:, :, 1]
        
        # On combine tous les masques (front, joues) pour avoir une zone d'intérêt unifiée
        combined_mask = np.bitwise_or.reduce([rois[k] for k in rois.keys()])
        
        # Filtrer les pixels qui sont dans les masques de ROI
        pixels_in_roi = green_channel[combined_mask > 0]
        
        if len(pixels_in_roi) > 0:
            mean_val = np.mean(pixels_in_roi)
            # SQI basique
            low_light = mean_val < 40.0
            return mean_val, low_light
        return 0.0, True
