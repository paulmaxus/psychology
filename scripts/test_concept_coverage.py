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
# How many publications have at least one level x concept?

# %%
import sys
sys.path.append('..')  # this way, we can import from utils

# %%
import pandas as pd
import json
from utils.openalex_works import get_works

# %%
with open('../config.json', 'r') as f:
    config = json.loads(f.read())

# %%
institutes = pd.read_csv(f'{config["project_path"]}/affiliations.csv')
ror = institutes[institutes.university=='VU']['ror'].iloc[0]

# %%
works_filter = f'authorships.institutions.ror:{ror},publication_year:2021'
works = get_works(works_filter, '*', config['email'])

# %%
for l in range(6):
    has_level = list(map(lambda x: any(list(map(lambda y: y['level']==l, x['concepts']))), works))
    print(round(sum(has_level)/len(has_level)*100,1), '% of publications have level', l, 'concept')

# %%
