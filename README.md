
# City Weather Data API

Author: Alex Escalante Sanchez
- alexandurs@gmail.com 

https://www.linkedin.com/in/alex-escalante-sanchez-1679a8141/

This project is an API to fetch, store, and retrieve weather data from OpenWeatherMap and Yandex for multiple cities. The API is built using FastAPI, and Celery is used for scheduled weather updating tasks. The data is stored in a PostgreSQL database. This project is for demo purposes and is not intended for production use.

## Requirements (detailed information on requirements can be found in requirements.txt)

- Python 3.*
- PostgreSQL >=9.5
- rabbitmq-server
- A google maps API key, a 3 month free trial can be obtained on https://console.cloud.google.com/

## Installation.

1. Clone the repository:

`git clone https://github.com/Alexbdengineer/improvado_project.git`

2. Create and activate a virtual environment:

- `sudo apt update`
- `sudo apt install python3.11-venv`
- `python3 -m venv env`
- `source env/bin/activate`

3. Install the required packages:

- `pip install -r requirements.txt`
- `sudo apt update`
- `sudo apt-get install rabbitmq-server`
- `sudo systemctl start rabbitmq-server`

4. Setup the postgresql database:

- `sudo apt update`
- `sudo apt-get install postgresql postgresql-contrib`
- `sudo service postgresql start`
- `sudo su - postgres`
- `psql`
- `CREATE USER your_postgres_user WITH PASSWORD 'your_postgres_password';`
- `CREATE DATABASE your_postgres_db WITH OWNER your_postgres_user;`
- `exit`
- `exit`

5. Configure the app:

Create a file config.py with your actual values and API keys. A sample_config.py file is included for your reference. Once the config.py file is updated, run the database.py script.
- `python3 database.py`

## Running the application.

The application requires three shells to run the main app, the Celery worker, and the Celery scheduler:

1. Start the main app (Shell 1):

- `source env/bin/activate`
- `uvicorn main:app --host 0.0.0.0 --port 8000`

2. Celery worker (Shell 2):
- `source env/bin/activate`
- `celery -A celery_app:app worker --loglevel=info --concurrency=1`

**Note**: This has not been tested with concurrency higher than 1 as of this version.

3. Celery scheduler (Shell 3):
- `source env/bin/activate`
- `celery -A celery_app beat --loglevel=info`


## API Endpoints.

FastAPI provides automatic API documentation, which can be accessed at http://localhost:8000/docs.

You can interact with the API using the following endpoints:

1.  Get cities list.

Method: GET 

Endpoint: /api/v1/cities/

Example curl:

`curl -X GET "http://localhost:8000/api/v1/cities/"`

2. Add a new city with its name.

Method: POST 

Endpoint: /api/v1/cities/  

Request body: {"name": "City name"}

Example curl:

`curl -X POST "http://localhost:8000/api/v1/cities/" -H "Content-Type: application/json" -d '{"name": "Cancun"}'`

3. Get city Weather.

Method: GET

Endpoint: /api/v1/cities/{city_name}/

Example curl:

`curl -X GET "http://localhost:8000/api/v1/cities/{"Cancun"}/"`

4. Get city weather specifying time.

Method: GET

Endpoint: /api/v1/cities/{city_name}/time/

Example curl:

`curl -X GET "http://localhost:8000/api/v1/cities/{"Cancun"}/?weather_time=2023-04-19T00:30:01"`




