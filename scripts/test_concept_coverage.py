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
# %cd ..  
# this way, we can import from utils

# %%
import pandas as pd
import json
from utils.openalex_works import get_works

# %%
with open('config.json', 'r') as f:
    config = json.loads(f.read())

# %%
institutes = pd.read_csv('affiliations.csv')
ror = institutes[institutes.university=='VU']['ror'].iloc[0]

# %%
works_filter = f'authorships.institutions.ror:{ror},publication_year:2021'
works = get_works(works_filter, '*', config['email'])

# %%
has_level1 = list(map(lambda x: any(list(map(lambda y: y['level']==1, x['concepts']))), works))

# %%
has_level1[:10]

# %%
sum(has_level1)/len(has_level1)

# %%
