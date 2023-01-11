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
# Dashboard-independent overview table of concepts, topics and themes

# %%
import pandas as pd
import json

# %%
pure = pd.read_csv('../data/pure_outputs/pure.csv')

# %%
with open('../data/raw/works.json', 'r') as f:
    openalex = json.loads(f.read())

# %%
concepts = []
for pub in openalex:
    doi = pub['doi'].replace('https://doi.org/', '').lower()
    concepts.append({'doi': doi, 'concepts': '; '.join([c['display_name'] for c in pub['concepts']])})

# %%
pure = pure.merge(pd.DataFrame(concepts), how='left', on='doi')

# %%
scival = pd.read_csv('../data/raw/scival.csv')[['DOI|', 'Topic Cluster name', 'Topic name']]
scival.columns = ['doi', 'topic_cluster', 'topic']
scival['doi'] = scival['doi'].apply(str.lower)

# %%
pure = pure.merge(scival, how='left', on='doi')

# %%
themes = pd.read_csv('../data/raw/works_themes.csv')
themes['doi'] = themes['doi'].apply(lambda x: x.replace('https://doi.org/', '').lower())

# %%
pure = pure.merge(themes, how='left', on='doi')

# %%
# make dois clickable
pure['doi'] = pure['doi'].apply(lambda x: 'https://doi.org/'+x)

# %%
pure.to_csv('../data/overview.csv', index=False)

# %%
