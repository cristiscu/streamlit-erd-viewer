Streamlit ERD Viewer
====================

Simple Entity-Relationship diagram generator and viewer for any database schema from your Snowflake account. Can show tables only, or tables with columns (and optional data types). It generates as well the create DDL script.

Can be installed right away as a Streamlit App in your Snowflake account. Or tested locally as a Streamlit web application.

Instructions
------------

To connect locally from the web app to your Snowflake account:

* In a new **profile_db.conf** file, create a valid entry with your Snowflake account number, and the user name, following the **profiles_db_template.conf** format.
* Set a **SNOWFLAKE_PASSWORD** environment variable with your password.

To test and run the Streamlit application locally, on Windows, in VSCode or your own Python IDE:

* Clone this repository on your local machine, then open the IDE with the folder of this project.
* Make sure you have installed a Python version supported by Snowpark (v8, v9, or v10 at this moment).
* In a Terminal window, create a virtual environment with **`python -m venv venv`**.
* Switch to this new environment with venv/scripts/activate.
* Run **`pip install -r requirements.txt`**, to install the Snowpark and Streamlit dependencies.
* Call **`streamlit run main.py`** to open the web app in your browser.
* When done, type **CTRL+C** in the Terminal to stop the web app.

To install and run this as a Streamlit app in your Snowflake account:

* Paste and run the **chinook.sql** script in a new worksheet, to create an empty Chinook sample database.
* In a new database (and schema), create a new Streamlit app with the default template.
* Replace the Python code with the full content of our **main.py** file.
* Test and run the Streamlit app online.
