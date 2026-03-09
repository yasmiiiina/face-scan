import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

# ==============================
# 1️⃣ Charger dataset
# ==============================
df = pd.read_csv("C:\\Users\\bouch\\OneDrive\\Desktop\\peren_ai_mvp\\data\\processed\\01_Dataset_clean_merge.csv")
df["datetime"] = pd.to_datetime(df["datetime"])

# ==============================
# 2️⃣ Garder 1 seule ligne par user (première apparition)
# ==============================
df_unique = df.sort_values("datetime").drop_duplicates("user_id")
total_users = df_unique["user_id"].nunique()

# ==============================
# 3️⃣ Catégorisation des sports
# ==============================
def sport_category(sport):
    endurance = ["Running", "Football", "Triathlon"]
    if sport in endurance:
        return "Sports d'endurance"
    else:
        return "Autres sports"

df_unique["sport_category"] = df_unique["Sport_type"].apply(sport_category)

# ==============================
# 4️⃣ Camembert GLOBAL (Endurance / Autres)
# ==============================
sport_counts = df_unique["sport_category"].value_counts()
n = len(sport_counts)
colors = cm.Purples_r(np.linspace(0.3, 0.9, n))  # couleurs distinctes violettes

plt.figure(figsize=(6,6))
plt.pie(
    sport_counts,
    labels=sport_counts.index,
    autopct='%1.1f%%',
    colors=colors
)
plt.title(f"Répartition globale des disciplines\n{total_users} inscrits")
plt.show()

# ==============================
# 5️⃣ Camembert ACTIVITÉS RETENUES (Sports d'endurance)
# ==============================
retained_sports = ["Running", "Football", "Triathlon"]
df_retained = df_unique[df_unique["Sport_type"].isin(retained_sports)]
retained_counts = df_retained["Sport_type"].value_counts()
n = len(retained_counts)
colors = cm.Purples_r(np.linspace(0.3, 0.9, n))

plt.figure(figsize=(6,6))
plt.pie(
    retained_counts,
    labels=retained_counts.index,
    autopct='%1.1f%%',
    colors=colors
)
plt.title("Activités retenues (Sports d'endurance)")
plt.show()

# ==============================
# 6️⃣ Camembert TOUS LES SPORTS (1 ligne par user)
# ==============================
# Remplace la section 6️⃣ par ceci :
all_sport_counts = df_unique["Sport_type"].value_counts(normalize=True) * 100 # En %
n = len(all_sport_counts)
colors = cm.Purples_r(np.linspace(0.3, 0.9, n))

plt.figure(figsize=(10, 8))
all_sport_counts.sort_values().plot(kind='barh', color=colors)

plt.xlabel("Pourcentage (%)")
plt.title("Répartition de tous les sports (Plus lisible)")
plt.grid(axis='x', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()