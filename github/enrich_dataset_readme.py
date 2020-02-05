import click
import pandas as pd
import glob
import os
from tqdm import tqdm


def read_content(file_path):

    try:
        with open(file_path, 'r') as content_file:
            return content_file.read()
    except UnicodeDecodeError: 
        return "DecodeError"
    except FileNotFoundError:
        return "FileNotFoundError"

    return None
    
def add_file_info(project, filepreffix, targetdir):

    name = project['full_name']
    
    # Dict to return the results
    ret = dict()
    ret['id'] = project['id']
    ret['full_name'] = name

    project_dir = os.path.join(targetdir, name)

    if not os.path.isdir(project_dir):
        return None

    target_files = [f for f in os.listdir(project_dir) if filepreffix in f.lower()]

    # # Search README file
    # for f in os.listdir(dir):
    #     # Find the first file that matches - considering only lower case
    #     if filepreffix.lower() in f.lower(): 
    #         target_file = f.
    #         break

    for f in target_files:
        ret['readme_filename'] = f
        ret['readme'] = read_content(os.path.join(project_dir, f))

    return pd.Series(ret)


@click.command()
@click.argument("input_file", required=1)
@click.argument("projects_dir", required=1)
@click.argument("output_file", required=1)
def enrich_project_readme(input_file, projects_dir, output_file):

    print('Reading the pickled input file')
    projects_df = pd.read_csv(input_file)

    if 'full_name' not in projects_df.columns:
        print('Input file does not contain the project full_name...')
        print('Aborting...')
        return 

    tqdm.pandas()

    print("Initiating the processing of projects")
    output_df = projects_df.progress_apply(add_file_info, axis=1, args=("readme.md", projects_dir))

    print("Writing the output at %s" % output_file)
    output_df.to_csv(output_file, index=False)

    pass

if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    enrich_project_readme()    
    pass