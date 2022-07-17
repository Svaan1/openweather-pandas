from sqlalchemy import create_engine
from requests import get
import json
from datetime import datetime
from pandas import DataFrame



class QueryClient():

    def __init__(self):
        self.load_configs()
        self.results_dictionary = {
            'dt': [],
            'aqi': [],
            'co': [],
            'no': [],
            'no2': [],
            'o3': [],
            'so2': [],
            'pm2_5': [],
            'pm10': [],
            'nh3': [],
            'latlon': []
        }

    def load_configs(self, configs='config.json'):
        self.settings = json.load(open(configs))

    def database_setup(self): # Creates database tables and database engine object
        database_settings = self.settings['database']
        database_engine = create_engine(f"{database_settings['dialect']}://{database_settings['username']}:{database_settings['password']}@{database_settings['host']}:{database_settings['port']}/{database_settings['dbname']}")
        connection = database_engine.connect()

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
            latlon point
            )''')

        self.database_engine = database_engine
    
    def get_query_dataframe(self):
        for item in self.query['list']:
            timestamp = item['dt']
            date_time = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

            self.results_dictionary['dt'].append(date_time)
            self.results_dictionary['aqi'].append(item['main']['aqi'])
            self.results_dictionary['latlon'].append(f'({self.query["coord"]["lat"]},{self.query["coord"]["lon"]})')

            for key, value in item['components'].items():
                self.results_dictionary[key].append(value)

        dataframe = DataFrame(data=self.results_dictionary)
        self.dataframe = dataframe

    def get_api_response(self): # Creates a get request for the query and returns a json
        query_settings = self.settings['query']
        response = get(f'''http://api.openweathermap.org/data/2.5/air_pollution/history?lat={query_settings['lat']}&lon={query_settings['lon']}&start={query_settings['start']}&end={query_settings['end']}&appid={self.settings['api_key']}''')
        if response.ok:
            self.query = response.json()
            self.get_query_dataframe()
        else:
            print("Whoops, something went wrong: ", response.json())

    def add_dataframe_to_database(self):
        self.database_setup()
        self.dataframe.to_sql('weather_readings', self.database_engine, if_exists='append', index=False)

def set_json_config_file():
    with open('config.json', 'r+') as json_file:
        config = json.load(json_file)
            
        print("You'll be given list of inputs, give no value to keep the existing one. ")

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

#  Functions  #
