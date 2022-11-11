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
import requests
import json

# %%
with open('../config.json', 'r') as f:
    config = json.loads(f.read())

# %%
pure = pd.read_excel('../data/pure_psychology_2017-2022.xls')

# %%
dois = pure['10.1 Electronic version(s) of this work > DOI (Digital Object Identifier)[1]']

# %%
dois = dois.dropna().apply(lambda x: x.replace('https://doi.org/', '').lower().strip())

# %%
print(len(dois), len(dois.unique()))

# %%
dois = dois.unique()

# %% [markdown]
# search for those in openalex and extract concepts (copy from another project)

# %%
base_url_works = 'https://api.openalex.org/works'

def get_works(params_ext):
    params = {
        'per-page': 100,
        'mailto': config['email']
    }
    params.update(params_ext)
    r = requests.get(base_url_works, params)
    results = []
    if r.status_code == 200:
        data = r.json()
        if 'results' in data:
            results = data['results']
    else:
        print('error:', r.status_code, 'url:', r.url)
    return results


# %%
results = []
# maximum amount of options per filter is 50
n = 50
for dois_sub in [dois[i:i+n] for i in range(0, len(dois), n)]:
    dois_filter = f"doi:{'|'.join(dois_sub)}"
    params = {'filter': dois_filter}
    results = results + get_works(params)

print(len(results), 'of', len(dois), 'found')


# %%
def agg_concepts(concepts):
    agg = {}
    for c in concepts:
        label = 'level' + str(c['level'])
        if label in agg:
            agg[label].append(c['display_name'])
        else:
            agg[label] = [c['display_name']]
    return agg


# %%
data = []
works = []
for pub in results:
    data.append({'title': pub['title'],
                 'year': pub['publication_year'],
                 'concepts': agg_concepts(pub['concepts'])})
    works.append({'title': pub['title'],
                  'year': pub['publication_year'],
                  'concepts': pub['concepts']})

# %%
df = pd.DataFrame(data)
df = pd.concat([df.drop('concepts', axis=1), pd.json_normalize(df.concepts).sort_index(axis=1)], axis=1)

# %%
df.to_csv('../data/pure_concepts.csv', index=False)

# %%
import json
with open('../data/pure_concepts.json', 'w') as f:
    f.write(json.dumps(works))

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
mask = df.apply(axis=1, 
         func=lambda x: has_psychology(x['level0']) or has_psychology(x['level1']))

# %%
len(df[~mask])/len(df)

# %%
len(df)

# %%
df[~mask].to_csv('../data/pure_concepts_rest.csv', index=False)

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
