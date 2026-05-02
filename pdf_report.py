import pandas as pd
from fpdf import FPDF
import matplotlib.pyplot as plt
import os
from datetime import datetime

class PDFReport:
    """Génère un rapport de santé PDF à l'aide de fpdf2 et matplotlib."""
    def __init__(self, csv_file="results.csv"):
        self.csv_file = csv_file
        
    def generate(self):
        if not os.path.exists(self.csv_file):
            print("Aucun fichier de résultat trouvé, rapport annulé.")
            return False
            
        try:
            df = pd.read_csv(self.csv_file)
            if len(df) < 2: return False
            
            # --- Graphe Matplotlib ---
            plt.figure(figsize=(10, 4))
            plt.plot(df.index, df['HR'], label="Heart Rate (BPM)", color='green', linewidth=2)
            plt.title("Evolution du Rythme Cardiaque (BPM) au cours de la session")
            plt.xlabel("Mesures (Temporel)")
            plt.ylabel("BPM")
            plt.grid(True)
            plt.tight_layout()
            graph_path = "temp_hr_plot.png"
            plt.savefig(graph_path)
            plt.close()
            
            # --- PDF avec FPDF2 ---
            pdf = FPDF()
            pdf.add_page()
            
            # En-tête
            pdf.set_font("Helvetica", "B", 18)
            pdf.cell(0, 10, "PEREN AI - Wellness Report", new_x="LMARGIN", new_y="NEXT", align='C')
            pdf.set_font("Helvetica", "I", 10)
            pdf.cell(0, 10, f"Session Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", new_x="LMARGIN", new_y="NEXT", align='C')
            pdf.ln(10)
            
            # Synthèse
            mean_hr = df['HR'].mean()
            mean_hrv = df['HRV'].mean()
            mean_score = df['Score'].mean()
            
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 10, "Resume de la session :", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 12)
            pdf.cell(0, 10, f"- Rythme Cardiaque Moyen : {mean_hr:.1f} BPM", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 10, f"- Variabilite (HRV/RMSSD) Moyenne : {mean_hrv:.1f} ms", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 10, f"- Score Physique Global : {mean_score:.1f} / 100", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(10)
            
            # Insérer Image
            pdf.image(graph_path, x=10, y=pdf.get_y(), w=190)
            
            report_name = f"PEREN_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf.output(report_name)
            
            if os.path.exists(graph_path):
                os.remove(graph_path)
                
            print(f"Rapport PDF genere avec succes : {report_name}")
            return True
        except Exception as e:
            print(f"Erreur PDF : {e}")
            return False
