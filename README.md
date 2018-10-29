# Linux Server project
________
## Description
In this project I setup a Linux server to host my previous project item catalog project (details below).

## Prior project
This program will run a server that pushes a database driven website that will provide the reader information on scientific awards and their recipients.
- It has full CRUD functionality on both awards and the biographies of the winners.
- CRUD functionality requires authentication
- Each database item is linked to its creator, and requires authorization of that creators login to be edited/deleted.

## Location
URL: AJLLinuxProject.net
IP address: 54.186.218.168
SSH Port: 2200

## Built with
* Ubuntu 18.04.1
* Apache 2.4.29
* Squlite 3.22.0
* SQLAlchemy 1.2.12
* Flask 1.0.2
* Oauth2client 4.1.3
* pip 9.0.1
* git

## Process
 Commands used in parenthesis ().
### Security
* Create instance of Ubuntu through AWS Lightsail
* Login
* Upgraded installed packages (apt-get update, apt-get upgrade)
* Create creator and grader Users (`addUsers`)
  * create .ssh/authenticated_keys location (`sudo mkdir`, `nano`) for both users, and transfer ownership/group (`chown`, `chgrp`)
    * Change permissions to 700 for .ssh and 644 authenticated_keys (`chmod 700/600 {file/folder_name}`)
  * create new private/public keys on local machine (`ssh-keygen`), copy public key into .ssh/authenticated_keys (`nano`)
  * Give both users sudo access in etc/sudoers.d/[name].
* Configure `ect/ssh/sshd_config` file (`nano`)
  * Change AWS Lightsail firewall under Networking tab to allow connections through port 2200.
  * change SSH port 22 to 2200 (`Port 2200`)
  * Disable ability to login as root users (`PermitRootLogin no`)
  * Force login using private key (`PasswordAuthentication no`)
  * Restart ssh (`service ssh restart`)
* Configure firewall
  * Change AWS Lightsail firewall under Networking tab to block connections through port 22.
  * Configure ufw to allow ports 2200, www(80), and 123 and deny all other incoming. (`ufw allow [port]`)
  * Start firewall (`ufw enable`)



## Server
* Install apache2 (`apt-get install apache2`)
* Install mod_wsgi (`apt-get install libapache2-mod-wsgi`)
* Install squlite (`apt-get install squlite`)
* Install pip (`apt-get install pip2`)
  * Install Flask, SQLAlchemy, git, Oauth2client (`pip2 install {item}`)

## WSGI
  * Git init in var/www/html folder
  * Link git to github
  * Port over previous catalog project
  * create myapp.wsgi file, import scienceawards.py
  * Create scienceawards.conf in apache2/sites-enabled/
    * Point WSGIScriptAlias at var/www/html folder
  * Enable configuration (`a2enconf wsgi`)
  * Restart apache2

## Google Oauth2 modifications
  * Create domain name
    * Register domain (Amazon route 53)
    * Create A record
    * Point A record at IP address
    * Create DNS zone in Lightsail, register domain with it.
    * Modify nameservers per Lightsail.
  * Register domain with Google as authorized domain.
  * Point JavaScript origins and redirects at domain.


## Course Name
Fullstack Nanodegree - Udacity

## Author
Alex Love
