import numpy as np
from scipy.signal import find_peaks

class FeatureExtractor:
    """
    Module responsable du calcul des métriques physiologiques (HR, HRV et RR)
    à partir des signaux rPPG filtrés.
    """
    def __init__(self):
        pass

    def calculate_hrv(self, peaks, fps):
        """
        Calcule la Variabilité de Fréquence Cardiaque (HRV) estimée (RMSSD).
        """
        if len(peaks) < 2:
            return 0.0
            
        times = peaks / fps * 1000.0
        rr_intervals = np.diff(times)
        
        if len(rr_intervals) < 1:
            return 0.0
            
        diff_rr = np.diff(rr_intervals)
        rmssd = np.sqrt(np.mean(diff_rr**2)) if len(diff_rr) > 0 else 0.0
        return rmssd

    def extract_features(self, cardiac_signal, fps):
        """
        Sépare le HR et le HRV.
        """
        N = len(cardiac_signal)
        if N < 30: 
            return 0.0, 0.0
            
        fft_data = np.fft.rfft(cardiac_signal)
        fft_freqs = np.fft.rfftfreq(N, 1.0 / fps)
        amplitudes = np.abs(fft_data)
        
        valid_indices = np.where((fft_freqs >= 0.75) & (fft_freqs <= 4.0))[0]
        if len(valid_indices) == 0:
            return 0.0, 0.0
            
        dominant_freq = fft_freqs[valid_indices][np.argmax(amplitudes[valid_indices])]
        hr = dominant_freq * 60.0
        
        peaks, _ = find_peaks(cardiac_signal, distance=int(fps/4.0))
        hrv = self.calculate_hrv(peaks, fps)
        
        return hr, hrv

    def extract_rr(self, resp_signal, fps):
        """
        Estime la fréquence respiratoire (Breathes Per Minute) via le signal respiratoire.
        """
        N = len(resp_signal)
        if N < 30: 
            return 0.0
            
        fft_data = np.fft.rfft(resp_signal)
        fft_freqs = np.fft.rfftfreq(N, 1.0 / fps)
        amplitudes = np.abs(fft_data)
        
        # Fréquence respiratoire humaine normale au repos : ~12 à 20 cycles par minute (0.2 à 0.33 Hz)
        # On regarde entre 9 et 24 CPM (0.15 à 0.4 Hz)
        valid_indices = np.where((fft_freqs >= 0.15) & (fft_freqs <= 0.4))[0]
        if len(valid_indices) == 0:
            return 0.0
            
        dominant_freq = fft_freqs[valid_indices][np.argmax(amplitudes[valid_indices])]
        rr = dominant_freq * 60.0
        
        return rr
