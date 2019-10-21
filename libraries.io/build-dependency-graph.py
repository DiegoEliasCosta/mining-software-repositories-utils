#%%
import pandas as pd
import sqlite3
import networkx
import os

data_path = '../../../data/libraries.io/libraries-1.4.0-2018-12-22/'
db_path = os.path.join(data_path, 'database', 'libraries-io.db')



#%%
# Connecting to the DB
conn = sqlite3.connect(db_path)
# The cursor is the API entry-level for our queries
cursor = conn.cursor() 

#%%
#dependency_graph_df = pd.read_sql_query('`Repository ID`, ')

