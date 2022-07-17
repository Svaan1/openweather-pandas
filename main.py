
from functions import QueryClient, set_json_config_file
from argparse import ArgumentParser

# Arguments #
parser = ArgumentParser()
parser.add_argument('command', choices=('config', 'request'))
args = parser.parse_args()

if args.command == 'config':
    set_json_config_file()
elif args.command == 'request':
    # Standard use of the client
    query = QueryClient()
    query.get_api_response()
    query.add_dataframe_to_database()




