import csv
import logging
import time
from random import random
from github import Github
from os import environ
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(format='%(asctime)s - %(message)s',
                    datefmt='%d-%m-%Y %H:%M:%S', level=logging.INFO)
seen = set()


def main():
    g = Github(environ.get("GITHUB_ACCESS_TOKEN"),   per_page=100)
    f = open('repositories.csv', 'w', newline='')
    writer = csv.writer(f)
    writer.writerow([
        "full_name",
        "description",
        "stargazers_count",
        "forks_count",
        "open_issues_count",
        "watchers_count",
        "created_at",
        "updated_at",
        "pushed_at",
        "clone_url",
        "is_archived",
        "is_fork",
        "default_branch",
        "owner_type",
        "size"
    ])

    max_stars = 1000000
    min_stars = 100

    while max_stars >= min_stars:
        logging.info(
            "fetching repositories with stars count less than: %s" % max_stars)

        res = g.search_repositories("language:Java stars:%s..%s" % (min_stars, max_stars),
                                    sort="stars",
                                    order="desc")

        for repo in res:
            if repo.full_name in seen:
                logging.debug("skip: %s" % repo.full_name)
                continue
            seen.add(repo.full_name)

            logging.debug("write: %s - stars: %s" %
                          (repo.full_name, repo.stargazers_count))
            writer.writerow([
                repo.full_name,
                repo.description, 
                repo.stargazers_count,
                repo.forks_count,
                repo.open_issues_count,
                repo.watchers_count,
                repo.created_at,
                repo.updated_at,
                repo.pushed_at,
                repo.clone_url,
                repo.archived,
                repo.fork,
                repo.default_branch,
                repo.owner.type,
                repo.size
            ])

        if max_stars == min_stars:
            break

        max_stars = repo.stargazers_count
        sleep_seconds = 2 + (random() * 8)
        logging.info("sleeping for %ss" % sleep_seconds)
        time.sleep(sleep_seconds)

    f.close()
    logging.info("done!")


if __name__ == '__main__':
    logging.info("starting the repository fetching process")
    main()
