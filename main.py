from pandas import DataFrame
from datetime import datetime
import functions
from argparse import ArgumentParser

# Arguments #
parser = ArgumentParser()
parser.add_argument('command', choices=('config', 'request'))
args = parser.parse_args()

if args.command == 'config':
    set_configs()


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
        'latlon': []
    }

    # Add information to results_dictionary
    for item in query['list']:
        timestamp = item['dt']
        date_time = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

        results_dictionary['dt'].append(date_time)
        results_dictionary['aqi'].append(item['main']['aqi'])
        results_dictionary['latlon'].append(f'({query["coord"]["lat"]},{query["coord"]["lon"]})')

        for key, value in item['components'].items():
            results_dictionary[key].append(value)

