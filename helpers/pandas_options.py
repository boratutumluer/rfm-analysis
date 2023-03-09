import pandas as pd
def set_pandas_options(max_rows=None, max_columns=None, width=500, precision=3):
    pd.set_option('display.max_rows', max_rows)
    pd.set_option('display.max_columns', max_columns)
    pd.set_option('display.width', width)
    pd.set_option("display.float_format", lambda x: f'%.{precision}f' % x)
    print(f"Max Rows: {max_rows}, Max Cols: {max_columns}, Width: {width}, Precision: {precision}")
