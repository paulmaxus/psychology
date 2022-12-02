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
import pandas as pd
import json
import glob
import gzip

# %%
with open('../config.json', 'r') as f:
    config = json.loads(f.read())

# %% [markdown]
# # Create concept relations table for network visualisation
# - first, find "core" level 2 concepts for the entire dataset (based on publication counts)
# - keep publication counts per university for color coding

# %% [markdown]
# ## first, prepare the data

# %%
# load publications data
with open('../data/publications.json', 'r') as f:
    publications = pd.DataFrame(json.loads(f.read()))

# %%
# load concept hierarchy
# note: concept ids are lowercase, parent ids not
concepts_hierarchy = pd.read_csv(f'{config["project_path"]}/openalex_concepts_hierarchy.csv')
concepts_hierarchy['parent_ids'] = concepts_hierarchy['parent_ids'].str.lower()

# %%
# filter on psychology concepts
psy_id = concepts_hierarchy[concepts_hierarchy.display_name=='Psychology']['openalex_id'].iloc[0]
psy_children = concepts_hierarchy[concepts_hierarchy.parent_ids.str.find(psy_id) > -1]
psy_grandchildren = concepts_hierarchy[concepts_hierarchy.parent_ids.
    apply(lambda x: any([y in psy_children['openalex_id'].values for y in x.split(', ')]) if not pd.isna(x) else False)]

# %% [markdown]
# ## create concepts subset

# %%
publications = publications.explode('concepts')
publications = pd.concat([publications.reset_index(drop=True),
                          pd.json_normalize(publications.concepts).reset_index(drop=True).rename(lambda x: 'concept.'+x, axis='columns')],
                        axis=1)
publications = publications.drop(columns='concepts')

# %%
# only level 2 concepts with grandparent psychology
# add parents for vosviwer map file
publications_2 = publications.copy()[publications['concept.level'].isin([1,2])]
publications_2['concept.id'] = publications_2['concept.id'].str.lower()
publications_2 = publications_2[
    publications_2['concept.id'].isin(psy_grandchildren.openalex_id) |
    publications_2['concept.id'].isin(psy_children.openalex_id)
]

# %%
# count how often each concept appears in the publication set
# then filter using a cutoff (~50 nodes?)
counts = publications_2.value_counts('concept.id')
n_nodes = len(counts) #50
print(len(counts), 'concepts in total')
print(n_nodes, 'are', round((n_nodes/len(counts))*100), '% of total')

# %%
concepts_subset = list(counts.copy()[counts >= counts.quantile(1-(n_nodes/len(counts)))].index)
print('number of nodes (concepts):', len(concepts_subset))

# %%
publications_2_subset = publications_2.copy()[publications_2['concept.id'].isin(concepts_subset)]

# %% [markdown]
# aggregate, but keep the counts per university for color coding

# %%
# counts per university
# display_names should also be unique but use "first" just to be sure
works_count = publications_2_subset.groupby(['university', 'concept.id']).agg(label=('concept.display_name', 'first'), count=('id', 'count'))

# %%
works_count.to_csv('../data/works_count.csv')

# %% [markdown]
# ## create concept relations table

# %%
concepts_2 = publications_2_subset.copy()[['concept.id', 'concept.display_name', 'concept.level', 'concept.score']]
concepts_2 = concepts_2.rename(lambda x: x.replace('concept.', ''), axis='columns')

# %%
# NOTE: works are now counted more than once if they are shared amongst universities
concepts_2['works_count'] = concepts_2.groupby(['id'])['id'].transform('size')

# %%
concepts_2 = concepts_2.drop_duplicates('id', keep='first')

# %%
print(len(concepts_2))

# %%
# get concept relations from data snapshot
concepts_meta = []
for filename in glob.glob(f'{config["project_path"]}/openalex-snapshot-concepts/**/*.gz', recursive=True):
    with gzip.open(filename, 'rb') as f:
        for line in f:
            concepts_meta.append(json.loads(line))

# %%
len(concepts_meta)  # that's the exact amount that is stated on https://api.openalex.org/concepts

# %%
concepts_meta_df = pd.DataFrame(concepts_meta)[['id', 'related_concepts']]
concepts_meta_df['id'] = concepts_meta_df['id'].str.lower()

# %%
concepts_2 = concepts_2.merge(concepts_meta_df, how='left', on='id')

# %%
concepts_2_relations = concepts_2.copy().explode('related_concepts').reset_index(drop=True)

# %%
concepts_2_relations = pd.concat([concepts_2_relations,
                                  pd.json_normalize(concepts_2_relations['related_concepts']).add_prefix('rel_')],
                                 axis=1)

# %%
concepts_2_relations['rel_id'] = concepts_2_relations['rel_id'].str.lower()

# %%
# filter out the related concepts that are not part of our set
concepts_2_relations = concepts_2_relations[concepts_2_relations['rel_id'].isin(concepts_2['id'])]

# %%
# level 1 concepts (parents) will be added to the graph
parents_relations = psy_grandchildren[psy_grandchildren.openalex_id.isin(concepts_subset)].\
    apply(lambda x: x.str.split(', ') if x.name in ['parent_display_names', 'parent_ids'] else x).\
    explode(['parent_display_names', 'parent_ids'])
parents_relations = parents_relations[parents_relations.parent_ids.isin(psy_children.openalex_id)]

# %%
aux = pd.DataFrame({'id': parents_relations.openalex_id,
                    'display_name': parents_relations.display_name,
                    'rel_id': parents_relations.parent_ids,
                    'rel_display_name': parents_relations.parent_display_names,
                    'rel_level': 1,
                    'rel_score': concepts_2_relations.rel_score.mean()})

# %%
concepts_2_relations = pd.concat([concepts_2_relations, aux[aux.id.isin(concepts_2_relations.id)]])

# %%
concepts_2_relations.to_csv('../data/concepts_relations.csv', index=False)

# %%
