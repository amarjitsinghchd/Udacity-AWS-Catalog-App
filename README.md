#Linux Server Configuration and Launch Catalog App

## Amarjit Singh 
 Initial Submmission Sep 19, 2018
 Udacity Full Stack Nano Degree Project 
 References: Udacity Videos and Linux Server Configuration
 

## Introduction 

This project is the last project of Full Stack Web Developement Course. This project focuses on using getting bare metal Linux Server and configuring its ports and access and launching the catalog app created earlier in the course. The project uses [AWS LightSail server](lightsail.aws.amazon.com)

## Server Public IP 

Server is available at IP Address:
52.88.221.69

SSH Port: 2200

Server Domain name:

www.52.88.221.69.xip.io

Note: Domain Name must be used for Google log in to work. Google log in redirect does not work on IP address also.
 Facebook log in requires https. The original project was done without https. Facebook API does not support http anymore.

## Softwares Installed

###STEP 1: Configure Instance on AWS Light Sail with Ubuntu 18.04.1 LTS. Download ssh key from AWS Webport for terminal log in.

###STEP 2: Install Apache (sudo apt-get install apache2) and Configure Firewall per project requirements (ufw)

###STEP 3: Install git (sudo apt-get install git)

###STEP 4: Get Catalog project created in Module 3 from GitHub

git clone https://github.com/amarjitsinghchd/Project-Catalog-FullStack-Udacity.git 

###STEP 5: Create Python Virtual Env. The project was created in Python 2.7 while AWS came with default Python 3.
So some additional changes on Print statements and from refernces have to be adjusted to make it. 
Virtual Env involved installating following python packages. Most of the packages were from required to support the original project except 2to3 that was used to convert old project from 2.t to Python 3.
				2to3==1.0
				cachetools==2.1.0
				certifi==2018.8.24
				chardet==3.0.4
				click==6.7
				Flask==1.0.2
				Flask-SQLAlchemy==2.3.2
				Flask-WTF==0.14.2
				google-api-python-client==1.7.4
				google-auth==1.5.1
				google-auth-httplib2==0.0.3
				httplib2==0.11.3
				idna==2.7
				itsdangerous==0.24
				Jinja2==2.10
				MarkupSafe==1.0
				oauth2==1.9.0.post1
				oauth2client==4.1.3
				pkg-resources==0.0.0
				psycopg2==2.7.5
				psycopg2-binary==2.7.5
				pyasn1==0.4.4
				pyasn1-modules==0.2.2
				requests==2.19.1
				rsa==4.0
				six==1.11.0
				SQLAlchemy==1.2.11
				uritemplate==3.0.0
				urllib3==1.23
				Werkzeug==0.14.1
				WTForms==2.2.1

###STEP 6: Debug and Make sure application.py runs as local server in python3. 
I was not able to get xterm windows to run and see local webserver to make sure all code is working.

###STEP 7: Install Mod_Wsgi module that will allow interfece between apache and python/flask application. This need good read on mod_wsgi.io documentation and other references like

https://modwsgi.readthedocs.io/en/develop/

https://www.digitalocean.com/community/tutorials/how-to-serve-django-applications-with-apache-and-mod_wsgi-on-ubuntu-14-04

###STEP 8: Configure Apache config file to server the app.

		sudo nano /etc/apache2/sites-available/000-default.conf

		Adding the follwing to the above file:

		'
		 <Directory /home/ubuntu/catalog/myproject>
		        <IfVersion < 2.4>
		        Order allow,deny
		        Allow from all
		        </IfVersion>
		        <IfVersion >= 2.4>
		        Require all granted
		        </IfVersion>
		        </Directory>

		        # set home to project files dir. This will help loading python user modules
		        WSGIDaemonProcess mycatalogproject home=/home/ubuntu/catalog/myproject  python-path=/home/ubuntu/catalog python-home=/home/ubuntu/catalog/venv
		        WSGIProcessGroup mycatalogproject

		        WSGIScriptAlias / /home/ubuntu/catalog/myproject/myapp.wsgi

		        ServerAdmin webmaster@localhost
		        DocumentRoot /var/www/html

		'
		Make sure apache has read / write permissions and proper group ownership

###STEP 9: Create myapp.wsgi file in project directory to point to original python application file.

		''
		import sys

		# add path to where flask project is located.

		sys.path.append('/home/ubuntu/catalog/myproject')

		from application import app as application
		''

		The wsgi file is the entry point of the wsgi and then it import
		app from original Flask application app as application

		Also, when you start wsgi, there is really no sys path defined and hence
		you have issues importing other python modules.s 

One of the issues was session was global variable in original python project and it created conflicts. Session is created from sessionmaker (sessionmaker is like factory per documentation) and closed when not need or commit takes care of that. This caused application not to work in the beginning

###STEP 10: Server Reboot / Service Restart

Reboot server (Mod_wsgi may actup when you started with some errors on config file initiallly). Normally apache2 service restart works for most changes.

At this point the web application must be running.

###STEP 11: Database update form sqlite to postgresql

Install Postgresql, create database and database user catalog and enable password for that user.
Make database engine updates on python file to connect to postgresql.
Test this database

### STEP 12: Update Google Log in

Update Google developers to have new host instead of localhost before.

### STEP 13: Facebook Update (Not working)

FB log in was freezing but worked after changing to https on AJAX. It still needs secure https website. This is not part of the course.

### STEP 14: Grader User
Create user grader on ubuntu and generate key-pair.  Copy pub key to server.
Leave private key for the grader.


### DONE !


