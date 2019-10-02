import os
import click
from git import Repo
import pandas as pd
from tqdm import tqdm

counter = 1

def clone_repository(df, output):
    """
    Clone repositories 
    """
    
    git_url = df['items']['clone_url']
    project_name = df['items']['full_name']
    
    project_folder = os.path.join(output, project_name)

    # Here we assume that if a folder has already been created
    # the repo has already beeing cloned
    if not os.path.exists(project_folder):
        os.makedirs(project_folder)
        global counter
        click.echo("Cloning the %d project %s" % (counter, project_folder))
        counter += 1
        
        try:
            # Clone the repository
            Repo.clone_from(git_url, project_folder)
        except:
            click.echo("Error while trying to clone the repository %s" % git_url)
        
    

@click.command()
@click.argument("file_name", required=1)
@click.option("--output", default=".", help="The output folder where the projects will be cloned into (default: current dir)")
def repo_cloner(file_name, output):
    """ Clone repositories from a FILENAME with results from GitHub API """


    # Create the dataframe with the content from the JSON returned by GitHub API
    #dataset = pd.read_json(file_name, encoding='ISO-8859-1')
    dataset = pd.read_pickle(file_name)

    # Register `pandas.progress_apply` and `pandas.Series.map_apply` with `tqdm`
    # (can use `tqdm_gui`, `tqdm_notebook`, optional kwargs, etc.)
    tqdm.pandas(desc="Progress bar")

    projects = pd.DataFrame(dataset['items'])
    
    # Clone the repository for each row of url in the dataframe
    projects.progress_apply(clone_repository, axis=1, args=(output, ))        
    
    pass


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    repo_cloner()
    pass