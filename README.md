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
  <a href="https://www.python.org">
    <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white" alt="python-badge">
  </a>
  <a href="https://www.djangoproject.com">
    <img src="https://img.shields.io/badge/Django-4.0+-092E20?style=flat&logo=django&logoColor=white" alt="django-badge">
  </a>
    <a href="https://www.django-rest-framework.org/">
    <img src="https://img.shields.io/badge/DRF-3.13.1-a30000?style=flat" alt="drf-badge">
  </a>
</p>

<p align="center">
  <a href="https://black.readthedocs.io/en/stable/index.html">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="black-badge">
  </a>
    <a href="https://coverage.readthedocs.io/en/6.4.4/">
    <img src="https://img.shields.io/badge/coverage-98%25-brightgreen" alt="coverage-badge">
  </a>
</p>

# Epic Events

## Description

Project 12 OpenClassrooms Path - Epic Events -- develop a secure back-end architecture with Python and SQL

Epic Events is an Event Manager CLI program to create, update and delete employees, clients, contracts and events.

I have chosen to use the Django ORM to create my models, use BaseCommand to create, update, delete and also to display a manu. As admin tool I have used the Django admin interphase. The database is a SQLite database.
My permission system is integrated in the EpicEventCommand, where I use a class attribute 'permission' to verify if the user has the permission to access the command.

The authentication is Django based but to create a token I am using the JWT. To integrate the token into the commands, there is a JWTTokenMixin. This mixin generates a token,
verifies the token and handles the login and logout of the user.

Every employee has a specific role. The roles are SAles, SUpport and MAnagement. Every employee can make different operation within that program. This operation are permission-based
and even the menu is based on the specific role of the employee. To visualize which employee has access to which operation you can check the file: `cli/utils_menu.py.get_app_menu`.

## Installation

open terminal

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

**Option 1:**
start the program with command: `python manage.py start` and login with one of these emails:

  |   **Employee email**    |    Password     |  Role  |
  |:-----------------------:|:---------------:|:------:|
  |jason.jefferson@mail.com |  TestPassw0rd!  |   SA   |
  |   tara.nguyen@mail.com  |  TestPassw0rd!  |   SU   |
  |jennifer.white@mail.com  |  TestPassw0rd!  |   MA   |

**Option 2:**

create fake data by yourself, by running these commands:

1. `python manage.py data_create_employees` (prints one employee/user email, with Role: SA, on console to log in, password: TestPassw0rd!)
2. `python manage.py data_create_clients`
3. `python manage.py data_create_contracts`
4. `python manage.py data_create_events`
the commands to create all these data is located in `data/management/commands/`.
5. start the program with command: `python manage.py start` and login with e.g. the email which is printed on the console after you enter `python manage.py data_create_employee` command with password: `TestPassw0rd!`.

## Entity-Relationship Diagram (ERD)

realized with [Visitez](https://dbdiagram.io)

![diagram](/README_images/EpicEvents_modelDiagramm.png)

## Skill

- Implementing a secure database with Python and SQL

## Visualisation

After loging in with email and password, you will be redirected to the command: `python manage.py start` and you choose from a menu what you want to do:
![start](/README_images/EpicEvents_start.png)

Every employee, regardless of their role, can list all employees, all clients, all contracts and all events. This list appears as ready only.
![list](/README_images/EpicEvents_listEmployees.png)

As described every employee can list all, but certain can filter further. After the listing of the model, an input appears to ask if this employee wants to filter.
If the employee chooses 'yes' and have the permission to filter, the employee can filter the model.
![list_filter](/README_images/EpicEvents_listContracts.png)

After choosing to filter and permission granted, the employee can choose one to several model attributes to filter the events.
![filter](/README_images/EpicEvents_filterEvents.png)

This picture demonstrate the creation of a client.
![create](/README_images/EpicEvents_createClient.png)

To update a model instance, a little table displays all details of the model instance. The employee can choose, from one to multiple, which field the employee wants to update.
The updated data will be displayed right after the update of the model instance.
![update](/README_images/EpicEvents_updateContract.png)

To demonstrate the data creation:
![data](/README_images/EpicEvents_data_creation.png)
