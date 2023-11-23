<div align='center'>
<h1>Welcome to RDX Solutions</h1>
</div>

![](rdx.gif)



## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

<h2>Prerequisites</h2>

[`Python`](https://www.python.org/downloads/), [`Django`](https://www.djangoproject.com/download/), [`pip`](https://pypi.org/project/pip/)

## Installation and Setup:
**1.Clone the Repository**
```sh
https://gitlab.liu.se/tddc88-2022/c4/rdx-solutions-backend-project.git
```
**2.Navigate to the Project Folder**
```sh
cd Web/

```
**3.Setup Virtual Environment and Install Requirements**
```sh
python3 -m venv venv
source venv/bin/activate - Mac 
source venv/Scripts/activate - Windows 
pip install -r requirements.txt

```
**4.Create a Superuser and Provide Login Details**
```sh
python3 manage.py createsuperuser
Username: example
Email address: example@gmail.com
Password: *****
```
**5.Migrate Database**
```sh
python3 manage.py makemigrations
python3 manage.py migrate
```
**6.Start Server**
```sh
python manage.py runserver
```
**7.Enter the site and login with provided credentials**
```sh
http://127.0.0.1:8000/admin/
```
## Architecture and schema is available at 
https://app.diagrams.net/#G1wfihktfheNB74xuKVK3J80uDa2fYga5N
