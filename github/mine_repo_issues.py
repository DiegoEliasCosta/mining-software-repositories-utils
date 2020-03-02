"""
    Script responsible for mining issues from a repo
"""

import pandas as pd
from github import Github
import click
import os
from itertools import cycle
from tqdm import tqdm
import numpy as np
from time import sleep
from github import Github, GithubException, GithubObject
from urllib3.util.retry import Retry

def sleep_random(max):
    from random import randint
    sleep(randint(1,max))

# FIXME: Remove this after the first use
TOKENS = [
  #  'b2bdaa2663178d832b16fe34b376be549d5fd06a',  # shassankhatoonabadi
  #  '010331afa1fc53a51378b2e31a08f786f23f5b4b',  # DiegoEliasCosta
  #  'd598715deb5cc19759db618d2a0ad4d23748f93c',  # ahmad-abdellatif
  #  '29d7055440bb9173a7e41081e8eea90d525b78ac',  # Mhmdelshf
  #  '222c76e405a021c34a8ed9b7a35f4aa0a3eceb17',  # atchowdhury
    'a5e72385b1b406e2663a9f0cb0d30b43af6bbbd2',  # abbasjavan
    'd9a0f2c51e6368ca5819b72f06b76dec6f8c1c09',  # MahsaAfzali
    'ead4d0406eea1fbbd6169171abb05c8383db406a',  # KhaledBadran
]
tokens = cycle(TOKENS)

def github_client(per_page=100):
    token = next(tokens)
    print(f'Created new GitHub client with token {token}')

    return Github(
        token,
        per_page=per_page,
        retry=Retry(total=None, status_forcelist=[502])
    )

# GLOBAL
github_client = github_client()

def mine_issues(df, output_file_path, project_col):

    name = df[project_col]
    ret = list()

    done = False
    while not done:

        try:
            # Getting the projects
            global github_client
            repo = github_client.get_repo(name)
            
            # Retrieving the topics
            issues = list(repo.get_issues(state='all'))

            for i in issues:
                # Append a dictionary
                # We use _rawData because we dont want to issue another request
                # FIXME: Update this with a parameter
                issue_data = i._rawData
                issue_data['full_name'] = name
                ret.append(issue_data)


            done = True
        # We need this to stop the program when we press Ctrl + C
        except GithubException:
            github_client = github_client()
        except KeyboardInterrupt:
            done = True
            raise
        except Exception as e:
            done = True
            print("Error while processing project %s - %s" % (name, e))

    df = pd.DataFrame(ret)
    out_file_name = name.replace('/', '-') + '.csv'
    df.to_csv(os.path.join(output_file_path, out_file_name), index=False)

    pass

@click.command()
@click.argument("input_file", required=1)
@click.argument("output_file_path", required=1)
@click.option("--project-col", default='full-name', help='Specify the project column name in the input file.')

def mine_repo_issues(input_file, output_file_path, project_col):

    print('Reading the csv input file')
    projects_df = pd.read_csv(input_file)

    print(f'Using project_col = {project_col}')

    if project_col not in projects_df.columns:
        print('Input file does not contain the project full_name...')
        print('Aborting...')
        return 

    tqdm.pandas()

    projects_df.progress_apply(mine_issues, axis=1, args=(output_file_path, project_col))


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    mine_repo_issues()    
    pass
