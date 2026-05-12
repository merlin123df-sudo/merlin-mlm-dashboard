import pandas as pd
import os
files = {
    'clickpost': 'raw_data/20260509_1330_CLICKPOST (1).csv',
    'dispatch': 'raw_data/20260509_1330_dispatch (1).csv',
    'so': 'raw_data/20260509_1330_so (1).csv',
    'kitting': 'raw_data/20260509_1330_kitting (1).xlsx'
}
for name, path in files.items():
    print('---', name, '---')
    if not os.path.exists(path):
        print('MISSING', path)
        continue
    if path.endswith('.csv'):
        df = pd.read_csv(path, on_bad_lines='skip')
    else:
        df = pd.read_excel(path)
    print('shape', df.shape)
    print('columns', df.columns.tolist()[:40])
    print('sample rows:')
    print(df.head(3).to_string(index=False))
    print('nulls count:')
    print(df.isna().sum().sort_values().head(15))
    print()