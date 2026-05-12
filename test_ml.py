import pandas as pd
from ml_engine import get_inventory_gap
try:
    result = get_inventory_gap()
    print('Type:', type(result))
    print('Empty:', result.empty)
    if not result.empty:
        print('Columns:', result.columns.tolist())
        print('Head:', result.head())
    else:
        print('Result is empty')
except Exception as e:
    import traceback
    print('Error:', e)
    traceback.print_exc()