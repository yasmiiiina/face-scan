# PEREN AI – Digital Twin Dashboard (Phase 4)

**Auteur : Bouchra Sahel**  
**Rôle : AI / Data Engineer – Digital Twin Modeling**  

© 2026 PEREN AI Technologies. Tous droits réservés.  
PEREN AI® est une marque déposée de PEREN AI Technologies et ne peut être utilisée sans autorisation.  
🌐 www.peren.ai

---

# 🎯 Objectif de la phase 4

Cette phase a pour objectif de :

👉 Transformer les indicateurs de santé calculés (Phase 2 & 3)  
👉 en une **interface visuelle interactive (Dashboard)**  
👉 permettant de **lire l’évolution du Digital Twin dans le temps**

Le dashboard sert de :

- outil de suivi longitudinal
- support décisionnel
- base MVP pour démonstration client
- fondation pour la future plateforme PEREN AI

---

# 🧠 Rappel des phases précédentes

## Phase 2 — Scores physiologiques
Calcul des indicateurs :

- Body Age
- Work Load
- Body Toxins

## Phase 3 — Digital Twin v1
Ajout de :

- Timeline (multi-dates)
- Baseline individuelle
- Changements entre périodes (Δ)
- États corporels interprétables
- Dataset longitudinal final

Sortie :
PerenAI_digital_twin_v1.csv


---

# 🚀 Phase 4 — Dashboard

## ✅ Ce qui a été réalisé

### 1. Création d’un dashboard interactif
Développé avec :
- Streamlit
- Pandas

Permet :

✔ Sélection d’un utilisateur  
✔ Visualisation des métriques santé  
✔ Suivi temporel  
✔ Lecture simple et médicale  

---

### 2. Profil utilisateur affiché

Affichage :

- Sexe
- Âge chronologique
- Body Age
- Différence Body Age – Âge réel
- Date du dernier assessment

Objectif :
👉 contextualiser immédiatement l’état du patient

---

### 3. KPIs principaux (vs période précédente)

Pour chaque indicateur :

- Body Age
- Work Load
- Body Toxins

On affiche :

Valeur actuelle + Δ (change)

Exemple :
Body Age : 39 (+1)


Interprétation :
- + → dégradation
- – → amélioration
- 0 → stable

⚠️ Important :  
On utilise **le changement vs dernière mesure**  
(et non une baseline fixe)

Cela correspond mieux à :
👉 un suivi médical réel

---

### 4. États corporels

Chaque score est traduit en état lisible :

Exemples :

- aligned_with_chrono
- accelerated_aging
- moderate_load
- high_toxic_load

Objectif :
👉 interprétation non technique

---

### 5. Timeline longitudinale

Graphiques :

- Body Age
- Work Load
- Body Toxins

Permet de voir :

- tendances
- dérives
- signaux faibles
- progression

C’est le cœur du **Digital Twin dynamique**.

---

### 6. Historique complet

Tableau brut affiché :

- toutes les dates
- toutes les valeurs
- utile pour validation médicale

---
Date: 16 Feb 2026 | Version: 1.0 | Auteur: Bouchra Sahel/ AI & Robotics Engineer