from sqlalchemy import create_engine
from requests import get
import matplotlib.pyplot as plt
import json
from datetime import datetime
from pandas import DataFrame

class QueryClient():
    def __init__(self):
        self.settings = {
            "api_key": "",
            "database": {
                "dialect": "",
                "username": "",
                "password": "",
                "host": "",
                "port": "",
                "dbname": ""
            },
            "query": {
                "lat": "",
                "lon": "",
                "start": "",
                "end": ""
            }}

    def set_json_config_file(self):
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
            nh3 real
            )''')

        return database_engine

    def get_api_response(self): # Creates a get request for the query and returns a json
        query_settings = self.settings['query']
        response = get(f'''http://api.openweathermap.org/data/2.5/air_pollution/history?lat={query_settings['lat']}&lon={query_settings['lon']}&start={query_settings['start']}&end={query_settings['end']}&appid={self.settings['api_key']}''')
        if response.ok:
            return QueryResult(response.json(), self.database_setup())
        else:
            print("Whoops, something went wrong: ", response.json())


class QueryResult():
    def __init__(self, query, database_engine):
        self.results = query
        self.dataframe = None
        self.database_engine = database_engine
    
    def get_query_dataframe(self):
        results_dictionary = {
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
        }
        for item in self.results['list']:
            timestamp = item['dt']
            date_time = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

            results_dictionary['dt'].append(date_time)
            results_dictionary['aqi'].append(item['main']['aqi'])

            for key, value in item['components'].items():
                results_dictionary[key].append(value)

        self.dataframe = DataFrame(data=results_dictionary)

    def add_dataframe_to_database(self):
        if not self.dataframe:
            print("No dataframe, yet. Run get_query_dataframe first!")
            return
        self.dataframe.to_sql('weather_readings', self.database_engine, if_exists='append', index=False)

    def create_plot(self):
        dataframe = self.dataframe
        plt.subplot(3, 1, 1)
        plt.plot("dt", "co", "", data=dataframe, label="co levels")
        plt.ylabel("Co levels in μg/m3")
        plt.title("Air pollution levels")

        plt.subplot(3, 1, 2)
        plt.plot("dt", "o3", "", data=dataframe, label="o3 levels")
        plt.ylabel("O3 levels in μg/m3")

        # I can improve this repetition
        plt.subplot(3, 1, 3)
        plt.plot("dt", "no", "", data=dataframe, label="no levels")
        plt.plot("dt", "no2", "", data=dataframe, label="no2 levels")
        plt.plot("dt", "so2", "", data=dataframe, label="so2 levels")
        plt.plot("dt", "pm2_5", "", data=dataframe, label="pm2_5 levels")
        plt.plot("dt", "pm10", "", data=dataframe, label="pm10 levels")
        plt.plot("dt", "nh3", "", data=dataframe, label="nh3 levels")
        plt.xlabel("Datetime")
        plt.ylabel("Pollutant concentration in μg/m3")
        plt.legend()

        plt.show()