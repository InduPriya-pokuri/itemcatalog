# Item-Catalog

## By Pokuri InduPriya

This web application is a project for the Udacity [FSND Course](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004)

## About Project

This Project is a RESTful web application utilizing the Flask Framework which accesses a SQL database that populates  Restaurant categories and their Restaurant Menu Items information. OAuth2 provides authentication for furuther CRUD functionality on the application. Currently OAunt2 is implemented for Google Accounts.

## In This Project

This project has one main python module `project.py` which runs the flask application. A SQL database is created using the `database_setup.py` module and you can populate the database with test data using `restaurent_info.py`

The Flask application uses stored HTML templates in the templates directory to build the front-end of application.

## Software Requirements

--> Python3
--> VirtualBox
--> Vagrant
--> Git
--> SQLite DB
--> Text Editor(Sublime Text3)

## Required Skills

--> Python3
--> HTML
--> CSS
--> Bootstrap
--> OAuth
--> Flask Framework
--> sqlalchemy

## Features

--> Authentication and authorisation check
--> Full CRUD support using SQLAlchemy and Flask
--> JSON endpoints.
--> Implements oAuth using Google Sign-in API

## Installation
There are some dependancies and few instructions on hoee to run the application. Seperate instructions are provided to get GConnect working also.

## URL's

* [Git](https://git-scm.com/downloads)
* [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
* [Vagrant](https://www.vagrantup.com/)
* [Vagrantfile](https://https://github.com/udacity/fullstack-nanodegree-vm)
* [Sublime Text](https://www.sublimetext.com/3)
* [python](https://www.python.org)

## Installation Process

step 1: Install Git, Sublime text, VirtualBox and Vagrant , Python3
step 2:Clone the Udacity Vagrantfile
step 3:Goto Vagrant dictory and download the zip file and place here 
step 4:Open terminal or git
step 5:Launch the Vagrant VM(`vagrant up`)
step 6:Run Vagrant VM(`vagrant ssh`)
step 7:Now change the directory into vagrant folder i.e., `cd /vagrant`
step 8:The application imports requests which is not on this vm. Run pip install 		   requests

## Some dependencies libraries

* pip install Flask
* pip install sqlalchemy
* pip install requests
* pip install psycopg2
* pip install oauth2client

## How to run python files

--> Here we are creating three different files
	
	* database_setup.py - It is a database file. In this database files I have created Restaurent and MenuItems tables.

	* restaurent_info.py - In this file we are inserting sample data.

	* project.py - It is main file for running application.

--> Now open git or terminal and inside project folder type python filename.py, 
	1. python database_setup.py
	2. python restaurent.py
	3. python project.py

## Using Google Login
To get the Google login working there are a few additional steps:

1. Goto [Google Dev Console](https://console.developers.google.com)
2. Login if prompted
3. Goto Credentials
4. Select Create Credentials
5. Select OAuth Client ID
6. Select Web Application Name
7. Enter Application Name 'Cricket Player Item-catalog'
8. Authorized JavaScript origins = 'http://localhost:5050'
9. Authorized redirect URLs = 'http://localhost:5000/login' && 'http://localhost:5000/gconnect'
10. Select Create
11. Select Create ID and Paste it into the `data-clientID` in login.html
12. On the Dev Console Select and Download JSON
13. Rename JSON file to client_secrets.json 
14. Place JSON file in item-catalog directory that you 
15. Run application using `python /item-catalog/project.py`

## JSON Endpoints

The following are open to the public:

Restaurent Catalog JSON: `http://localhost:5000/restaurants/JSON'`
	
	- It displays the whole restaurant catalog. Restaurent categories and all menuitems.

MenuItemwise JSON: `http://restaurants/<int:rest_id>/menu/<int:menu_id>/JSON`

    - Based on MenuItem id it  will displays all menu items in particular restaurant.

Restaurent of particular Menu Item details JSON: `localhost:5000/restaurants/<int:rest_id>/menus/JSON'`

    - it displays the particular restaurent of particulr menu item information.


## Miscellaneous

This project is inspiration from [gmawji](https://github.com/gmawji/item-catalog).
