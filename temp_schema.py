import sqlite3
import pandas as pd
conn = sqlite3.connect('processed_db/warehouse.db')
print(conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall())
for tbl in ['clickpost_table','dispatch_table','so_master','kitting_table']:
    print('TABLE', tbl)
    df = pd.read_sql(f'SELECT * FROM {tbl} LIMIT 5', conn)
    print(df.columns.tolist())
    print(df.head(2).to_string(index=False))
conn.close()
