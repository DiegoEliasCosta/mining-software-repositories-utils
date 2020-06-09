# %%
import pandas as pd 
import os 
import pydriller
from github import Github
from tqdm import tqdm
import click

# %%

def collect_repository_data(df, client):

    ret = dict()
    try:

        git_url = df['URL']
        project_name = df['full_name']

        repo = client.get_repo(project_name)
        github_data = repo._rawData

        ret['project'] = project_name
        ret['n_commits'] = repo.get_commits().totalCount
        ret['n_contributors'] = repo.get_contributors().totalCount
        ret.update(github_data)

       # We need this to stop the program when we press Ctrl + C
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print("Error while processing project %s - %s" % (project_name, e))

    return pd.Series(ret)


@click.command()
@click.argument("input_file", required=1)
@click.argument("output_file", required=1)
@click.argument("token", required=1)
def repo_stats_collector(input_file, output_file, token):

    print('Accessing Github using the token=%s' % token)
    client = Github(token)

    print('Reading the pickled input file')
    projects_df = pd.read_csv(input_file)

    tqdm.pandas()

    output_df = projects_df.progress_apply(collect_repository_data, axis=1, args=(client,))

    print("Writing the output at %s" % output_file)
    output_df.to_csv(output_file, index=False)

    pass

if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    repo_stats_collector()    
    pass


