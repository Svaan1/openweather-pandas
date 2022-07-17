from sqlalchemy import create_engine
from requests import get
import json

config_json = json.load(open('config.json'))

#  Functions  #
def set_configs():
    with open('config.json', 'r+') as json_file:
        config = json.load(json_file)

        # Set API key
        new_api_key = input("Specify user's api key: ")
        if new_api_key != "": config['api_key'] = new_api_key

        # Set database values
        for key in config['database'].keys():
            new_value = input(f"Specify the user's database {key}: ")
            if new_value != "":
                config['database'][key] = new_value

        # Set query values
        for key in config['query'].keys():
            new_value = input(f"Specify the query's desired {key}: ")
            if new_value != "": 
                config['query'][key] = new_value
        
        # Save json changes
        json_file.seek(0)
        json.dump(config, json_file, indent= 4)
        json_file.truncate()

def initial_setup():
    # Load database settings from json
    settings = config_json['database']

    # Loads up and connects database
    database_engine = create_engine(f"{settings['dialect']}://{settings['username']}:{settings['password']}@{settings['host']}:{settings['port']}/{settings['dbname']}")
    connection = database_engine.connect()

    # Table create
    connection.execute('''CREATE TABLE IF NOT EXISTS weather_readings (
        dt timestamp, 
        aqi smallint,
        co real,
        no real,
        no2 real,
        o3 real,
        so2 real,
        pm2_5 real,
        pm10 real,
        nh3 real,
        latlon point,
        CONSTRAINT unique_timestamps UNIQUE (dt)
        )''')
    return database_engine

def get_api_response():
    # Loads up query settings from json 
    settings = config_json['query']

    # Get request with given query
    query_results = get(f'''http://api.openweathermap.org/data/2.5/air_pollution/history?lat={settings['lat']}&lon={settings['lon']}&start={settings['start']}&end={settings['end']}&appid={config_json['api_key']}''').json()

    return query_results