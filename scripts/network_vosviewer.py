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
# ## VOSviwer network visualisation

# %% [markdown]
# transform the works and relations table to map and network file
# * each university will have separate weights (weights\<uni>)

# %%
import pandas as pd

# %%
works_count = pd.read_csv('../data/works_count.csv')
relations = pd.read_csv('../data/concepts_relations.csv')

# %%
works_count.head(2)

# %%
relations.head(2)

# %%
vv_map = works_count.pivot(index=['concept.id', 'label'], columns='university', values='count')

# %%
vv_map = vv_map.rename(lambda x: f'weight<{x}>', axis=1).reset_index()

# %%
vv_map = vv_map.rename({'concept.id': 'id'}, axis=1)

# %%
# set missing works/weights to 0
vv_map = vv_map.fillna(0)

# %%
vv_map.to_csv('../data/vv_map.csv', index=False)

# %%
relations = relations[['id', 'rel_id', 'rel_score']]

# %%
relations.to_csv('../data/vv_network.csv', index=False, header=False)
