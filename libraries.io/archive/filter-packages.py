#%%
import pandas as pd
import os
from tqdm import tqdm


#%%
# Loading the dataset
data_path = '../../data/libraries.io/libraries-1.4.0-2018-12-22/'
file_path = 'projects-1.4.0-2018-12-22.csv'
output_path = '../../data/libraries.io/libraries-1.4.0-2018-12-22/go'

projects_df = pd.read_csv(os.path.join(data_path, file_path))
print("Libraries.io dataset contains %d projects" % len(projects_df))

#%%
# Checking the programming languages
languages = projects_df['Language'].unique()
print("%d programming languages" % len(languages))

#%%
# Filtering Go projects
go_projects = projects_df[projects_df.Language == 'Go']
print("From %d projects (packages) - %d are of language Go " % (len(projects_df), len(go_projects)))
go_projects.to_pickle(os.path.join(output_path, 'projects-go-1.4.0-2018-12-22.pickle'))

#%%
# Loading all project versions
versions_path = 'versions-1.4.0-2018-12-22.csv'
versions_df = pd.read_csv(os.path.join(data_path, versions_path))

#%%
# Merging Go projects + versions
go_projects_versions = pd.merge(go_projects, versions_df, left_on='ID', right_on='Project ID',\
    how='left', suffixes=('_p', '_v'))
# Saving into disk
go_projects_versions.to_pickle(os.path.join(output_path, 'projects-go-versions-1.4.0-2018-12-22.pickle'))

#%%
# Double-checking the merged data
print('# of Projects %d | # of Versions %d' % (go_projects_versions.ID_p.count(), go_projects_versions.ID_v.count()))
print('# of unique projects %d' % len(go_projects_versions.ID_p.unique()))
print('# of unique versions %d' % len(go_projects_versions.ID_v.unique()))

h = go_projects_versions.head(10000)

#%%
go_projects_versions.Platform_p.value_counts()

#%%
# Reading only the: ID, Platform, Project ID, Version ID of the repository dependencies
# This may take a LONG time but it only consumes a small share of the data in memory
dependencies_path = 'dependencies-1.4.0-2018-12-22.csv'
dependencies_df = pd.read_csv(os.path.join(data_path, dependencies_path), usecols=['ID', 'Platform',\
    'Project ID', 'Version ID'])

#%%
# Filtering only dependencies from Go Platform
go_dependencies_df = dependencies_df[dependencies_df.Platform == 'Go']
go_dependencies_df.to_pickle(os.path.join(output_path, 'dependencies-go-1.4.0-2018-12-22.pickle'))

#%%
# Statistics over the dependencies
dependencies_df.Platform.unique()