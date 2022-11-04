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

# %%
h = pd.read_csv('../openalex_concepts_hierarchy.csv')

# %% [markdown]
# Themes
# 1. Veerkracht bij jeugd
# 2. Psychische aandoeningen
# 3. De menselijke factor in nieuwe technologieën
# 4. Maatschappelijke transitie en gedragsverandering
# 5. Maatschappelijke ongelijkheid en diversiteit

# %%
# included concepts per theme
i1 = ['developmental psychology', 'young adult', 'positive youth development', 'child and adolescent psychiatry',
      'child behavior checklist', 'early childhood', 'child development', 'child health', 'child protection', 
      'early childhood education', 'child rearing', 'academic achievement', 'pediatrics']

i2 = ['clinical psychology', 'psychiatry']

i3 = ['nanotechnology', 'genetic enhancement', 'social media', 'mobile technology', 'wearable technology', 'virtual reality', 'cryptocurrency']

i5 = ['cultural diversity', 'religious diversity', 'inequality', 'social equality', 'underrepresented minority', 'social exclusion', 'refugee', 'transgender', 'homosexuality', 
      'racial diversity', 'gender diversity', 'ethnically diverse', 'economic inequality', 'educational inequality', 'gender inequality', 'social inequality', 'wage inequality', 
      'sexual minority', 'minority rights', 'minority group', 'ethnic group']

# %%
for concepts in [i1, i2, i3, i5]:
    # check that the included concepts are existing concepts
    for c in concepts:
        if c not in h['normalized_name'].values:
            print(c, 'is not a concept')


# %%
def is_one(concepts: list[tuple[str, int]]) -> bool:
    # concepts: (name, level)
    # concepts are all concepts assigned to a given work
    include_pattern = ['child', 'adoles', 'young', 'youth']
    return any([c[0] in i1 for c in concepts]) or any([p in c for p in include_pattern for c in concepts if c[1]>1])


# %%
def is_two(concepts: list[tuple[str, int]]) -> bool:
    # concepts: (name, level)
    # concepts are all concepts assigned to a given work
    return any([c[0] in i2 for c in concepts])


# %%
def is_three(concepts: list[tuple[str, int]]) -> bool:
    # concepts: (name, level)
    # concepts are all concepts assigned to a given work
    return any([c[0] in i3 for c in concepts]) or any(['robot' in c for c in concepts if c[1]==3])


# %%
def is_four(concepts: list[tuple[str, int]]) -> bool:
    # concepts: (name, level)
    # concepts are all concepts assigned to a given work
    return any(['behav' in c[0] for c in concepts])


# %%
def is_five(concepts: list[tuple[str, int]]) -> bool:
    # concepts: (name, level)
    # concepts are all concepts assigned to a given work
    return any([c[0] in i5 for c in concepts]) or any(['intercultural' in c for c in concepts if c[1]==3])


# %%
import json
with open('../data/pure_concepts.json', 'r') as f:
    pubs = json.loads(f.read())

# %%
pubs_themes = []
for pub in pubs:
    concepts = [(c['display_name'].lower(), c['level']) for c in pub['concepts']]
    record = {'title': pub['title']}
    record['theme1'] = is_one(concepts)
    record['theme2'] = is_two(concepts)
    record['theme3'] = is_three(concepts)
    record['theme4'] = is_four(concepts)
    record['theme5'] = is_five(concepts)
    pubs_themes.append(record)

# %%
pd.DataFrame(pubs_themes).to_csv('../data/pure_themes.csv', index=False)

# %%
