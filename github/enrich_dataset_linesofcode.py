# %%
import pandas as pd
from tqdm import tqdm
import click


import glob 
def count_lines_of_code(project, dataset_source, extension):
    """
        Pythonic style
        Inspects each directory and uses glob to extract all go files
        Reads each go file and returns the sum of all LOC 
    """
    project_id = project['full_name']
    path = dataset_source + project['full_name']

    # List all go files
    files = [f for f in glob.glob(path + "/**/*.%s" % extension, recursive=True)]
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
    command = "( find ./ -name '*.%s' -print0 | xargs -0 cat ) | wc -l" % extension

    project_id = project['full_name']
    path = dataset_source + project['full_name']
    return pd.Series({"id": project['id'],\
        "full_name": project_id,\
        "LOC": int(subprocess.check_output(command, shell=True, cwd=path))})


@click.command()
@click.argument("input_file", required=1)
@click.argument("extension", required=1)
@click.argument("projects_dir", required=1)
@click.argument("output_file", required=1)
def enrich_project_metadata(input_file, extension, projects_dir, output_file):

    print('Reading the csv input file')
    projects_df = pd.read_csv(input_file)

    if 'full_name' not in projects_df.columns:
        print('Input file does not contain the project full_name...')
        print('Aborting...')
        return 

    tqdm.pandas()

    print("Initiating the processing of projects")
    loc_df = projects_df.progress_apply(fast_count_lines_of_code, axis=1, args=(projects_dir, extension))

    print("Writing the output at %s" % output_file)
    loc_df.to_csv(output_file, index=False)

    pass

if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    enrich_project_metadata()    
    pass



# %%
