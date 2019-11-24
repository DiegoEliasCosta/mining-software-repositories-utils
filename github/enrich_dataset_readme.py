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


def sleep_random(max):
    from random import randint
    from time import sleep
    sleep(randint(1,max))


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

        # Project labels
        labels = repo.get_labels()
        ret['labels'] = labels
        
        # "Retrieving the README
        # Attempt 1
        #print('Attempting to retrive the README for project %s' % name)
        readme_content = get_file_content('README.md', repo)

        if not readme_content:
            readme_content = find_file_content('readme', repo)
        ret['readme'] = readme_content
        

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
@click.option('--sleep', default=2, help='How long to sleep in between requests to bypass network security.')
def enrich_project_description(input_file, output_file, user, password, sleep):

    print('Accessing Github using the username=%s' % user)
    g = Github(user, password)

    print('Reading the pickled input file')
    projects_df = pd.read_csv(input_file)

    if 'full_name' not in projects_df.columns:
        print('Input file does not contain the project full_name...')
        print('Aborting...')
        return 

    tqdm.pandas()

    print("Initiating the processing of projects")
    output_df = projects_df.progress_apply(add_topics_readme, axis=1, args=(g, sleep))

    print("Writing the output at %s" % output_file)
    output_df.to_csv(output_file, index=False)


    pass

if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    enrich_project_description()    
    pass
