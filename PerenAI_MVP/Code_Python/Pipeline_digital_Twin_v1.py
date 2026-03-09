import pandas as pd
import numpy as np
import argparse
import os

def merge_excel(input_excel_path, output_csv_path):
    """
    Merges data from the Excel file into a long format CSV.
    """
    df = pd.read_excel(input_excel_path)

    base_cols = ["ID"]

    periods = ["", ".1", ".2"]

    dfs = []

    for p in periods:
        temp = pd.DataFrame({
            "user_id": df["ID"],
            "sex": df[f"Sexe{p}"],
            "age": df[f"Âge{p}"],
            "height_cm": df[f"Taille{p}"],
            "weight_kg": df[f"Poids{p}"],
            "Sport_type": df[f"Sport{p}"],
            "activity_freq": df[f"PA{p}"],
            "sleep_duration": df[f"Sommeil{p}"],
            "stress_level": df[f"Stress{p}"],
            "nutrition_raw": df[f"Nutri{p}"],
            "sedentary_time": df[f"Sédentaire{p}"],
            "alcohol_raw": df[f"Alcool{p}"],
            "family_history_raw": df[f"Antécédents{p}"],
            "cycle_raw": df[f"Cycle{p}"],
            "date": df[f"Date{p}"],
            "time": df[f"Heure{p}"],
        })

        dfs.append(temp)

    long_df = pd.concat(dfs, ignore_index=True)

    long_df["datetime"] = pd.to_datetime(long_df["date"].astype(str) + " " + long_df["time"].astype(str))

    long_df = long_df.sort_values(["user_id", "datetime"])

    cols = list(long_df.columns)
    cols.remove("datetime")
    new_cols = ["user_id", "datetime"] + [c for c in cols if c != "user_id"]
    long_df = long_df[new_cols]
    long_df['sex'] = long_df.groupby('user_id')['sex'].ffill()

    long_df.to_csv(output_csv_path, index=False)
    return output_csv_path

def clean_mapping(input_csv_path, output_csv_path):
    """
    Cleans and maps data, calculates BMI, normalizes variables.
    """
    df_raw = pd.read_csv(input_csv_path)
    df = df_raw.copy()

    df["sex"] = df["sex"].astype(str).str.upper()  # Handle case variations
    df["sex"] = df["sex"].map({"F": "female", "H": "male", "M": "male"})  # Expanded map
    df["sex"] = df.groupby('user_id')['sex'].ffill()  # Extra ffill if any blanks remain

    # IMC (BMI)
    df["height_m"] = df["height_cm"] / 100
    df["bmi"] = df["weight_kg"] / (df["height_m"] ** 2)

    # Stress
    stress_map = {
        "Faible": "low",
        "Modéré": "moderate",
        "Élevé": "high"
    }
    df["stress_level_norm"] = df["stress_level"].map(stress_map)

    # Sommeil (fixed the lambda based on context: assuming 0 for <6h, 1 otherwise)
    # Note: Original had typo; adjusted to lambda x: 0 if x == "<6h" else 1
    df["sleep_6h_plus_norm"] = df["sleep_duration"].apply(lambda x: 0 if x == ">6h" else 1)

    # Nutrition
    nutrition_map = {
        "Maison": "equilibrated",
        "Mix maison": "mixed",
        "Mix": "mixed",
        "Équilibrée": "equilibrated"
    }
    df["nutrition_norm"] = df["nutrition_raw"].map(nutrition_map)

    df["family_history_flag"] = df["family_history_raw"].apply(lambda x: 0 if x == "Aucun" else 1)

    df.to_csv(output_csv_path, index=False)
    return output_csv_path

def calculate_scores(input_csv_path, output_scores_csv_path, output_features_csv_path):
    """
    Calculates scores like body_age, work_load, body_toxins.
    """
    df = pd.read_csv(input_csv_path)

    # Body Age Score Maps
    activity_score_map_body_age = {
        "0–1": 3,
        "0": 3,
        "1": 3,
        "2–3": 1,
        "2": 1,
        "3": 1,
        "4": 0,
        "4–5": 0,
        "5": 0,
        "≥6": -2
    }

    def bmi_score(bmi):
        if bmi < 18.5:
            return 1
        elif 18.5 <= bmi < 25:
            return 0
        elif 25 <= bmi < 30:
            return 1
        else:
            return 3

    sleep_score_map_body_age = {
        "<6h": 1,
        "6–7h": 0,
        "7–8h": 0,
        ">8h": -1
    }

    stress_score_map_body_age = {
        "high": 2,
        "moderate": 1,
        "low": 0
    }

    nutrition_score_map_body_age = {
        "poor": 2,
        "mixed": 0,
        "equilibrated": -1
    }

    df["activity_score"] = df["activity_freq"].map(activity_score_map_body_age).fillna(0)
    df["bmi_score"] = df["bmi"].apply(bmi_score)
    df["sleep_score"] = df["sleep_duration"].map(sleep_score_map_body_age).fillna(0)
    df["stress_score"] = df["stress_level_norm"].map(stress_score_map_body_age).fillna(0)
    df["nutrition_score"] = df["nutrition_norm"].map(nutrition_score_map_body_age).fillna(0)

    df["body_age"] = (
        df["age"]
        + df["activity_score"]
        + df["bmi_score"]
        + df["sleep_score"]
        + df["stress_score"]
        + df["nutrition_score"]
    )

    # Work Load Score Maps
    activity_freq_map_workload = {
        "0–1": 0,
        "0": 0,
        "1": 0,
        "2–3": 10,
        "2": 10,
        "3": 10,
        "4": 20,
        "4–5": 20,
        "5": 20,
        "≥6": 30
    }

    stress_map_workload = {
        "low": 0,
        "moderate": -10,
        "high": -20,
        "very_high": -30
    }

    df["intensity_score_workload"] = 0
    df["activity_score_workload"] = df["activity_freq"].map(activity_freq_map_workload).fillna(0)
    df["stress_score_workload"] = df["stress_level_norm"].map(stress_map_workload).fillna(0)
    df["sleep_debt_score_workload"] = df["sleep_6h_plus_norm"].apply(lambda x: 0 if x == 1 else 20)

    df["work_load"] = (
        df["intensity_score_workload"]
        + df["activity_score_workload"]
        - df["stress_score_workload"]
        - df["sleep_debt_score_workload"]
    )

    # Body Toxins Score Maps
    nutrition_exposure_map_toxins = {
        "ultra_processed": 2,
        "mixed": 0,
        "equilibrated": 0
    }

    alcohol_exposure_map_toxins = {
        "Jamais": 0,
        "Occasionnel": 0,
        "Régulier": 2,
        "1–3/sem": 2,
        ">3/sem": 2
    }

    df["Hydratation_score_toxins"] = 0
    df["nutrition_toxin"] = df["nutrition_norm"].map(nutrition_exposure_map_toxins).fillna(0)
    df["alcohol_toxin"] = df["alcohol_raw"].map(alcohol_exposure_map_toxins).fillna(0)

    df["sport_toxins"] = df["activity_freq"].apply(
        lambda x: -2 if x in ["3", "4", "4–5", "≥5"] else 0
    )

    df["Body_Toxins"] = (
        df["nutrition_toxin"]
        + df["alcohol_toxin"]
        - (df["Hydratation_score_toxins"] + df["sport_toxins"])
    )

    # Final Features (from notebook)
    final_features = df[[
        "user_id",
        "datetime",
        "sex",
        "age",
        "height_cm",
        "weight_kg"
    ]].copy()

    final_features["body_age"] = df["body_age"]
    final_features["work_load"] = df["work_load"]
    final_features["body_toxin"] = df["Body_Toxins"]
    final_features["sync_cycle"] = None
    final_features["energy"] = None
    final_features["recovery"] = None

    long_df = final_features.drop(columns=["sync_cycle", "energy", "recovery"])

    final_features.to_csv(output_features_csv_path, index=False)
    long_df.to_csv(output_scores_csv_path, index=False)
    return output_scores_csv_path  # Main output used by next step

def digital_twin(input_csv_path, output_csv_path):
    """
    Adds temporal modeling, states, changes for digital twin.
    """
    df = pd.read_csv(input_csv_path)
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.sort_values(["user_id", "datetime"])

    # Body Age
    df["delta_body_age"] = df["body_age"] - df["age"]

    def body_age_state(delta):
        if delta <= -2:
            return "younger_than_chrono"
        elif -1 <= delta <= 1:
            return "aligned_with_chrono"
        else:
            return "accelerated_aging"

    df["body_age_state"] = df["delta_body_age"].apply(body_age_state)
    df["body_age_change"] = df.groupby("user_id")["body_age"].diff().fillna(0)

    # Work Load
    def workload_state(score):
        if score <= 0:
            return "low_load"
        elif score <= 30:
            return "moderate_load"
        else:
            return "high_load"

    df["workload_state"] = df["work_load"].apply(workload_state)
    df["work_load_change"] = df.groupby("user_id")["work_load"].diff().fillna(0)

    # Body Toxins
    def toxin_state(score):
        if score <= 0:
            return "low_toxic_load"
        elif score <= 2:
            return "moderate_toxic_load"
        else:
            return "high_toxic_load"

    df["body_toxins_state"] = df["body_toxin"].apply(toxin_state)
    df["body_toxin_change"] = df.groupby("user_id")["body_toxin"].diff().fillna(0)

    df["global_body_state"] = (
        df["body_age_state"] + " | "
        + df["workload_state"] + " | "
        + df["body_toxins_state"]
    )

    final_cols = [
        "user_id",
        "datetime",
        "sex",
        "age",
        "height_cm",
        "weight_kg",

        "body_age",
        "body_age_change",
        "body_age_state",

        "work_load",
        "work_load_change",
        "workload_state",

        "body_toxin",
        "body_toxin_change",
        "body_toxins_state",
    ]

    df_final = df[final_cols].copy()
    df_final.to_csv(output_csv_path, index=False)
    return output_csv_path

def run_pipeline(input_excel):
    csv1 = 'temp_merged.csv'
    merge_excel(input_excel, csv1)
    
    csv2 = 'temp_cleaned.csv'
    clean_mapping(csv1, csv2)
    
    csv3 = 'temp_scores.csv'
    features_temp = 'temp_features.csv'  # Not used in next step
    calculate_scores(csv2, csv3, features_temp)
    
    final_csv = 'final_digital_twin.csv'
    digital_twin(csv3, final_csv)
    
    print(f"Pipeline complete. Final output: {final_csv}")
    
    # Optional: Clean up temporary files
    os.remove(csv1)
    os.remove(csv2)
    os.remove(csv3)
    os.remove(features_temp)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automate the 4-notebook pipeline from Excel to final CSV.")
    parser.add_argument('--input', required=True, help='Path to the input Excel file')
    args = parser.parse_args()
    run_pipeline(args.input)