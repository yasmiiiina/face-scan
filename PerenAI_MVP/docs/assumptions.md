# PEREN AI — Assumptions & Hypotheses (MVP Phase 2)

**Projet**: PEREN AI — Digital Health Twin  
**Phase**: Feature Engineering (Semaine 3–5)  
**Version**: v1.0  
**Auteur**: Bouchra Sahel  
**Date**: 16 Janvier 2026  

---

## 1. Contexte général

Ce document décrit les **hypothèses**, **choix méthodologiques** et **limitations connues**  
liées au calcul des premiers indicateurs MVP :

- Body Age  
- Work Load  
- Body Toxins  

Ces scores sont calculés à partir des données issues du formulaire d’assessment PEREN AI  
`assessment_clean.csv`.


---

## 2. Principes globaux (communs à tous les scores)

### 2.1 Données manquantes
- Toute variable non disponible dans l’assessment actuel est :
  - intégrée avec une **valeur neutre (score = 0)**

➡️ Objectif : éviter le blocage du pipeline et permettre l’évolution future.

---


### 2.2 Architecture évolutive
Les scores sont conçus pour être enrichis ultérieurement via :
- données longitudinales (30–90 jours)
- wearables / devices (FC, HRV, sommeil réel)
- modules additionnels (cardio, récupération, hormonal, etc.)

---

## 3. Body Age — Hypothèses

### 3.1 Objectif
Estimer un **âge biologique approximatif** à partir de facteurs lifestyle  
en comparaison avec l’âge chronologique.

---

### 3.2 Variables utilisées
- Âge chronologique
- Activité physique (fréquence)
- IMC (calculé à partir taille / poids)
- Sommeil (durée moyenne)
- Stress perçu
- Qualité de l’alimentation (poor, mixed and equilibrated)

---

## 4. Work Load — Hypothèses

### 4.1 Objectif
Estimer la **charge globale supportée par l’organisme**,  
en tenant compte de l’activité et des facteurs de récupération.

---

### 4.2 Variables utilisées
- Fréquence d’activité sportive
- Stress perçu
- Dette de sommeil (< 6h)

---


### 4.3 Variables non disponibles (neutres)
- Intensité sportive

➡️ Ces variables sont fixées à un score neutre (0) en MVP.

---

## 5. Body Toxins — Hypothèses

### 5.1 Objectif
Estimer l’**exposition globale aux facteurs toxiques lifestyle**,  
contrebalancée par des comportements protecteurs.

---

### 5.2 Variables utilisées
- Qualité de l’alimentation
- Consommation d’alcool
- Activité physique (effet protecteur)

---

### 5.3 Variables non disponibles (neutres)
- Hydratation réelle

➡️ Ces variables sont fixées à un score neutre (0) en MVP.

---

## 6. Scores reportés

### 6.1 Energy
- Aucune formule validée dans le document d’assessment actuel
- Score **non calculé** en Phase 2

---

### 6.2 Recovery
- Trop de variables manquantes (âge pondéré, charge cumulée, sommeil profond, etc.)
- Score **non calculé** en Phase 2

---

### 6.3 Sync Cycle
- Données insuffisantes (symptômes, hormones, tracking)
- Score **reporté à une phase ultérieure**

---


**Fin du document**
