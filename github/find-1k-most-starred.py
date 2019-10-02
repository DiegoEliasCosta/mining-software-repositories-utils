import requests
import pandas as pd
import time
import os
import click
from github import Github

@click.command()
@click.argument("username", required=1)
@click.argument("password", required=1)
@click.option("--n_pages", default=35, help="The number of pages the request will go over (typically 33) as Github has a limit of 1000 results")
@click.option("--language", default="java", help="The target programming language")
def find_1k_most_starred_repos(username, password, n_pages, language):
    """ Find the most starred repositories using an authenticated GiHub USERNAME and PASSWORD """


    # create a re-usable session object with the user creds in-built
    gh_session = requests.Session()
    gh_session.auth = (username, password)

    go_url = "https://api.github.com/search/repositories?q=language:{language}&stars:1..*&sort=stars&order=desc&page={page}"

    df = pd.DataFrame()

    for page in range(1, n_pages):

            req_url = go_url.format(language=language, page=page)

            response = gh_session.get(req_url)

            if response:
                content = response.content
                tmp = pd.read_json(content)
                df = df.append(tmp)
                print('{page} Page Requested with success'.format(page=page))

            else:
                print('{page} Page Requested failed'.format(page=page))

            time.sleep(.1)
    pass

    df.to_csv(os.path.join('top-1kmoststarred-{language}-projects.csv'.format(language=language)))



if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    find_1k_most_starred_repos()
    pass
