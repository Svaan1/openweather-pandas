
from functions import QueryClient
from argparse import ArgumentParser

# Arguments #
parser = ArgumentParser()
parser.add_argument('command', choices=('config', 'request'))
args = parser.parse_args()

if args.command == 'config':
    QueryClient().set_json_config_file()
elif args.command == 'request':
    #Standard use of the client
    client = QueryClient()
    client.load_configs()
    query = client.get_api_response()

    print(query.results)
    query.get_query_dataframe()
    query.create_plot()



