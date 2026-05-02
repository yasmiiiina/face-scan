class ScoreCalculator:
    """
    Module pour l'algorithme de calcul du score de bien-être (0-100)
    basé sur les métriques calculées.
    """
    def __init__(self):
        pass

    def count_score(self, hr, hrv):
        """
        Calcule un score sur 100 combinant HR et HRV.
        Ceci est une heuristique basique.
        
        Considérations :
        - HR optimal : 60-80 BPM (Repose complet). Pénalité plus on s'en éloigne.
        - HRV (RMSSD) : Plus il est élevé, plus le système parasympathique est actif (meilleur bien-être).
        """
        if hr == 0.0:
            return 0.0
            
        score = 100.0
        
        # Ajustement sur la fréquence cardiaque (HR)
        if 60 <= hr <= 80:
            # Optimal
            pass
        elif 50 <= hr < 60 or 80 < hr <= 90:
            score -= 10
        elif 40 <= hr < 50 or 90 < hr <= 100:
            score -= 20
        else:
            score -= 30
            
        # Ajustement sur le HRV (Varie grandement selon l'individu, heuristique générique)
        # Supposons un HRV optimal cible > 50ms pour un jeune/adulte en bonne santé.
        if hrv < 20: 
            score -= 15 # Possible stress
        elif hrv < 30:
            score -= 5
        elif hrv > 50:
            score += 5 # Bonus
            
        # Borner entre 0 et 100
        return max(0.0, min(100.0, score))

    def classify_state(self, score):
        """
        Exporte une classification de l'état en tant que texte.
        """
        if score >= 80:
            return "Équilibré"
        elif score >= 60:
            return "À surveiller"
        else:
            return "À risque"
