class Classifier:
    """
    Module pour la classification de l'état de bien-être
    en fonction du score calculé et du rythme cardiaque brut.
    """
    def __init__(self):
        pass
        
    def classify_state_by_score(self, score):
        """
        Interprète le score de bien-être.
        """
        if score >= 80:
            return "Équilibré"
        elif score >= 60:
            return "À surveiller"
        else:
            return "À risque"

    def get_bpm_state(self, hr):
        """
        Interprète l'état basé uniquement sur le rythme cardiaque (HR).
        Returns un tuple: (Texte, Couleur OpenCV BGR)
        """
        if hr <= 0.0:
            return ("Calcul...", (150, 150, 150)) # Gris
        elif hr < 60:
            return ("Low", (255, 165, 0)) # Bleu/Orange (Orange OpenCV: B=0, G=165, R=255) -> (0, 165, 255)
        elif hr <= 100:
            return ("Normal", (0, 255, 0)) # Vert
        else:
            return ("High", (0, 0, 255)) # Rouge

    def get_stress_level(self, hrv):
        """
        Interprète le niveau de stress basé sur la variabilité (RMSSD).
        Plus c'est élevé, mieux c'est (dominance parasympathique).
        Returns un tuple: (Texte, Couleur OpenCV BGR)
        """
        if hrv <= 0.0:
            return ("Calcul...", (150, 150, 150))
        elif hrv < 25:
            return ("High Stress", (0, 0, 255)) # Rouge
        elif hrv < 45:
            return ("Normal", (0, 255, 0)) # Vert
        else:
            return ("Low (Relaxed)", (255, 200, 0)) # Cyan
