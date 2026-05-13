import pandas as pd
import sqlite3
import os
import glob
import shutil
from datetime import datetime

# Path Configuration
RAW_FOLDER = 'raw_data/'
ARCHIVE_FOLDER = 'archive/'
DB_PATH = 'processed_db/warehouse.db'

def run_pipeline():
    # Folder check
    for folder in [RAW_FOLDER, ARCHIVE_FOLDER, 'processed_db']:
        if not os.path.exists(folder): os.makedirs(folder)

    conn = sqlite3.connect(DB_PATH)
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    
    try:
        files = {
            'dispatch': glob.glob(os.path.join(RAW_FOLDER, '*dispatch*.csv')),
            'so': glob.glob(os.path.join(RAW_FOLDER, '*so*.csv')),
            'kitting': glob.glob(os.path.join(RAW_FOLDER, '*kitting*.xlsx')),
            'cp': glob.glob(os.path.join(RAW_FOLDER, '*CLICKPOST*.csv'))
        }

        found_any = any(files.values())
        if not found_any:
            return False, "⚠️ No uploaded raw files found. Use the sidebar upload button and click data sync."

        for key, paths in files.items():
            if paths:
                if 'kitting' in key:
                    df_new = pd.read_excel(paths[0])
                    if 'CreatedOn' in df_new.columns:
                        df_new['CreatedOn'] = pd.to_datetime(df_new['CreatedOn']).dt.date
                else:
                    df_new = pd.read_csv(paths[0], on_bad_lines='skip')

                table_map = {
                    'dispatch': 'dispatch_table',
                    'so': 'so_master',
                    'kitting': 'kitting_table',
                    'cp': 'clickpost_table'
                }
                
                table_name = table_map[key]
                unique_keys = {
                    'dispatch_table': 'OrderNo',
                    'so_master': 'OrderNo',
                    'kitting_table': 'KitNo',
                    'clickpost_table': 'AWB'
                }
                
                unique_col = unique_keys.get(table_name)
                if unique_col and unique_col in df_new.columns:
                    # Check if table exists
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
                    table_exists = cursor.fetchone()
                    
                    if table_exists:
                        # Get existing unique values
                        cursor.execute(f"SELECT DISTINCT {unique_col} FROM {table_name}")
                        existing = set(row[0] for row in cursor.fetchall())
                        # Filter new data
                        df_new = df_new[~df_new[unique_col].isin(existing)]
                        if df_new.empty:
                            continue  # No new data
                    
                # Append only new data
                inserted_count = df_new.shape[0]
                if inserted_count > 0:
                    df_new.to_sql(table_name, conn, if_exists='append', index=False)
                    print(f"Inserted {inserted_count} new records into {table_name}")
                
                # Move to archive
                shutil.move(paths[0], os.path.join(ARCHIVE_FOLDER, f"{ts}_{os.path.basename(paths[0])}"))

        conn.close()
        return True, "✅ Smart pipeline: only new records were added, duplicates were skipped, files were archived!"
    except Exception as e:
        if conn: conn.close()
        return False, f"❌ Pipeline error: {str(e)}"