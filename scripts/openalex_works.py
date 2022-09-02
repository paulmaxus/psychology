import pandas as pd
import requests
import json
import config


base_url_works = 'https://api.openalex.org/works'


def get_works(works_filter, cursor='*'):
    # works_filter: e.g.
    # f'authorships.institutions.ror:{ror},publication_year:{year}'
    params = {
        'per-page': 100,
        'mailto': config.email,
        'filter': works_filter,
        'cursor': cursor
    }
    r = requests.get(base_url_works, params)
    data = r.json()
    results = data['results']
    if data['meta']['next_cursor']:
        results.extend(get_works(works_filter, data['meta']['next_cursor']))

    return results


def main():
    institutes = pd.read_csv('../institutes.csv')
    year_range = range(2020, 2023)
    publications = []
    for index, row in institutes.iterrows():
        for year in year_range:
            works_filter = f'authorships.institutions.ror:{row["ROR"]},publication_year:{year}'
            pubs = get_works(works_filter)
            for pub in pubs:
                pub['ror'] = row['ROR']
                pub['year'] = year
            publications.extend(pubs)
    # store as json
    with open('../data/works.json', 'w') as f:
        f.write(json.dumps(publications))
