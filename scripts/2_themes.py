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
# Assigning themes to Pure publications:
# - themes are based partly on concepts (see themes_concepts.csv) and concept patterns
# - some constraints are specified, e.g. concept level

# %%
import pandas as pd
import json

# %%
with open('../config.json', 'r') as f:
    config = json.loads(f.read())

# %%
# themes
themes = pd.read_csv('../themes.csv', header=None)
themes

# %%
h = pd.read_csv(f'{config["project_path"]}/openalex_concepts_hierarchy.csv')
h['display_name'] = h.display_name.str.lower()

# %%
# load theme-concept mapping
themes_concepts = pd.read_csv('../themes_concepts.csv').to_dict('list')
for theme in themes_concepts:
    themes_concepts[theme] = [i for i in themes_concepts[theme] if not pd.isna(i)]
# check that the included concepts are existing concepts
for theme in themes_concepts:
    for c in themes_concepts[theme]:
            if c not in h['display_name'].values:
                print(c, 'is not a concept')


# %%
def is_theme1(concepts: list[tuple[str, int]]) -> bool:
    return any([c[0] in themes_concepts['theme1'] for c in concepts])


# %%
def is_theme2(concepts: list[tuple[str, int]]) -> bool:
    return any([c[0] in themes_concepts['theme2'] for c in concepts])


# %%
def is_theme3(concepts: list[tuple[str, int]]) -> bool:
    return any([c[0] in themes_concepts['theme3'] for c in concepts]) or any(['robot' in c[0] for c in concepts if c[1]==3])


# %%
def is_theme4(concepts: list[tuple[str, int]]) -> bool:
    return any([c[0] in themes_concepts['theme4'] for c in concepts]) or any(['behav' in c[0] for c in concepts])


# %%
def is_theme5(concepts: list[tuple[str, int]]) -> bool:
    return any([c[0] in themes_concepts['theme5'] for c in concepts]) or any(['intercultural' in c[0] for c in concepts if c[1]==3])


# %%
#with open('../data/pure_concepts.json', 'r') as f:
#    pubs = json.loads(f.read())
with open('../data/raw/works.json', 'r') as f:
    pubs = json.loads(f.read())

# %%
'''
pubs_themes = []
for pub in pubs:
    concepts = [(c['display_name'].lower(), c['level']) for c in pub['concepts']]
    record = {'title': pub['title'], 'year': pub['publication_year'], 'concepts': concepts}
    record['theme1'] = is_theme1(concepts)
    record['theme2'] = is_theme2(concepts)
    record['theme3'] = is_theme3(concepts)
    record['theme4'] = is_theme4(concepts)
    record['theme5'] = is_theme5(concepts)
    pubs_themes.append(record)
'''
pubs_themes = []
for pub in pubs:
    concepts = [(c['display_name'].lower(), c['level']) for c in pub['concepts']]
    record = {'doi': pub['doi']}
    is_theme = [is_theme1(concepts), is_theme2(concepts), is_theme3(concepts), is_theme4(concepts), is_theme5(concepts)]
    record['themes'] = '; '.join(themes[is_theme][0].values)
    pubs_themes.append(record)

# %%
#pd.DataFrame(pubs_themes).drop(columns='concepts').to_csv(f'{config["project_path"]}/tables/pure_themes.csv', index=False)
pd.DataFrame(pubs_themes).to_csv(f'../data/raw/works_themes.csv', index=False)

# %% [markdown]
# Extra processing

# %%
# long format
df_long = pd.DataFrame(pubs_themes).drop(columns='concepts').melt(id_vars=['title', 'year'], var_name='theme',
                                                                  value_vars=['theme1', 'theme2', 'theme3', 'theme4', 'theme5'])
df_long = df_long[df_long.value==True]
df_long.drop(columns='value').to_csv(f'{config["project_path"]}/tables/pure_themes_long.csv', index=False)

# %%
# what are the concepts of publications without theme?
df = pd.DataFrame(pubs_themes)
df = df[~df.loc[:,'theme1':'theme5'].any(axis=1)]
df = df[['title', 'year', 'concepts']]
df.to_csv('../data/pure_themes_rest.csv', index=False)

# %%
len(df)

# %%
# this set should overlap with a previous set (pubs without psychology concepts)
rest = pd.read_csv('../data/pure_concepts_rest.csv')
print('rest has', len(rest))
print('overlap has', len(rest.merge(df, on='title', how='inner')))

# %%
