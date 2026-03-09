# 🧬 Digital Twin – Phase 3: Metrics Processing & Dashboard Dataset

## 👤 Auteur
**Bouchra Sahel** AI Engineer / Digital Twin & Data Processing

## 🏢 Propriété
© 2026 **PEREN AI Technologies**. Tous droits réservés.  
PEREN AI® est une marque déposée de PEREN AI Technologies.  
🌐 [www.peren.ai](https://www.peren.ai)

---

## 📌 Objectif de la Phase 3

La Phase 3 transforme les données brutes issues de la Phase 2 en un **dataset propre, dynamique et prêt pour le dashboard Digital Twin**. 

Cette étape est cruciale pour passer d'une simple base de données à un outil d'aide à la décision :
* **Nettoyage** en profondeur et tri chronologique.
* **Calcul des métriques longitudinales** (suivi dans le temps).
* **Analyse des variations** (comparaison avec la mesure précédente).
* **Génération des états de santé** (classification métier automatisée).
* **Export optimisé** pour une visualisation fluide sur le dashboard Athlete.

---

## 📂 Input attendu

Le pipeline consomme le fichier généré lors de la phase précédente.

| Colonne | Description |
| :--- | :--- |
| `user_id` | Identifiant unique de l'athlète |
| `datetime` | Horodatage de la mesure |
| `age` | Âge chronologique |
| `body_age` | Âge métabolique calculé |
| `work_load` | Charge de travail mesurée |
| `body_toxin` | Niveau de toxines détecté |

---

## ⚙️ Pipeline de traitement

### 1️⃣ Nettoyage & Préparation
Le script assure l'intégrité temporelle pour permettre des calculs de différentiation cohérents.
* Conversion du format `datetime`.
* Tri par utilisateur puis par temps : `sort_values(["user_id", "datetime"])`.
* Suppression des colonnes redondantes pour alléger le dataset.

### 2️⃣ Body Age Processing
Le calcul repose sur la comparaison entre l'âge réel et l'âge biologique estimé.

* **Delta Biologique :** $$delta\_body\_age = body\_age - age$$

* **Classification des états (State) :**
  | Condition | État |
  | :--- | :--- |
  | $\Delta \leq -2$ | `younger_than_chrono` |
  | $-1 \leq \Delta \leq 1$ | `aligned_with_chrono` |
  | $\Delta > 1$ | `accelerated_aging` |

* **Variation Temporelle :** Calcul dynamique par rapport à la mesure $t-1$.

### 3️⃣ Workload & Toxins Processing
Classification selon des seuils de performance et de santé.

| Métrique | État (State) | Condition (Score) |
| :--- | :--- | :--- |
| **Workload** | `low_load` | $\leq 0$ |
| | `moderate_load` | $0 < x \leq 30$ |
| | `high_load` | $> 30$ |
| **Body Toxins**| `low_toxic_load` | $\leq 0$ |
| | `moderate_toxic_load`| $0 < x \leq 2$ |
| | `high_toxic_load` | $> 2$ |

---

## 🚨 Décision clé d'architecture : Suppression de la Baseline

Nous avons délibérément abandonné la logique de comparaison par rapport à la "valeur initiale" (baseline fixe) pour adopter une approche **current vs previous**.

**Pourquoi ?**
1.  **Vrai suivi longitudinal :** Capture les fluctuations réelles d'une session à l'autre.
2.  **Pertinence médicale :** Identifie les pics de fatigue immédiats plutôt que l'écart par rapport à un historique lointain.
3.  **Compatibilité Dashboard :** Permet d'afficher des indicateurs de tendance (+/-) instantanés.

---

## 📊 Dataset Final : `PerenAI_digital_twin_v1.csv`

Le fichier exporté contient les colonnes traitées prêtes pour l'affichage :

| Type | Colonnes |
| :--- | :--- |
| **Identifiants** | `user_id`, `datetime` |
| **Valeurs Actuelles** | `body_age`, `work_load`, `body_toxin` |
| **Variations ($\Delta$)** | `body_age_change`, `work_load_change`, `body_toxin_change` |
| **États Qualitatifs** | `body_age_state`, `workload_state`, `body_toxins_state` |

---
**© 2026 PEREN AI Technologies - Confidentiel**