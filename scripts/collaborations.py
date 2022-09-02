
def is_national(country_list, nation):
    # definition: at least 1 collaborator is national
    return country_list.count(nation) > 1


def collaborations(df, domain_col, af_col, id_col, country_col, nation):
    c_int = []  # (internal) collaborations amongst participating institutes, X-X is empty
    c_ext = []  # (external) collaborations on national or international level
    df['is_national'] = df[country_col].apply(lambda x: is_national(x, nation))
    for af1 in df[af_col].unique():
        sub = df.copy()[df[af_col] != af1]
        # per domain
        for domain in sub[domain_col].unique():
            ids1 = df[(df[domain_col] == domain) & (df[af_col] == af1)][id_col]
            # internal collaborations
            for af2 in sub[af_col].unique():
                ids2 = df[(df[domain_col] == domain) & (df[af_col] == af2)][id_col]
                overlap = len(ids1[ids1.isin(ids2)])
                c_int.append(dict(domain=domain, university_x=af1, university_y=af2, count=overlap))
            # external collaborations
            ids2 = sub[sub[domain_col] == domain][id_col]
            rest_n = ids1[~ids1.isin(ids2) & ids1.isin(df[df['is_national']][id_col])]
            rest_i = ids1[~ids1.isin(ids2) & ids1.isin(df[~df['is_national']][id_col])]
            c_ext.append(dict(domain=domain, type='national', university=af1, count=len(rest_n)))
            c_ext.append(dict(domain=domain, type='international', university=af1, count=len(rest_i)))
        # all domains (make sure ids are unique)
        # internal collaborations
        ids1 = df[df[af_col] == af1][id_col].drop_duplicates()
        for af2 in sub[af_col].unique():
            ids2 = df[df[af_col] == af2][id_col].drop_duplicates()
            overlap = len(ids1[ids1.isin(ids2)])
            c_int.append(dict(domain='ALL', university_x=af1, university_y=af2, count=overlap))
        # external collaborations
        ids2 = sub[id_col].drop_duplicates()
        rest_n = ids1[~ids1.isin(ids2) & ids1.isin(df[df['is_national']][id_col])]
        rest_i = ids1[~ids1.isin(ids2) & ids1.isin(df[~df['is_national']][id_col])]
        c_ext.append(dict(domain='ALL', type='national', university=af1, count=len(rest_n)))
        c_ext.append(dict(domain='ALL', type='international', university=af1, count=len(rest_i)))
    return c_int, c_ext
