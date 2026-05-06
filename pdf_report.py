import os
import uuid
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
from fpdf import FPDF

class PDFReport:
    """Genere un rapport PDF robuste a partir d'un CSV de biomarqueurs."""
    def __init__(self, csv_file="results.csv"):
        self.csv_file = csv_file

    @staticmethod
    def _safe_text(value):
        """Convertit et nettoie les textes pour une sortie FPDF stable."""
        text = str(value) if value is not None else ""
        # Evite les crashs de sortie lies aux caracteres hors latin-1.
        return text.encode("latin-1", errors="replace").decode("latin-1")

    @staticmethod
    def _safe_float(value, default=0.0):
        try:
            return float(value)
        except Exception:
            return float(default)

    @staticmethod
    def _normalize_session_data(session_data):
        session_data = session_data or {}
        metrics = session_data.get("metrics", {}) if isinstance(session_data, dict) else {}
        states = session_data.get("states", {}) if isinstance(session_data, dict) else {}
        return {
            "scan_id": session_data.get("scan_id", "N/A") if isinstance(session_data, dict) else "N/A",
            "timestamp": session_data.get("timestamp") if isinstance(session_data, dict) else None,
            "metrics": {
                "hr": PDFReport._safe_float(metrics.get("hr", 0.0)),
                "hrv": PDFReport._safe_float(metrics.get("hrv", 0.0)),
                "rr": PDFReport._safe_float(metrics.get("rr", 0.0)),
                "score": PDFReport._safe_float(metrics.get("score", 0.0)),
                "bp": str(metrics.get("bp", "--")),
                "stress_index": PDFReport._safe_float(metrics.get("stress_index", 0.0)),
                "workload": PDFReport._safe_float(metrics.get("workload", 0.0)),
            },
            "states": {
                "wellness": str(states.get("wellness", "Indisponible")),
                "heart_rate": str(states.get("heart_rate", "Indisponible")),
                "stress": str(states.get("stress", "Indisponible")),
            },
        }

    def generate(self, output_path=None, session_data=None):
        graph_path = None
        try:
            normalized_session = self._normalize_session_data(session_data)
            if session_data is not None:
                metrics = normalized_session["metrics"]
                df = pd.DataFrame(
                    {
                        "HR": [metrics["hr"], metrics["hr"]],
                        "HRV": [metrics["hrv"], metrics["hrv"]],
                        "RR": [metrics["rr"], metrics["rr"]],
                        "Score": [metrics["score"], metrics["score"]],
                    }
                )
            else:
                if not os.path.exists(self.csv_file):
                    print("Aucun fichier de resultat trouve, rapport annule.")
                    return False
                df = pd.read_csv(self.csv_file)
                if df.empty:
                    return False
                expected_cols = ["HR", "HRV", "RR", "Score"]
                for col in expected_cols:
                    if col not in df.columns:
                        df[col] = 0.0
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
                if len(df) < 2:
                    df = pd.concat([df, df], ignore_index=True)

            # Graphe Matplotlib
            plt.figure(figsize=(10, 4))
            plt.plot(df.index, df["HR"], label="Heart Rate (BPM)", color="green", linewidth=2)
            plt.title("Evolution du rythme cardiaque (BPM)")
            plt.xlabel("Mesures (Temporel)")
            plt.ylabel("BPM")
            plt.grid(True)
            plt.tight_layout()
            graph_path = f"temp_hr_plot_{uuid.uuid4().hex[:8]}.png"
            plt.savefig(graph_path)
            plt.close()

            # PDF avec FPDF
            pdf = FPDF()
            pdf.add_page()

            # En-tete
            pdf.set_font("Helvetica", "B", 18)
            pdf.cell(0, 10, self._safe_text("PEREN AI - Wellness Report"), new_x="LMARGIN", new_y="NEXT", align="C")
            pdf.set_font("Helvetica", "I", 10)
            session_date = normalized_session["timestamp"] or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            pdf.cell(
                0,
                10,
                self._safe_text(f"Session Date: {session_date}"),
                new_x="LMARGIN",
                new_y="NEXT",
                align="C",
            )
            pdf.ln(10)

            # Synthese
            mean_hr = self._safe_float(df["HR"].mean())
            mean_hrv = self._safe_float(df["HRV"].mean())
            mean_rr = self._safe_float(df["RR"].mean())
            mean_score = self._safe_float(df["Score"].mean())
            metrics = normalized_session["metrics"]
            states = normalized_session["states"]

            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 10, self._safe_text("Resume de la session :"), new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 12)
            pdf.cell(0, 10, self._safe_text(f"- Scan ID : {normalized_session['scan_id']}"), new_x="LMARGIN", new_y="NEXT")
            pdf.cell(
                0,
                10,
                self._safe_text(f"- Rythme Cardiaque Moyen : {mean_hr:.1f} BPM"),
                new_x="LMARGIN",
                new_y="NEXT",
            )
            pdf.cell(
                0,
                10,
                self._safe_text(f"- Variabilite (HRV/RMSSD) Moyenne : {mean_hrv:.1f} ms"),
                new_x="LMARGIN",
                new_y="NEXT",
            )
            pdf.cell(
                0,
                10,
                self._safe_text(f"- Frequence Respiratoire Moyenne : {mean_rr:.1f} cpm"),
                new_x="LMARGIN",
                new_y="NEXT",
            )
            pdf.cell(
                0,
                10,
                self._safe_text(f"- Score Physique Global : {mean_score:.1f} / 100"),
                new_x="LMARGIN",
                new_y="NEXT",
            )
            pdf.cell(0, 10, self._safe_text(f"- Blood Pressure : {metrics['bp']} mmHg"), new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 10, self._safe_text(f"- Stress Index : {metrics['stress_index']:.0f} / 100"), new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 10, self._safe_text(f"- Cardiac Workload : {metrics['workload']:.1f} %"), new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 10, self._safe_text(f"- Etat global : {states['wellness']}"), new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 10, self._safe_text(f"- Stress : {states['stress']}"), new_x="LMARGIN", new_y="NEXT")
            pdf.ln(10)

            # Inserer l'image du graphe
            pdf.image(graph_path, x=10, y=pdf.get_y(), w=190)

            report_name = output_path or f"PEREN_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}.pdf"
            pdf.output(report_name)

            print(f"Rapport PDF genere avec succes : {report_name}")
            return report_name
        except Exception as e:
            print(f"Erreur PDF : {e}")
            return False
        finally:
            if graph_path and os.path.exists(graph_path):
                try:
                    os.remove(graph_path)
                except OSError:
                    pass
