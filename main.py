
from functions import QueryClient, set_configs
from argparse import ArgumentParser

# Arguments #
parser = ArgumentParser()
parser.add_argument('command', choices=('config', 'request'))
args = parser.parse_args()

if args.command == 'config':
    set_configs()


elif args.command == 'request':

    # Standard use of the client
    query = QueryClient()
    query.initial_setup()
    query.get_api_response()
    query.add_query_to_database()
