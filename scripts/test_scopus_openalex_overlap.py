# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     notebook_metadata_filter: kernel
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.14.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# We compare the coverage of Scopus and Openalex
# - for each of the participating institutes
# - for years within the range 2017-2021
# - for all outputs and restricted to journal publications

# %%
import pandas as pd
import json
import requests

# %%
with open('../config.json', 'r') as f:
    config = json.loads(f.read())

# %%
# load affiliations file with rors and scopus afids
affiliations = pd.read_csv(config['project_path'] + '/affiliations.csv')
year_range = range(2017,2022)

# %%
affiliations

# %%
# get scopus data
scopus = []
scopus_search_url = 'https://api.elsevier.com/content/search/scopus'
pub_types_labels = ['all', 'journal']
pub_types_string = ['', ' AND SRCTYPE(j)']
for index, row in affiliations.iterrows():
    for year in year_range:
        for pt_idx in range(len(pub_types_string)):
            params = {'query': f'AF-ID({row["afid"]}) AND PUBYEAR = {year}{pub_types_string[pt_idx]}',
                      'insttoken': config['elsevier_instkey'], 
                      'apiKey': config['elsevier_apikey']}
            result = requests.get(scopus_search_url, params=params)
            scopus.append({'university': row['university'],
                           'year': year,
                           'type': pub_types_labels[pt_idx],
                           'count': result.json()['search-results']['opensearch:totalResults']})

# %%
openalex = []
openalex_url = 'https://api.openalex.org/works'
pub_types_labels = ['all', 'journal']
pub_types_string = ['', ',type:journal-article']
for index, row in affiliations.iterrows():
    for pt_idx in range(len(pub_types_string)):
        params = {'filter': f'institutions.ror:{row["ror"]}{pub_types_string[pt_idx]}',
                  'group_by': 'publication_year',
                  'mailto': config['email']}
        result = requests.get(openalex_url, params=params)
        data = result.json()['group_by']
        for group in data:
            if int(group['key']) in year_range:
                openalex.append({'university': row['university'],
                                 'year': group['key'],
                                 'type': pub_types_labels[pt_idx],
                                 'count': group['count']})

# %%
df_scopus = pd.DataFrame(scopus, dtype=str)
df_scopus['count'] = pd.to_numeric(df_scopus['count'])

df_openalex = pd.DataFrame(openalex, dtype=str)
df_openalex['count'] = pd.to_numeric(df_openalex['count'])

df_merged = df_scopus.merge(df_openalex, how='left', on=['university', 'year', 'type'], suffixes=['_scopus', '_openalex'])
df_merged['scopus_coverage'] = df_merged['count_openalex'] / df_merged['count_scopus']

# %%
df_merged.to_csv('../data/sc_oa_comp.csv', index=False)

# %%
pubtype = 'journal'
df_pivot = df_merged[df_merged.type==pubtype].pivot(index='year', columns=['university'], values=['scopus_coverage'])
df_pivot.plot(legend=False)

# %%
pubtype = 'journal'
df_pivot = df_merged[df_merged.type==pubtype].pivot(index='year', columns=['university'], values=['count_scopus'])
df_pivot.plot(legend=False)

# %%
