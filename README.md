# OC-P12 : EPICEVENT - Développez une architecture back-end sécurisée avec Python et SQL

<p align="center">
  <img src="IMG/logo_light.png#gh-light-mode-only" alt="logo-light" />
  <img src="IMG/logo_dark.png#gh-dark-mode-only" alt="logo-dark" />
</p>

![logo](IMG/Logo_EpicEvents.png)

[![forthebadge](https://forthebadge.com/images/badges/cc-0.svg)](https://forthebadge.com)
[![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com)
[![forthebadge](https://forthebadge.com/images/badges/built-with-love.svg)](https://forthebadge.com)
[![forthebadge](https://forthebadge.com/images/badges/made-with-markdown.svg)](https://forthebadge.com)
[![forthebadge](https://forthebadge.com/images/badges/code-style-black.svg)](https://forthebadge.com)
[![forthebadge](https://forthebadge.com/images/badges/made-in-python.svg)](https://forthebadge.com)

<p align="center">
    <a href="https://www.djangoproject.com">
    <img src="https://img.shields.io/badge/Django-4.0+-092E20?style=flat&logo=django&logoColor=white" alt="django-badge">
  </a>
    <a href="https://www.django-rest-framework.org/">
    <img src="https://img.shields.io/badge/DRF-3.13.1-a30000?style=flat" alt="drf-badge">
  </a>
</p>

<p align="center">
    <a href="https://coverage.readthedocs.io/en/6.4.4/">
    <img src="https://img.shields.io/badge/coverage-98%25-brightgreen" alt="coverage-badge">
  </a>
</p>

# Epic Events

## Description

Projet 12 du parcours OpenClassrooms - Epic Events -- développer une architecture back-end sécurisée avec Python et SQL

Epic Events est un programme CLI de gestion d'événements permettant de créer, mettre à jour et supprimer des employés, des clients, des contrats et des événements.

J'ai choisi d'utiliser l'ORM Django pour créer mes modèles, utiliser BaseCommand pour créer, mettre à jour, supprimer et également afficher un menu. En tant qu'outil d'administration, j'ai utilisé l'interface d'administration Django. La base de données est un Postgres SQL.
Mon système de permissions est intégré dans EpicEventCommand, où j'utilise un attribut de classe 'permission' pour vérifier si l'utilisateur a la permission d'accéder à la commande.

L'authentification est basée sur Django mais pour créer un jeton j'utilise le JWT. Pour intégrer le jeton dans les commandes, il y a un JWTTokenMixin. Ce mixin génère un jeton, vérifie le jeton et gère la connexion et la déconnexion de l'utilisateur.

Chaque employé a un rôle spécifique. Les rôles sont Vente, Support et Management. Chaque employé peut effectuer différentes opérations dans ce programme. Ces opérations sont basées sur les permissions et même le menu est basé sur le rôle spécifique de l'employé. Pour visualiser quel employé a accès à quelle opération, vous pouvez consulter le fichier : `cli/utils_menu.py.get_app_menu`.

## Installation

Ouvrir un terminal

1. `git clone https://github.com/Matthiiews/Project12_EpicEvents.git`
2. `cd Project12_EpicEvents`
3. `pipenv install`
4. `pipenv shell`
5. `pip install -r requirements.txt`
ou
6. `git clone https://github.com/Matthiiews/Project12_EpicEvents.git`
7. `cd Project12_EpicEvents`
8. `python3 -m venv venv`
9. `. venv/bin/activate` on MacOS and Linux `venv\Scripts\activate` on Windows
10. `pip install -r requirements.txt`
11. `python manage.py makemigrations`
12. `python manage.py migrate`

**Option 1:**
Démarrer le programme avec la commande : `python manage.py start` et connectez-vous avec l'un de ces e-mails :

  |   **Employee email**    |    Password     |  Role  |
  |:-----------------------:|:---------------:|:------:|
  |jason.jefferson@mail.com |  TestPassw0rd!  |   SA   |
  |   tara.nguyen@mail.com  |  TestPassw0rd!  |   SU   |
  |jennifer.white@mail.com  |  TestPassw0rd!  |   MA   |

**Option 2:**

Générer des données fictives vous-même, en exécutant ces commandes:

1. `python manage.py data_create_employees` (Affiche un e-mail d'employé/utilisateur, avec le rôle : SA, sur la console pour se connecter, mot de passe : TestPassw0rd!)
2. `python manage.py data_create_clients`
3. `python manage.py data_create_contracts`
4. `python manage.py data_create_events`
Les commandes pour créer toutes ces données sont situées dans `data/management/commands/`.
5. démarrer le programme avec la commande: `python manage.py start` et connectez-vous avec par exemple l'e-mail qui est imprimé sur la console après avoir entré `python manage.py data_create_employee` la commande avec le mot de passe: `TestPassw0rd!`.

## Diagramme Entité-Relation (ERD)

réalisé avec [Visitez](https://dbdiagram.io)

![diagram](/IMG/EpicEvents_ERD.png)

## Skill

- Implémentation d'une base de données sécurisée avec Python et SQL

## Visualisation

Après vous être connecté avec votre email et votre mot de passe, vous serez redirigé vers la commande : `python manage.py start`, et vous choisirez à partir d'un menu ce que vous souhaitez faire.:
![start](/IMG/EpicEvents_start.PNG)

Chaque employé, quel que soit son rôle, peut lister tous les employés, tous les clients, tous les contrats et tous les événements. Cette liste apparaît en lecture seule.
![list](/IMG/EpicEvents_listEmployees.PNG)

Comme décrit, chaque employé peut lister tout, mais certains peuvent filtrer davantage. Après l'énumération du modèle, une saisie apparaît pour demander si cet employé souhaite filtrer. Si l'employé choisit 'oui' et a la permission de filtrer, l'employé peut filtrer le modèle.
![list_filter](/IMG/EpicEvents_listContracts.PNG)

Après avoir choisi de filtrer et obtenu l'autorisation, l'employé peut choisir un ou plusieurs attributs du modèle pour filtrer les événements.
![filter](/IMG/EpicEvents_filterEvents.PNG)

Cette image illustre la création d'un client.
![create](/IMG/EpicEvents_createClient.PNG)

Pour mettre à jour une instance de modèle, une petite table affiche tous les détails de l'instance du modèle. L'employé peut choisir, d'un à plusieurs, les champs qu'il souhaite mettre à jour.
Les données mises à jour seront affichées immédiatement après la mise à jour de l'instance du modèle.
![update](/IMG/EpicEvents_updateContract.PNG)

Pour démontrer la création de données :
![data](/IMG/EpicEvents_data_creation.PNG)
