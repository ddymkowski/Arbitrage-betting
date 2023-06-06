import requests
import json

x = requests.get('https://offer.lvbet.pl/client-api/v3/matches/competition-view/?date_from=2023-06-05%2000%3A00&date_to=2023-06-10%2000%3A00&lang=en&sports_groups_ids=1&sports_groups_ids=36530&sports_groups_ids=37609',
                 headers={'Accept': 'application/json'})




data = x.json()


matches_dict = {i['match_id']:i for i in data['matches']}
# primary_column_markets_dict = {i['match_id']:i for i in data['primary_column_markets']}


# cwel = merge_dicts(matches_dict, primary_column_markets_dict)
from pprint import pprint
# pprint(primary_column_markets_dict['bc:22384587'])



for i in data['primary_column_markets']:
    if i['match_id'] == 'bc:22384587' and i['name'] == 'Match Result':
        pprint(i)
        print('~~~~~~~~~~~~~~~~~~~~')

# with open('data.json', 'w') as f:
#     json.dump(x.json(), f)
#

# https://offer.lvbet.pl/client-api/v3/markets/bc:1236573993?lang=pl



# curl -X 'GET' \
#   'https://offer.lvbet.pl/client-api/v3/markets/bc%3A1235315351' \
#   -H 'accept: application/json'