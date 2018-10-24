# Item Catalog project
________
## Description
This program will run a server that pushes a database driven website that will provide the reader information on scientific awards and their recipients.
-It has full CRUD functionality on both awards and the biographies of the winners.
-CRUD functionality requires authentication
-Each database item is linked to its creator, and requires authorization of that creators login to be edited/deleted.


## Prerequisites
 * Python 2 [Download python 2](https://www.python.org/downloads/release/python-2713/) and install on your machine.
 * VirtualBox 5.1 [Download VirtualBox](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1) and install on your machine to run Vagrant.
 * Vagrant [Download Vagrant](https://www.vagrantup.com/downloads.html) and install on your machine.
 * Upgrade pip - run command `pip2 install --upgrade pip`
 * Use pip to install the following in the shell:
 *   `pip2 install flask packaging oauth2client redis passlib flask-httpauth`
     `pip2 install sqlalchemy flask-sqlalchemy psycopg2-binary bleach requests`

## Installation
1. Start the virtual machine in the project folder using shell command `vagrant up`.
2. Use shell command `vagrant ssh` to log in.
3. Access the files by using command `cd /vagrant`, as instructed on the screen.
4. Change directories to catalog - 'cd catalog' command in the shell.
5. Start the database (if not already present) using command `python databaseSetup.py`.
6. Run the program `python project.py`.
7. Visit the webpage via localhost:8000/awards


## Login information
*Users may read any of the informational links within the webpage, but cannot create, edit, or delete without logging in.
*Login page (/login/) will allow user to create both awards and biographies, and edit or delete any entries created by that same user.
*User may logout at any time, but will lose authorization/access privileges.
*Attempts to access material without logging in will return user to the login page.
*Attempts to access material without access privileges will be refused and rerouted to the home page. 


## Built With
* Python 2.7.12
* Flask
* SQLAlchemy
* oauth2client

## Course Name
Fullstack Nanodegree - Udacity

## Author
Alex Love
