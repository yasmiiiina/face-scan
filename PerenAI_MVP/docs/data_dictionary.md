# Data Overview — PEREN AI MVP

## Périmètre MVP
Inclus :
- données de base (âge, sexe, taille, poids)
- activité physique
- sommeil
- stress
- nutrition et habitudes
- antécédents
- cycle (profil féminin)

Exclus :
- données médicales cliniques
- prédiction médicale
- données temps réel
- multi-wearables

# 01_data_exploration  

##  Format des données
Les données sont fournies sous forme de fichier Excel.
Aucune modification n’est apportée aux données sources.
Le nettoyage et la transformation sont réalisés dans les notebooks.

##  Exploration initiale
Une exploration initiale a été réalisée afin de :
- vérifier la cohérence des données
- identifier les types de variables
- repérer les valeurs manquantes attendues (ex : cycle pour les hommes)
Aucune transformation n’a été effectuée à ce stade.

## Source des données
Les données sont fournies sous forme de fichier Excel (`Data.xlsx`) et sont
stockées dans le dossier `data/raw`.Ce fichier constitue la source de vérité et n’est jamais modifié manuellement.

---

## Description des variables
Les principales catégories de variables sont :

- Données démographiques : sexe, âge, taille, poids
- Activité physique : type de sport, fréquence /semaine
- Sommeil : durée moyenne
- Stress : niveau perçu
- Habitudes : nutrition, sédentarité, alcool
- Antécédents de santé
- Cycle (profil féminin uniquement)

La majorité des variables sont catégorielles, issues de choix fermés.

---

## Exploration initiale
Les opérations suivantes ont été réalisées :

- affichage des premières lignes du dataset
- analyse des types de données
- statistiques descriptives globales
- identification des valeurs manquantes

Les valeurs manquantes observées (ex : cycle pour les hommes) sont cohérentes
avec la structure du formulaire et attendues.

---
# Data Cleaning & Mapping 

Objectif : transformer les données brutes issues du formulaire d’assessment en un dataset propre, cohérent et exploitable, prêt à être utilisé par les étapes suivantes du MVP (Digital Twin, scores, timeline).

Aucune interprétation médicale ni calcul de score n’est effectué à ce stade.

## Data Model MVP

Le modèle de données cible du MVP est structuré au format user-centric :

user_id
sex
age
height_cm
weight_kg
bmi
activity_freq
sleep_duration
stress_level
nutrition
sedentary_time
alcohol
family_history
cycle

Ce modèle constitue la base technique du Digital Twin et sera enrichi progressivement (timeline, longitudinal, wearable data).

## Nettoyage des données

1. Normalisation des noms de colonnes

Les noms de colonnes ont été harmonisés afin de :

-respecter une nomenclature cohérente

-faciliter l’exploitation dans les étapes suivantes

-garantir la lisibilité du pipeline

Exemple :

Âge → age

Taille → height_cm

Poids → weight_kg

2. Conversion des types de données

Les variables numériques (âge, taille, poids) sont converties en formats numériques

Les variables catégorielles sont conservées sous forme de chaînes de caractères normalisées

3. Calcul des variables dérivées (neutres)
BMI (IMC)

Le BMI est calculé selon la formule standard :
 ( \text{IMC} = \frac{Poids (kg)}{(Taille (m))^2} ) 

## Mapping des variables catégorielles

Le mapping a pour objectif de :
-rendre les catégories cohérentes
-faciliter leur utilisation future dans les modèles
-préparer les indicateurs du Digital Twin

Stress:
Valeur brute	Valeur normalisée
Faible	         low
Modéré	         moderate
Élevé            high
Très élevé	     very_high

Nutrition:
Conformément à la validation métier :
Maison → equilibree
Mix maison → mixte
Les autres catégories sont conservées telles que définies dans l’assessment.

## Dataset final
Le dataset nettoyé est exporté au format CSV :
data/processed/assessment_clean.csv

### Note longitudinale
Le dataset actuel correspond à un snapshot d’assessment initial.
Le data model est conçu pour être étendu à une structure longitudinale
(30–90 jours) via l’ajout d’un index temporel (date) dans les phases suivantes.


Date: 6 Jan 2026 | Version: 1.0 | Auteur: Bouchra Sahel/ AI & Robotics Engineer