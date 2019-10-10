# %%
# Script for inserting large CSV files into a SQLLITE for further querying
# Based on: *
import pandas as pd
import os
import tqdm
import sqlite3
import click

# Establishing the table variables
from collections import namedtuple
Table = namedtuple('Table', 'csv name')

@click.command()
@click.argument("csv-dir", required=1)
@click.option("--version", default="1.4.0-2018-12-22", help="The dataset version (e.g., 1.4.0-2018-12-22)")
@click.option("--output", default="./libraries-io.db", help="The output file where the SQLLITE database will be saved into (default: ./libraries-io.db)")
def import_sql_lite(csv_dir, version, output):
    """ Import the csv files of Libraries.IO into a sqllite instance """

    # Establish a connection
    conn = sqlite3.connect(output)

    # The cursor is the API entry-level for our queries
    cursor = conn.cursor() 

    tables = [
        Table("projects_with_repository_fields-%s.csv" % version, "PROJECTS_REPO"),
        # Repositories CSV file have misaligned Header + content
        # We need to enforce Pandas to disconsider the index otherwise
        # the df will pick ID as the index and shift all columns to the right
        
        # Also, typically these two tables are not needed
        #Table("projects-%s.csv" % version, "PROJECTS"),
        #Table("repositories-%s.csv" % version, "REPOSITORIES"),
        # ------------------------------
        Table("versions-%s.csv" % version, "VERSIONS"),
        Table("dependencies-%s.csv" % version, "DEPENDENCIES"),
        Table("repository_dependencies-%s.csv" % version, "REPOSITORY_DEPENDENCIES"),
        Table("tags-%s.csv" % version, "TAGS")
    ]


    print('Populating the database - This process may take from 30-60 minutes')
    for table in tables:
        print("Populating table %s" % table.name)
        for chunk in pd.read_csv(os.path.join(csv_dir, table.csv), index_col=False, chunksize=5000000):
            chunk.to_sql(name=table.name, con=conn, if_exists="append", index=False)  #"name" is name of table 
            print('Chunk finished - ID: %d' % chunk.iloc[0].ID)


    # print('Creating all UNIQUE ID indexes')
    cursor.execute("CREATE UNIQUE INDEX id_projects ON PROJECTS (ID)")
    cursor.execute("CREATE UNIQUE INDEX id_repositories ON REPOSITORIES (ID)")
    cursor.execute("CREATE UNIQUE INDEX id_versions ON VERSIONS (ID)")
    cursor.execute("CREATE UNIQUE INDEX id_dependencies ON DEPENDENCIES (ID)")
    cursor.execute("CREATE UNIQUE INDEX id_repositorydependencies ON REPOSITORY_DEPENDENCIES (ID)")
    conn.commit()

    #%%
    # Check all tables
    all = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print('Showing the schema of the database')
    print(all.fetchall())
    


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    import_sql_lite()
