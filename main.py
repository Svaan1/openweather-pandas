
from functions import QueryClient
from argparse import ArgumentParser

# Arguments #
parser = ArgumentParser()
parser.add_argument('command', choices=('config', 'request'))
args = parser.parse_args()

if args.command == 'config':
    QueryClient().set_json_config_file()
elif args.command == 'request':
    # Standard use of the client
    client = QueryClient()
    client.load_configs()
    query = client.get_api_response() # Make an object for query results with add dataframe as its own function
    client.add_dataframe_to_database(query) # So it should look like query.add_dataframe_to_database()  
                                            # And creating it would be like Query(dataframe)
    




