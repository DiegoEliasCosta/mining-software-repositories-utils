import requests
import pandas as pd
import time
import os
import click
from github import Github

@click.command()
@click.argument("username", required=1)
@click.argument("password", required=1)
@click.option("--max_stars", default=None, help="The maximum number of stars - as we order the query, this can be used to find projects below the 1k most starred")
@click.option("--n_pages", default=35, help="The number of pages the request will go over (typically 33) as Github has a limit of 1000 results")
@click.option("--language", default="java", help="The target programming language")
@click.option("--output", default=".", help="The directory where the output will be saved")
def find_most_starred_repos(username, password, max_stars, n_pages, language, output):
    """ Find the most starred repositories using an authenticated GiHub USERNAME and PASSWORD """


    # create a re-usable session object with the user creds in-built
    gh_session = requests.Session()
    gh_session.auth = (username, password)

    if not max_stars:
        max_stars = '*'


    go_url = "https://api.github.com/search/repositories?q=language:{language}+stars:1..{max_stars}&sort=stars&order=desc&page={page}"

    

    df = pd.DataFrame()

    for page in range(1, n_pages):

            req_url = go_url.format(language=language, page=page, max_stars=max_stars)

            print("Querying {query}".format(query=req_url))
            response = gh_session.get(req_url)

            if response:
                content = response.content
                tmp = pd.read_json(content)
                df = df.append(tmp)
                print('{page} Page Requested with success'.format(page=page))

            else:
                print('{page} Page Requested failed'.format(page=page))

            sleep_random()
    pass

    # We pickle first in case we find some issues with converting to JSON  
    # such as non-unique indexes
    df.to_pickle(os.path.join(output, 'moststarred-{language}-projects-{max_stars}.pickle'.format(language=language, max_stars=max_stars)))

    # Making sure we 
    df.reset_index(inplace=True)
    df.to_json(os.path.join(output, 'moststarred-{language}-projects-{max_stars}.json'.format(language=language, max_stars=max_stars)))


def sleep_random():
    from random import randint
    from time import sleep
    sleep(randint(1,7))


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    find_most_starred_repos()
    pass
