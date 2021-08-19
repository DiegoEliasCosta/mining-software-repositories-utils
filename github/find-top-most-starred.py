import requests
import pandas as pd
import time
import os
import click
import sys
from github import Github

@click.command()
@click.argument("username", required=1)
@click.argument("password", required=1)
@click.option("--min_stars", default=200, type=int, help="The minimum number of stars a project (we go over the highest number)")
@click.option("--n_pages", default=35, help="The number of pages the request will go over (typically 33) as Github has a limit of 1000 results")
@click.option("--language", default="java", help="The target programming language")
@click.option("--output", default=".", help="The directory where the output will be saved")
def find_most_starred_repos(username, password, min_stars, n_pages, language, output):
    """ Find the most starred repositories using an authenticated GiHub USERNAME and PASSWORD """

    # create a re-usable session object with the user creds in-built
    gh_session = requests.Session()
    gh_session.auth = (username, password)


    go_url = "https://api.github.com/search/repositories?q=language:{language}+stars:{min_stars}..{max_stars}&sort=stars&order=desc&page={page}"

    df = pd.DataFrame()
    # Start with an arbitrary large size (1B)
    max_stars = 1000000000

    while max_stars > min_stars:

        print('Starting a new batch for projects with maxstars = %d' % max_stars)

        for page in range(1, n_pages):

                req_url = go_url.format(language=language, page=page, min_stars=min_stars, max_stars=max_stars)

                print("Querying {query}".format(query=req_url))
                response = gh_session.get(req_url)

                if response:
                    content = response.content
                    tmp = pd.read_json(content)

                    # We need to normalize as the content comes as a json
                    tmp = pd.io.json.json_normalize(tmp['items'])

                    df = df.append(tmp)
                    print('{page} Page Requested with success'.format(page=page))

                else:
                    print('{page} Page Requested failed'.format(page=page))
                    print(f'{response}')

                sleep_random(3, 5) 
        
        # Update max_stars with the smallest number already requested
        # We don't need to request these projects again
        if max_stars == df['stargazers_count'].min():
            # FIXME: This is a problem we need a workaround
            max_stars = max_stars - 1 
        
        else:
            max_stars = df['stargazers_count'].min()

        sleep_random(60, 120)

    # We pickle first in case we find some issues with converting to JSON  
    # such as non-unique indexes
    df.to_pickle(os.path.join(output, 'moststarred-{language}-projects-{min_stars}.pickle'.format(language=language, min_stars=min_stars)))

    # Making sure we 
    df.reset_index(inplace=True)
    df.to_json(os.path.join(output, 'moststarred-{language}-projects-{min_stars}.json'.format(language=language, min_stars=min_stars)))


def sleep_random(min=30, max=120):
    from random import randint
    from time import sleep
    sleep(randint(min,max))


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    find_most_starred_repos()
    pass
