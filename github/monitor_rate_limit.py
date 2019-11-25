from github import Github
import click
from time import sleep


@click.command()
@click.argument("username", required=1)
@click.argument("password", required=1)
@click.option("--refresh_seconds", default=10, type=int, help="Refresh every X seconds")
def monitor_rate_limit(username, password, refresh_seconds):

    g = Github(username, password)

    while True:
        # Print the rate limit
        print(g.get_rate_limit())
        sleep(refresh_seconds)
        pass

    pass


if __name__ == "__main__":
        # pylint: disable=no-value-for-parameter
    monitor_rate_limit()
    
    pass

