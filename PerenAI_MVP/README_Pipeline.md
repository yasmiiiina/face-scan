# Digital Health Twin – Data Pipeline


## 👤 Auteur
**Bouchra Sahel** AI Engineer 

## 🏢 Propriété
© 2026 **PEREN AI Technologies**. Tous droits réservés.  
PEREN AI® est une marque déposée de PEREN AI Technologies.  
🌐 [www.peren.ai](https://www.peren.ai)

---

## Overview

This project implements a **data pipeline for the Digital Health Twin system**.  
The pipeline transforms raw questionnaire data collected from Excel files into a **structured dataset representing the digital twin state of each user**.

The pipeline performs four main phases:

1. Data merging
2. Data cleaning and normalization
3. Feature engineering and score computation
4. Digital Twin modeling

The final output is a structured dataset that can be used for:

- health monitoring
- dashboards
- predictive modeling
- future machine learning systems

---

# Pipeline Architecture

Input Data → Merge → Clean & Normalize → Feature Engineering → Digital Twin Modeling → Final Dataset

---

# Input Data

The pipeline expects an **Excel questionnaire dataset (.xlsx)** containing user health and lifestyle information.

Example variables:

- ID
- Sexe
- Âge
- Taille
- Poids
- Sport
- Activité physique
- Sommeil
- Stress
- Nutrition
- Alcool
- Antécédents
- Cycle
- Date
- Heure

The dataset may contain **multiple periods of data collection** for the same user.

---

# Pipeline Phases

## Phase 1 — Data Merge

Function:

```
merge_excel()
```

Goal:

Transform the Excel dataset into a **long format dataset**.

Operations:

- read Excel file
- extract multiple periods (.1, .2)
- merge observations
- create datetime variable
- sort by user and time

Output:

```
temp_merged.csv
```

---

## Phase 2 — Data Cleaning & Normalization

Function:

```
clean_mapping()
```

Goal:

Standardize and normalize the dataset.

Operations:

- normalize sex values
- compute BMI
- map stress levels
- normalize nutrition variables
- encode family history
- normalize sleep variables

Output:

```
temp_cleaned.csv
```

---

## Phase 3 — Feature Engineering & Score Calculation

Function:

```
calculate_scores()
```

Goal:

Compute health-related indicators.

Generated scores:

### Body Age

Estimated biological aging based on:

- physical activity
- BMI
- sleep
- stress
- nutrition

### Work Load

Training load estimation based on:

- activity frequency
- stress
- sleep debt

### Body Toxins

Toxic exposure estimation based on:

- alcohol consumption
- nutrition
- sport activity

Outputs:

```
temp_scores.csv
temp_features.csv
```

---

## Phase 4 — Digital Twin Modeling

Function:

```
digital_twin()
```

Goal:

Create a **temporal digital representation of the user's health state**.

Generated variables:

### Body Age State

- younger_than_chrono
- aligned_with_chrono
- accelerated_aging

### Workload State

- low_load
- moderate_load
- high_load

### Body Toxin State

- low_toxic_load
- moderate_toxic_load
- high_toxic_load

Also computed:

- score variations over time
- global body state

Output:

```
final_digital_twin.csv
```

---

# Running the Pipeline

Run the pipeline from the command line:

```
python Pipeline_digital_Twin_v1.py --input input_data.xlsx
```

Example:

```
python Pipeline_digital_Twin_v1.py --input users_health_data.xlsx
```

Final output:

```
final_digital_twin.csv
```

---

# Output Dataset

The final dataset contains:

| Column | Description |
|------|------|
| user_id | Unique user identifier |
| datetime | Timestamp |
| sex | User sex |
| age | Chronological age |
| height_cm | Height |
| weight_kg | Weight |
| body_age | Estimated biological age |
| body_age_change | Variation over time |
| body_age_state | Biological aging state |
| work_load | Physical workload score |
| work_load_change | Variation over time |
| workload_state | Workload category |
| body_toxin | Toxic exposure score |
| body_toxin_change | Variation over time |
| body_toxins_state | Toxic exposure state |

---

# Future Extensions

The pipeline can be extended with:

### Wearable Data Integration

- heart rate
- sleep tracking
- physical activity sensors

### Machine Learning Models

Potential prediction tasks:

- health risk prediction
- fatigue prediction
- recovery estimation
- anomaly detection

### Digital Twin Simulation

Future digital twin models may simulate:

- lifestyle changes
- training load adaptation
- health evolution over time

---

# Technologies Used

- Python
- Pandas
- NumPy
- Streamlit (dashboard)
- Machine Learning (future phase)

---

# Author

AI Engineer – Digital Health Twin Project