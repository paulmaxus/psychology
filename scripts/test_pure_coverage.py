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
# - compare pure (doi) coverage in scival and openalex
# - investigate research output types (books etc.)
# - how much output is psychology-related?

# %%
import pandas as pd
import json

# %%
with open('../config.json', 'r') as f:
    config = json.loads(f.read())

# %%
institute_doi = pd.read_csv(config['project_path'] + '/tables/institute_has_doi.csv')

# %%
# openalex data
with open('../data/raw/works.json', 'r') as f:
    oa_data = json.loads(f.read())
oa_data = pd.DataFrame(oa_data)[['id', 'doi', 'title', 'type', 'concepts']]
oa_data['doi'] = oa_data['doi'].apply(lambda x: x.replace('https://doi.org/', '').lower().strip())

# %%
oa_data[oa_data.duplicated('doi', keep=False)]

# %%
oa_data = oa_data.drop_duplicates('doi', keep='first')

# %%
# scival data
sv_data = pd.read_csv('../data/pure_outputs/scival.csv', na_values='-')[['EID', 'DOI']]

# %%
sv_data = sv_data.rename({'DOI': 'doi'}, axis=1)

# %%
sv_data['doi'] = sv_data['doi'].apply(lambda x: x.lower().strip())

# %%
sv_data[sv_data.duplicated('doi', keep=False)]

# %%
# join
data = institute_doi.merge(oa_data, on='doi', how='left')
data = data.merge(sv_data, on='doi', how='left')

# %%
for i in data.institute.unique():
    print('---')
    print(i)
    n_pr = len(data[data.institute==i]['doi'].dropna().unique())
    n_oa = len(data[data.institute==i]['id'].dropna().unique())
    n_sv = len(data[data.institute==i]['EID'].dropna().unique())
    print('unique dois in', 'pure:',  n_pr, '/ openalex:', n_oa, '/ scival:', n_sv)
    print('coverage in openalex:', round(n_oa/n_pr, 3))
    print('coverage in scival:', round(n_sv/n_pr, 3))

# %%
# what are the publication types?
data.type.value_counts()

# %%
# what is posted-content?
data[data.type=='posted-content'].head()
# archive data, preprints

# %% [markdown]
# Testing concepts

# %%
def agg_concepts(concepts):
    agg = {}
    if type(concepts)==list:
        for c in concepts:
            label = 'level' + str(c['level'])
            if label in agg:
                agg[label].append(c['display_name'])
            else:
                agg[label] = [c['display_name']]
    return agg


# %%
data_c = data.copy()[~pd.isna(data.concepts)]

# %%
data_c = pd.concat([data.drop('concepts', axis=1), 
                    pd.json_normalize(data.concepts.apply(agg_concepts)).sort_index(axis=1)], axis=1)

# %% [markdown]
# how many have keyword 'psychology' in either level0 or level1 concept?

# %%
concepts_hierarchy = pd.read_csv(f'{config["project_path"]}/openalex_concepts_hierarchy.csv')
# concept ids are lowercase, parent ids not
concepts_hierarchy['parent_ids'] = concepts_hierarchy['parent_ids'].str.lower()

# %%
psychology_id = 'https://openalex.org/c15744967'
concepts_psychology = concepts_hierarchy[concepts_hierarchy.parent_ids.str.find(psychology_id) > -1]
concepts_psychology = list(concepts_psychology['display_name'].values)
concepts_psychology.append('Psychology')


# %%
def has_psychology(concepts):
    if type(concepts)==float:
        return False
    else:
        return any([c in concepts_psychology for c in concepts])


# %%
mask = data_c.apply(axis=1, func=lambda x: has_psychology(x['level0']) or has_psychology(x['level1']))

# %%
len(data_c[mask])/len(data_c)

# %% [markdown]
# is this coverage comparable when we tag ourselves?

# %%
tagged_data = pd.read_csv('../data/concept_tagger_output.csv')
# for comparison, let's focus on the one we also find in openalex
#tagged_data = tagged_data[tagged_data['1 Title of the contribution in original language'].isin(df.title)]

# %%
len(tagged_data)

# %%
concepts_psychology_normalized = concepts_hierarchy[concepts_hierarchy.parent_ids.str.find(psychology_id) > -1]
concepts_psychology_normalized = list(concepts_psychology_normalized['normalized_name'].values)
concepts_psychology_normalized.append('psychology')


# %%
def has_psychology_normalized(concepts):
    return any([c in concepts_psychology_normalized for c in concepts])


# %%
import ast  # for list literals

# %%
mask = tagged_data.apply(axis=1, 
         func=lambda x: has_psychology_normalized(ast.literal_eval(x['tags'])))

# %%
len(tagged_data[~mask])/len(tagged_data)

# %%
tagged_data[~mask].tags

# %%
