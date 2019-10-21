#%%
import pandas as pd
import os
from tqdm import tqdm

# Path variables
data_path = '../../data/libraries.io/libraries-1.4.0-2018-12-22/'
output_path = '../../data/libraries.io/libraries-1.4.0-2018-12-22/go'

#%%
# Loading the Projects dataset
projects_path = 'projects-1.4.0-2018-12-22.csv'
projects_df = pd.read_csv(os.path.join(data_path, projects_path), index_col='ID')
print("Libraries.io dataset contains %d projects" % len(projects_df))

#%%
# Inspecting the programming languages
languages = projects_df['Language'].unique()
print("%d programming languages" % len(languages))

#%%
# Filtering Go projects
go_projects = projects_df[projects_df.Language == 'Go']
print("From %d projects (packages) - %d are of language Go " % (len(projects_df), len(go_projects)))
go_projects.to_pickle(os.path.join(output_path, 'projects-go-1.4.0-2018-12-22.pickle'))

#%%
# After filtering we dont need the entire dataset anymore
del projects_df

#%%
# Loading all repositories
# This file has >5GB so we will be reading it with Dask
repositories_path = 'repositories-1.4.0-2018-12-22.csv'
repositories_df = pd.read_csv(os.path.join(data_path, repositories_path), usecols=['ID', 'Host Type',\
    'Name with Owner', 'Fork', 'Last pushed Timestamp', 'Stars Count', 'Language', 
    'SourceRank'], index_col=False)




#%%
# Filtering by the language
go_repositories_df = repositories_df[repositories_df.Language == 'Go']



#%%
# Merging Go projects + versions
go_projects_repositories = pd.merge(go_projects, repositories_df, left_on='Repository ID', right_on='ID',\
    how='left', suffixes=('_p', '_r'))
# Saving into disk
go_projects_repositories.to_pickle(os.path.join(output_path, 'projects-go-repositories-1.4.0-2018-12-22.pickle'))

#%%
# Release memory 
del repositories_df


#%%
# Load dependencies
repo_dependencies_path = 'repository_dependencies-1.4.0-2018-12-22.csv'
repo_dependencies_df = pd.read_csv(os.path.join(data_path, repo_dependencies_path), usecols=['ID',\
    'Host Type', 'Repository ID', 'Optional', 'Dependency Project ID'], index_col=False)

#%%
repo_dependencies_df.to_pickle(os.path.join(output_path, 'repository_dependencies-filtered-.pickle'))

#%%
all_ids = set(go_projects_repositories.ID.unique())

#%%
# Filtering only go dependencies
tqdm.pandas()
go_dependencies_df = repo_dependencies_df.progress_apply(lambda x: x['Repository ID'] in all_ids, axis=1)


#%%
go_dependencies_df.to_pickle(os.path.join(output_path, 'go-dependencies.pickle'))

#%%
del repo_dependencies_df