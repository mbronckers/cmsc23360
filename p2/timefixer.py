import pandas as pd
import re
import numpy as np

def fix_time(df):
    t_decrement = 0
    last_index = ""
    
    for i, row in df.iterrows():
        if last_index != row['website-index']: # Only reset t_decrement when we see a new website
            t_decrement = row['time']
            last_index = row['website-index']
        df.at[i,'time'] = df.at[i, 'time'] - t_decrement
        
        # Sanity check
        assert df.at[i, 'time'] >= 0, "negative time???"
        
    return df

# Modify this to ones you need 
files = ["aggregate_data/day_1_parsed.csv", "aggregate_data/day_2_parsed.csv", "aggregate_data/day_3_parsed.csv"]
outfiles = ["aggregate_data/day_1_fixed.csv", "aggregate_data/day_2_fixed.csv", "aggregate_data/day_3_fixed.csv"]
col_names = ['website-index', 'time', 'direction','packet size']

for i, file in enumerate(files):
    print(i, file)
    df = pd.read_csv(file, header=0, names=col_names)
    f_df = fix_time(df)
    f_df.to_csv(outfiles[i], index=False)
    