"""
    Script responsible to collect the topics + README file of each project.
    FIXME: We are currently not using README in our analysis so the enriched dataset
    is kept in the rawdata folder
"""

import pandas as pd
from github import Github
import click
from tqdm import tqdm
import numpy as np
from time import sleep

def sleep_random(max):
    from random import randint

    sleep(randint(1,max))


# TODO: Deprecated - We will not use this anymore
def get_file_content(filename, repo):

    try:
        file_content = repo.get_contents(filename)
        encoding = file_content.encoding

        if encoding == 'base64':
            import base64
            return base64.b64decode(file_content.content)

        else:
            print('Encoding %s not supported' % encoding)
            return None

    except KeyboardInterrupt:
        raise
    except Exception as e:
        print("Cannot GET file content %s - %s" % (filename, e))

    return None


def find_file_content(filenamepreffix, repo):

    try:

        # Get all file content in the root directory
        files = repo.get_contents("")

        target_file = None
        for f in files:
            # Find the first file that matches - considering only lower case
            if filenamepreffix.lower() in f.path.lower(): 
                target_file = f
                break

        encoding = target_file.encoding

        if encoding == 'base64':
            import base64
            return base64.b64decode(target_file.content)  

        else:
            return None

    except KeyboardInterrupt:
        raise
    except Exception as e:
        print("Cannot FIND file content %s - %s" % (filenamepreffix, e))    


def add_topics_readme(df, github, sleep):

    name = df['full_name']
    ret = dict()
    ret['id'] = df['id']
    ret['full_name'] = name
    try:
        # Getting the projects
        repo = github.get_repo(name)
        
        # Retrieving the topics
        topics = repo.get_topics()
        ret['topics'] = topics


    # We need this to stop the program when we press Ctrl + C
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print("Error while processing project %s - %s" % (name, e))

    #sleep_random(sleep)
    return pd.Series(ret)


@click.command()
@click.argument("input_file", required=1)
@click.argument("output_file", required=1)
@click.argument("user", required=1)
@click.argument("password", required=1)
@click.option("--split", default=10, help="As GitHub has a limit of 5000, we can split the processing into buckets and process each bucket in an hour")
#@click.option('--sleep', default=2, help='How long to sleep in between requests to bypass network security.')
def enrich_project_description(input_file, output_file, user, password, split):

    print('Accessing Github using the username=%s' % user)
    g = Github(user, password)

    print('Reading the pickled input file')
    projects_df = pd.read_csv(input_file)

    if 'full_name' not in projects_df.columns:
        print('Input file does not contain the project full_name...')
        print('Aborting...')
        return 

    tqdm.pandas()

    print('Splitting projects into buckets of size %d' % split)
    dfs = np.split(projects_df, [split], axis=0)

    for idx, df in enumerate(dfs):

        print("Starting the batch %d" % idx)
        output_df = df.progress_apply(add_topics_readme, axis=1, args=(g, sleep))

        output_file_name = output_file.replace('.csv', '-part-%d.csv' % (idx + 1))

        print("Writing the output at %s" % output_file_name)
        output_df.to_csv(output_file_name, index=False)

        # This should sleep for slightly more than an hour
        sleep(10)
    pass

if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    enrich_project_description()    
    pass
