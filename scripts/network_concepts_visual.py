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
import networkx as nx
import matplotlib.pyplot as plt

# %%
with open('../config.json', 'r') as f:
    config = json.loads(f.read())

# %% [markdown]
# - use a seed to keep the same layout for each university
# - change the color coding for each university (heatmap) without changing the layout
# - save the images to a dedicated folder which is pushed to bitbucket
# - create a table pointing to the images by url

# %%
concepts_relations = pd.read_csv('../data/concepts_relations.csv')
works_count = pd.read_csv('../data/works_count.csv', index_col='concept.id')

# %%
len(concepts_relations)

# %%
# needed for labels and color coding
concepts_hierarchy = pd.read_csv(f'{config["project_path"]}/openalex_concepts_hierarchy.csv')
concepts_hierarchy_1  = concepts_hierarchy.copy()[concepts_hierarchy.level==1]


# %%
# color coding: range from 0 to 1 with -1 for level 1 concepts, 0 for count == 0
def get_color_code(concept_id, works_count):
    try:
        code = works_count.loc[concept_id,'count'] / works_count['count'].max()
    except KeyError:
        if concept_id in concepts_hierarchy_1.openalex_id.values:
            code = -1
        else:
            code = 0
    return code

# size coding
def get_size(concept_id, works_count):
    try:
        size = works_count.loc[concept_id,'count'] / works_count['count'].max()
    except KeyError:
        if concept_id in concepts_hierarchy_1.openalex_id.values:
            size = 1
        else:
            size = 0
    return size*500


# %%
# needed for labels: topN 
# only the topN and level 1 concepts get labels
n = 25
topN = concepts_relations.drop_duplicates('id').sort_values('works_count', ascending=False)[:n]

# %%
G = nx.Graph()

labels = {}
label_count = 0
for index, row in concepts_relations.iterrows():
    G.add_edge(row['id'], row['rel_id'])
    for concept_id in [row['id'], row['rel_id']]:
        if concept_id not in labels:
            if (concept_id in topN.id.values) | (concept_id in concepts_hierarchy_1['openalex_id'].values):
                labels[concept_id] = \
                    concepts_hierarchy[concepts_hierarchy.openalex_id==concept_id]['display_name'].iloc[0]
            else:
                labels[concept_id] = ''#label_count
                label_count += 1

pos = nx.spring_layout(G, seed=2) # 97615

# draw separate plot for each university
# anonymise image, but keep track of uni - url association
counter = 1
network_images = []
for uni in works_count.university.unique():

    fig = plt.figure(figsize=(10, 6))
    ax = plt.axes()
    
    nx.draw_networkx_nodes(G, pos, ax=ax,
                           node_color=[get_color_code(n, works_count[works_count.university==uni]) for n in pos], 
                           cmap='seismic', alpha=0.5,
                           node_size=[get_size(n, works_count[works_count.university==uni]) for n in pos])
    nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.1)
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=8, labels=labels)

    #plt.legend()
    plt.tight_layout()
    plt.savefig(f"../images/network{counter}.svg", format="SVG")
    plt.close()
    network_images.append({'university': uni, 'url': f'{config["project_url"]}/images/network{counter}.svg'})
    counter += 1
pd.DataFrame(network_images).to_csv(f'{config["project_path"]}/tables/network_images.csv', index=False)

# %%
