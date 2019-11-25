"""
    Script responsible to collect the topics + README file of each project.

"""

import pandas as pd
from git import Repo, Commit
import click
from tqdm import tqdm
import numpy as np
import os

def add_commits_info(df, projects_dir):

    name = df['full_name']
    
    # Dict to return the results
    ret = dict()
    ret['id'] = df['id']
    ret['full_name'] = name
    
    # Repo directory 
    project_root = os.path.join(projects_dir, name) 

    try:
        #print('Assess the repository by pointing to the root directory')
        repo = Repo(project_root)
        assert not repo.bare

        # Getting the commits
        commits = list(repo.iter_commits())

        committers = set([i.committer for i in commits])
        authors = set([i.author for i in commits])

        ret['n_committers'] = len(committers)
        ret['n_authors'] = len(authors)
        repo.close() # We need to call close() otherwise gitpython leaks resources

    except KeyboardInterrupt as e:
        raise e

    except BlockingIOError:
        print("Error while processing project %s" % name)
        repo.close()

    except Exception:
        print("Error while processing project %s" % name)
        pass

    
        
    return pd.Series(ret)


@click.command()
@click.argument("input_file", required=1)
@click.argument("projects_dir", required=1)
@click.argument("output_file", required=1)
def enrich_project_metadata(input_file, projects_dir, output_file):

    print('Reading the pickled input file')
    projects_df = pd.read_csv(input_file)

    if 'full_name' not in projects_df.columns:
        print('Input file does not contain the project full_name...')
        print('Aborting...')
        return 

    tqdm.pandas()

    print("Initiating the processing of projects")
    output_df = projects_df.progress_apply(add_commits_info, axis=1, args=(projects_dir,))

    print("Writing the output at %s" % output_file)
    output_df.to_csv(output_file, index=False)

    pass

if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    enrich_project_metadata()    
    pass
