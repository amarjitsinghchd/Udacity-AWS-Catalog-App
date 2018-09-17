#Items Catalog Project #

## Amarjit Singh ##
 Completed July 7, 2018
 Udacity Full Stack Nano Degree Project #
 References: Udacity and Miguel Grinberg Flask Blogs
 Google developers and Facebook developers website
 flask.pocoo.org
 stackoverflow
 file editor: sublime text
 email: amarjit_71@hotmail.com
 

# Introduction #

This project is part of Full Stack Web Developement Course. Some of the important skills and packages required to do this project are python, python packages: flask, wtfforms, sqlalchemy, oauth2-client. Other skills essenstial for this porject are javascript and ajax calls in javascript, W3C Html syntax and CSS. You will also earn how to make api calls to 3rd party javscripts like google apis and facebook for O-Auth2. Basic sqllite database was used for this project.
mySql or Maria DB Open Source database can easily replace sqlite datadase. SQLAlchemy shields this program from individual variances of databases more or less.

The application does following things:
	a) Create a Catalog list and Items for each catalog list
	b) Allows the owner of the list to modify/delete the objects
	c) All authorized users are allowed to use this
	d) Any user authenticated by Google or Facebook sign in can be added.
	e) The Webapp gives Json objects for any user. It does not need any log in for the same.

# Application Setup #

The project comes with seed files to create starter database and Vagrant Virtual Machine Set up.
High Level Steps are: 
	## a) Create Virtual Machine ##
	## b) Provision Virtual Machine ##
	## c) Set up starter/seed databases ##
	## d) Run the actual python application ##
	## e) Enjoy the app in the Webbrower at : http://localhost:5000
	## f) Exit the program and Virtual Machine when down.

# STEPS #

##STEP 1: Virtual Machine Setup##
a) Start with Vagrant file as attached here in the porject
	>vagrant up
	>vagrant provision
	>vagrant ssh

Vagrant provision is required to updated some python packages like wtfforms.

##STEP 2: Start Seeder Database##

	>cd /vagrant
	>python database_setup.py

This will create seeder mysqlite database for starting and 2 users.

##STEP 3: Run the application##

>python application.py

##STEP 4: Open the app in webbrowser: https://localhost:5000##

For Google log in to work, use localhost:5000. the IP notation does not work for Google
as Google looks for Public IP in case of http://127.0.0.1:5000. Hence it does not work.

Future, Facebook will route URL to https: only. The app will need to be updated to support https

##STEP 5: Close and Tear Down ##

>Ctrl-c
This will stop application.py
>exit
>exit
>vagrant halt

or >vagrant destroy to remove all traces of Vagrant VM. Clean Slate.


# Application Organization #

a) application.py - Main program to launch app
b) database_setup.py and starter_catalog.py - Create database structure and starter seed entries
c) client_screts.josn - part of Google Signin2/Auth. Refer to developers.google.com
d) fb_clients.json - Part of facebook sign in
e) forms.py - create form structure for the project using wtfforms and flaskform
f) Vagrantfile - For Vagrant VM setup and provisioning
g) templates - contains html templates
h) static - contains css and fonts 

