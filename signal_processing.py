import numpy as np
from scipy.signal import butter, filtfilt, detrend

class SignalProcessor:
    """
    Module pour le nettoyage du signal rPPG (Filtrage et Normalisation).
    Gère désormais les bandes cardiaques et respiratoires.
    """
    def __init__(self, cardiac_low=0.75, cardiac_high=4.0, resp_low=0.15, resp_high=0.4):
        self.c_low = cardiac_low
        self.c_high = cardiac_high
        self.r_low = resp_low
        self.r_high = resp_high

    def butter_bandpass(self, lowcut, highcut, fps, order=3):
        """Construction du filtre de Butterworth pass-band."""
        nyq = 0.5 * fps
        low = max(0.01, min(lowcut / nyq, 0.99))
        high = max(0.01, min(highcut / nyq, 0.99))
        b, a = butter(order, [low, high], btype='band')
        return b, a

    def process(self, raw_signal, fps):
        """
        Traite le signal brut: Detrending, Filtrages passe-bande et Z-score.
        
        Returns:
            cardiac_signal: Signal cardiaque normalisé (pour HR/HRV)
            resp_signal: Signal respiratoire (pour RR)
        """
        y = np.array(raw_signal)
        
        # 1. Detrending (Retrait de la tendance lente / dérive de lumière)
        y_detrended = detrend(y, type='linear')
        
        # 2. Filtrage Cardiaque
        b_c, a_c = self.butter_bandpass(self.c_low, self.c_high, fps, order=4)
        c_filtered = filtfilt(b_c, a_c, y_detrended)
        
        # Normalisation Z-score
        std_c = np.std(c_filtered)
        c_normalized = c_filtered / std_c if std_c > 1e-10 else c_filtered
            
        # 3. Filtrage Respiratoire
        b_r, a_r = self.butter_bandpass(self.r_low, self.r_high, fps, order=2)
        r_filtered = filtfilt(b_r, a_r, y_detrended)
            
        return c_normalized, r_filtered
