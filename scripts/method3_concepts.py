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
output_path = f'{config["project_path"]}/tables/oalex_'

# %%
affiliations = pd.read_csv(f'{config["project_path"]}/affiliations.csv', dtype=object).applymap(lambda x: x.strip())
# strip: making sure no whitespaces are left

# %% [markdown]
# publications table

# %%
def extract_countries(work):
    # needed for collaborations
    work_countries = []
    for author in work.get('authorships', []):
        author_countries = set()
        # set: if an author has more than 1 affiliations in a country, we count it only once
        for institution in author.get('institutions', []):
            author_countries.add(institution.get('country_code'))
        work_countries.extend(author_countries)
    return work_countries


def extract_metadata(work):
    publication = {
        'id': work.get('id'),
        'doi': work.get('doi'),
        'title': work.get('title'),
        'concepts': work.get('concepts'),
        'cited_by_count': work.get('cited_by_count'),
        'countries': extract_countries(work)
    }
    return publication


# %%
subject_id = 'https://openalex.org/C15744967'  # psychology concept id
year_range = range(2016, 2022)  # end year is exclusive, 2016-2022
publications = []
for index, row in affiliations.iterrows():
    for year in year_range:
        works_filter = f'authorships.institutions.ror:{row["ror"]},publication_year:{year},concepts.id:{subject_id}'
        works = get_works(works_filter)
        for work in works:
            pub = extract_metadata(work)
            pub['university'] = row['university']
            pub['year'] = year
            publications.append(pub)

# %%
len(publications)

# %%
import json
with open('../data/publications.json', 'w') as f:
    f.write(json.dumps(publications))

# %%
publications_table = pd.json_normalize(publications)
publications_table = publications_table.drop_duplicates('id').drop(columns=['university', 'concepts'])

# %%
publications_table.to_csv(f'{output_path}publications.csv', index=False)

# %% [markdown]
# affiliations table

# %%
pubs_affs_table = pd.json_normalize(publications)[['id', 'university']]

# %%
pubs_affs_table.to_csv(f'{output_path}pubs_affs.csv', index=False)

# %% [markdown]
# concepts table
# - level 1 (with parent psychology)
# - level 2 (with grandparent psychology)
# - restcategory (psychology without child)

# %%
pubs_concepts_table = pd.json_normalize(publications)[['id', 'concepts']]
pubs_concepts_table = pubs_concepts_table.drop_duplicates('id')
pubs_concepts_table = pubs_concepts_table.explode('concepts').reset_index(drop=True)
pubs_concepts_table = pd.concat([pubs_concepts_table,
                                 pd.json_normalize(pubs_concepts_table['concepts']).add_prefix('concept_')],
                                axis=1).drop(columns='concepts')

# %%
concepts_hierarchy = pd.read_csv(f'{config["project_path"]}/openalex_concepts_hierarchy.csv')
# concept ids are lowercase, parent ids not
concepts_hierarchy['parent_ids'] = concepts_hierarchy['parent_ids'].str.lower()

# %%
psy_children = concepts_hierarchy[concepts_hierarchy.parent_ids.str.find(subject_id.lower()) > -1]
psy_grandchildren = concepts_hierarchy[concepts_hierarchy.parent_ids.
    apply(lambda x: any([y in psy_children['openalex_id'].values for y in x.split(', ')]) if not pd.isna(x) else False)]

# %%
pubs_concepts_table1 = pubs_concepts_table.copy()[pubs_concepts_table.concept_level==1]

pubs_concepts_table1_psy = pubs_concepts_table1.copy()\
    [pubs_concepts_table1.concept_id.str.lower().isin(psy_children['openalex_id'])]

# rest category (all publications that have level 1 concepts not related to psychology)
pubs_concepts_table1_rest = \
    pubs_concepts_table1.copy()[~pubs_concepts_table1.id.isin(pubs_concepts_table1_psy['id'])]
pubs_concepts_table1_rest['concept_display_name'] = 'REST'
# append rest
pubs_concepts_table1 = pd.concat([pubs_concepts_table1_psy, pubs_concepts_table1_rest])

# %%
pubs_concepts_table1.to_csv(f'{output_path}pubs_concepts1.csv', index=False)

# %%
pubs_concepts_table2 = pubs_concepts_table.copy()[pubs_concepts_table.concept_level==2]
pubs_concepts_table2 = pubs_concepts_table2[pubs_concepts_table2.concept_id.str.lower().isin(psy_grandchildren['openalex_id'])]
pubs_concepts_table2.to_csv(f'{output_path}pubs_concepts2.csv', index=False)

# %%
# hierarchy table
hierarchy = concepts_hierarchy.copy()[~pd.isna(concepts_hierarchy.parent_display_names)].\
    apply(lambda x: x.str.split(', ') if x.name in ['parent_display_names', 'parent_ids'] else x, axis=0).\
    explode(['parent_display_names'])
hierarchy = hierarchy[hierarchy.parent_display_names.isin(psy_children.display_name)]

# %%
hierarchy.to_csv(f'{output_path}concepts_hierarchy.csv', index=False)

# %% [markdown]
# collaborations

# %%
from utils.collaborations import collaborations

# %%
c_data = pubs_affs_table.merge(pubs_concepts_table1, how='left', on='id').\
    merge(publications_table, how='left', on='id')

# %%
# how many publications have no level 1 concept? also non-psychology children are included
len(c_data[pd.isna(c_data.concept_display_name)]['id'].unique())/len(c_data['id'].unique())

# %%
c_data = c_data[~pd.isna(c_data.concept_display_name)]

# %%
c_int, c_ext = collaborations(c_data, 'concept_display_name', 'university', 'id', 'countries', 'NL')

# %%
pd.DataFrame(c_int).to_csv(f'{output_path}collaborations.csv', index=False)
pd.DataFrame(c_ext).to_csv(f'{output_path}collaborations_rest.csv', index=False)

# %%
