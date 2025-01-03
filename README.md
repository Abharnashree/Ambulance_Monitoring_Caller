Set up for backend (local)

Pre-requisites : python (version > 3), xampp(or wampp or lammp), postman(desktop)

Steps:

navigate into the backend folder, where you can find app.py, which the backend server.
Now to run this server, you have to install the requirements listed in the file requirements.txt.
Best practice is to setup a virtial environment and install all the requirements locally
youtute tutorial : https://www.youtube.com/watch?v=Y21OR1OPC9A

After setting up the environment and installing the requirements, run your apache and mysql services in xampp. And now in phpMyAdmin, create a database for this project and name it as 'flask' without any password(name it anything you want, but make sure to rename it in __init__.py)

Now run the following command in your terminal :
flask run

You are free to make modifications to the setup as long as you know what you are doing

happy debugging
