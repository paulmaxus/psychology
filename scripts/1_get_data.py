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
# - read Pure data (DOIs)
# - find in OpenAlex
# - find in Scival (manually)
# - store temporarily

# %%
import pandas as pd
import requests
import json

# %%
with open('../config.json', 'r') as f:
    config = json.loads(f.read())

# %%
pure = pd.read_csv('../data/pure_outputs/research_output.csv')
# some have NULL as NA, but those are recognised by default (na_values)

# %%
pure = pure.melt(var_name='institute', value_name='doi')

# %%
# doi preprocessing
pure = pure.dropna()
pure['doi'] = pure['doi'].dropna().apply(lambda x: x.replace('https://doi.org/', '').lower().strip())
# instances have been spotted where the doi is prefixed with the string "doi:"
# this works as a link, but openalex recognises it as the doi filter parameter
pure['doi'] = pure['doi'].apply(lambda x: x.replace('doi:', ''))
pure = pure.drop_duplicates()

# %%
for i in pure.institute.unique():
    print(i + ':\t' + str(len(pure[pure.institute==i])))

# %%
# use one pile for data retrieval and keep the linking table
dois = pure.doi.unique()

# %%
print(len(dois))

# %%
pure.to_csv(config['project_path'] + '/tables/institute_has_doi.csv', index=False)

# %% [markdown]
# ## Scival data (manual)
# * do this in batches of 5000, those can be computed right away

# %%
for i in range(0, len(dois), 5000):
    pd.DataFrame(dois[i:i+5000]).\
        to_csv(f'../data/pure_outputs/dois/batch{i}.csv', index=False, header=False)

# %% [markdown]
# ## OpenAlex

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
# maximum amount of options per filter is 50
# URL length limit would otherwise be enforced anyways
dois_batches = [[]]
dois_batches_aux = []
cur_idx = 0
for doi in dois:
    # : causes errors in API, add those to individual requests
    if ':' in doi:
        dois_batches_aux.append([doi])
    else:
        if len (dois_batches[cur_idx]) < 50:
            dois_batches[cur_idx].append(doi)
        else:
            dois_batches.append([doi])
            cur_idx += 1
dois_batches.extend(dois_batches_aux)

# %%
results = []

n = 50
for dois_sub in dois_batches:
    dois_filter = f"doi:{'|'.join(dois_sub)}"
    params = {'filter': dois_filter}
    results = results + get_works(params)

print(len(results), 'of', len(dois), 'found')

# %%
with open('../data/raw/works.json', 'w') as f:
    f.write(json.dumps(results))

# %% [markdown]
# Additional requests

# %%
# sub-json on request
institute = 'UvA'
results_sub = []
for r in results:
    if r['doi'].replace('https://doi.org/', '').lower().strip() in pure[pure.institute==institute]['doi'].values:
        results_sub.append(r)

# %%
print(len(results_sub))

# %%
with open(f'../data/raw/works_{institute.lower()}.json', 'w') as f:
    f.write(json.dumps(results_sub))
