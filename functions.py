from sqlalchemy import create_engine
from requests import get
import json
from datetime import datetime
from pandas import DataFrame



class QueryClient():

    def __init__(self):
        self.set_variable_defaults()
        self.load_configs()
        self.initial_setup()

    def __str__(self):
        return [self.results_dictionary, self.database_engine, self.query]

    def set_variable_defaults(self):
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
        self.query = None

    def load_configs(self, configs='config.json'):
        self.config_json = json.load(open(configs))

    def initial_setup(self): # Creates database tables and database engine object
        settings = self.config_json['database']

        database_engine = create_engine(f"{settings['dialect']}://{settings['username']}:{settings['password']}@{settings['host']}:{settings['port']}/{settings['dbname']}")
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

    def get_api_response(self): # Creates a get request for the query and returns a json
        settings = self.config_json['query']

        response = get(f'''http://api.openweathermap.org/data/2.5/air_pollution/history?lat={settings['lat']}&lon={settings['lon']}&start={settings['start']}&end={settings['end']}&appid={self.config_json['api_key']}''')

        if response.ok:
            self.query = response.json()
        else:
            print("Whoops, something went wrong: ", response.json())
        
    def add_query_to_database(self):
        if self.query == None:
            print("No query available.")
        else: 
            for item in self.query['list']:
                timestamp = item['dt']
                date_time = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

                self.results_dictionary['dt'].append(date_time)
                self.results_dictionary['aqi'].append(item['main']['aqi'])
                self.results_dictionary['latlon'].append(f'({self.query["coord"]["lat"]},{self.query["coord"]["lon"]})')

                for key, value in item['components'].items():
                    self.results_dictionary[key].append(value)

            dataframe = DataFrame(data=self.results_dictionary)
            print(dataframe)
            dataframe.to_sql('weather_readings', self.database_engine, if_exists='append', index=False)
            self.set_variable_defaults()



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
