# %%
import pandas as pd
from tqdm import tqdm
import click
import os

import glob 
def count_lines_of_code(project, dataset_source):
    """
        Pythonic style
        Inspects each directory and uses glob to extract all go files
        Reads each go file and returns the sum of all LOC 
    """
    project_id = project['full_name']
    path = dataset_source + project['full_name']

    # List all go files
    files = [f for f in glob.glob(path + "/**/*.go", recursive=True)]
    # Remove the vendor ones (dependencies)
    files = [f for f in files if not 'vendor' in f]

    # Count lines of code
    num_lines = 0
    for f in files:
        try:
            num_lines += sum(1 for line in open(f))
        except: # Some crazy people will name a directory with the suffix .go
            continue

    return {'full_name': project_id, 'LOC': num_lines}


import subprocess
def fast_count_lines_of_code(project, dataset_source, extension):
    """ 
        OS style - Ask the OS to simply search for all go files
        and return the summed wc -l
        This is a couple of order of magnitudes faster
    """
    # From https://stackoverflow.com/questions/1358540/how-to-count-all-the-lines-of-code-in-a-directory-recursively
    command = f"( find ./ -name '*.{extension}' -print0 | xargs -0 cat ) | wc -l"

    project_id = project['full_name']
    path = dataset_source + project['full_name']
    return pd.Series({"id": project['id'],\
        "full_name": project_id,\
        "LOC": int(subprocess.check_output(command, shell=True, cwd=path))})


def cloc_lines_of_code(project, dataset_source, language):
    """
        Use the CLOC tool to count the lines of code (more precise).
       
    """
    project_name = project['full_name']
    path = dataset_source + project['full_name']

    cmd = f"cloc --csv --report-file=tmp.csv --include-lang={language} --by-file *"
    ret = subprocess.run(cmd, capture_output=True, shell=True, cwd=path)

    # Check if the command was executed without errors
    ret.check_returncode()
    ret_out = ret.stdout.decode('ascii')

    loc_df = pd.read_csv(os.path.join(dataset_source, project_name, 'tmp.csv'))
    os.remove(os.path.join(dataset_source, project_name, 'tmp.csv')) # Remove file

    loc_df['project'] = project_name
    return loc_df


@click.command()
@click.argument("input_file", required=1)
@click.argument("projects_dir", required=1)
@click.argument("output_file", required=1)
@click.option("--extension", defailt=None, description='Specify the extension as in (java -> .java) for the fastest loc count.')
@click.option("--language", default=None, description='Only count files of a programming languauge. See cloc --show-lang for support.')
def enrich_project_metadata(input_file, projects_dir, output_file, extension, language):

    print('Reading the pickled input file')
    projects_df = pd.read_csv(input_file)

    if 'full_name' not in projects_df.columns:
        print('Input file does not contain the project full_name...')
        print('Aborting...')
        return 

    tqdm.pandas()

    print("Initiating the processing of projects")
    
    if language:
        loc_df = projects_df.progress_apply(cloc_lines_of_code, axis=1, args=(projects_dir, language))

    elif extension:
        loc_df = projects_df.progress_apply(fast_count_lines_of_code, axis=1, args=(projects_dir,))

    print("Writing the output at %s" % output_file)
    loc_df.to_csv(output_file, index=False)

    pass

if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    enrich_project_metadata()    
    pass
