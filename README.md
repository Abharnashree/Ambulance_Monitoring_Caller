Backend local setup:

Pre-requisites in machine : python (version > 3), xampp (or wampp, or lampp), Postman(desktop preferrable)

Step 1: Clone this repo : git clone https://github.com/Abharnashree/Ambulance_Monitoring.git
Step 2: navigate into the repo and create a virtual environment :
        this tutorial can be helpful : https://www.youtube.com/watch?v=Y21OR1OPC9A
        Setup and activate the virtual environment.
Step 3: Install all the packages listed in the file backend/requirements.txt
        To do that, run the following command in your terminal
        (venv)YOUR_PATH\Ambulance_Monitoring> pip install -r backend/requirements.txt    (or)
        (venv)YOUR_PATH\Ambulance_Monitoring\backend> pip install -r requirements.txt

Step 4: Also, start your apache and mysql servers(preferrably on their default ports).
        Head over to 'localhost' in your browser, and click phpMyAdmin
        Now create a new database for our server.
        reflect your changes to \__init__.py (to the database connection uri)

Step 5: Now, run the following command to start the server
        >flask run

Features:

You can utilize the /init_db_with_dummy_data to populate the db with dummy data
Use postman for requests
