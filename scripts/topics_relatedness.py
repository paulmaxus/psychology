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
import requests
import json
import pandas as pd
import config

# %%
pubs = pd.read_csv(f'{config.project_path}/tables/topics_publications.csv')

# %%
topics = pubs.drop_duplicates('Topic number')[['Topic number', 'Topic name',
                                               'Topic Cluster number', 'Topic Cluster name']]

# %%
topics = topics[~pd.isna(topics['Topic number'])]

# %%
topics.loc[:, 'Topic number'] = topics['Topic number'].astype(int)

# %%
relations = {}

# %%
base_url = 'https://api.elsevier.com/analytics/scival/topic/metrics'
for topic_id in topics['Topic number']:
    params = {'topicIds': topic_id,
              'metricTypes': 'relatedTopics',
              'insttoken': config.elsevier_instkey,
              'apiKey': config.elsevier_apikey}
    headers = {'Accept': 'application/json'}
    result = requests.get(base_url, params=params, headers=headers)
    if result.status_code == 200:
        relations[int(topic_id)] = result.json()

# %%
# temp storage
with open('data/relations.json', 'w') as f:
    f.write(json.dumps(relations))

# %%
relation_scores = {}
for topic_id in relations:
    relation = relations[topic_id]
    for related_topic in relation['results'][0]['metrics'][0]['values']:
        related_topic_id = related_topic['topic']['id']
        score = related_topic['relationScore']
        if topic_id not in relation_scores:
            relation_scores[topic_id] = {}
        relation_scores[topic_id][related_topic_id] = score

# %%
# are the topics in our set also related?
relatedness = []
for topic_id in topics['Topic number']:
    for related_topic_id in topics['Topic number']:
        if related_topic_id in relation_scores[topic_id]:
            relatedness.append({'topic_id': topic_id,
                                'related_topic_id': related_topic_id,
                                'topic_name': topics[topics['Topic number']==topic_id]['Topic name'].iloc[0],
                                'related_topic_name': topics[topics['Topic number']==related_topic_id]['Topic name'].iloc[0],
                                'score': relation_scores[topic_id][related_topic_id]})

# %%
df = pd.DataFrame(relatedness)

# %%
df.to_csv(f'{config.project_path}/relations.csv', index=False)
