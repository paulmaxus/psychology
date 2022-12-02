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

# %%
import requests
import pandas as pd

# %%
# get all psychology children
url = 'https://api.openalex.org/concepts?filter=ancestors.id:https://openalex.org/C15744967,level:1'
results = requests.get(url)

# %%
p_ids = []
for r in results.json()['results']:
    p_ids.append(r['id'])

# %%
# benchmarked countries
country_codes = ['BE', 'DK', 'DE', 'SE', 'GB', 'CH', 'US', 'NL']

# %%
# per country and concept, get the number of publications, citations, and average
data = []
c_str = 'concepts.id:' + '|'.join(p_ids)
for cc in country_codes:
    url = f'https://api.openalex.org/works?filter=institutions.country_code:{cc},{c_str}&group_by=concepts.id'
    results = requests.get(url)
    for c in results.json()['group_by']:
        if c['key'] in p_ids:
            data.append({'cc': cc, 'concept': c['key_display_name'], 'count': c['count']})

# %%
pd.DataFrame(data).to_csv('../data/benchmarking.csv', index=False)

# %% [markdown]
# How can we get the average citations?
#
# Possibly using it as group_by
#
# http://api.openalex.org/works?group_by=cited_by_count

# %%
