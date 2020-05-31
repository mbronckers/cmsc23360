import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os 
from joblib import dump, load
import re
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def directional_packet_size(x):
    if (x['direction'] == 1):
        return -x['packet size']
    else:
        return x['packet size']

def cum_trace(df):    
    # Create a directional packet size column p_i (negative values if outbound)
    df.insert(4, 'p_i', df['packet size'])
    df['p_i'] = df.apply(directional_packet_size, axis=1)

    # Create cumulative packet size trace using directional packet sizes
    df['c_i'] = df.groupby('website-index')['p_i'].cumsum(axis=None)

    return df
def cumulative_packets(df, trace=False):
    # also use ndss2016
    if (trace):
        df = cum_trace(df)

    # cumulative packets counter
    df['cum_count'] = df.groupby('website-index').cumcount()+1

    # cumulative incoming packets counter
    df['cum_inc'] = df.groupby('website-index')['direction'].cumsum(axis=None)

    # cumulative outgoing packets counter
    df['cum_out'] = df['cum_count'] - df['cum_inc']

    # cumulative percentage outgoing/incoming
    df['perc_in'] = df['cum_inc']/(df.groupby('website-index').cumcount()+1)
    df['perc_out'] =  df['cum_out']/(df.groupby('website-index').cumcount()+1)

    return df
def previous_packets(df, prev=False):
    if (prev):
        df = cumulative_packets(df, True)

    # Get 100 previous packet sizes --> we can make it p_i instead of packet_size too
    for i in range(1, 101):
        name = "prev_"+str(i)

        if (prev):
            df[name] = df.groupby('website-index')['p_i'].shift(i)
        else:
            df[name] = df.groupby('website-index')['packet size'].shift(i)

    # Remove NaN
    df.fillna(0, inplace=True)

    return df

def safe_div(q, r):
    if r == 0:
        return 0
    else:
        return q / r

def n_o_statistics(df, prev=False):
    if (prev):
        df = previous_packets(df, True)

    # Total number of packets per session, total number of incoming/outgoing packets + percentages
    curr_index = df.at[0, 'website-index']
    total_inc_packets = 0
    total_out_packets = 0
    inc_values = []
    out_values = []
    total_values = []
    total_incoming_percentage = []
    total_outgoing_percentage = []
    for index, row in df.iterrows():
        if (row['website-index'] != curr_index):
            total_packets = total_inc_packets + total_out_packets

            inc_values.extend([total_inc_packets] * total_packets)
            out_values.extend([total_out_packets] * total_packets)
            total_values.extend([total_packets] * total_packets)

            total_incoming_percentage.extend([safe_div(total_inc_packets, total_packets)] * (total_packets))
            total_outgoing_percentage.extend([safe_div(total_out_packets, total_packets)] * (total_packets))
            curr_index = row['website-index']

            if row['direction'] == 0:
                total_inc_packets = 1
                total_out_packets = 0
            else:
                total_inc_packets = 0
                total_out_packets = 1
        else: 
            if row['direction'] == 0:
                total_inc_packets += 1
            else:
                total_out_packets += 1
    # Repeat for last website index
    total_packets = total_inc_packets + total_out_packets
    inc_values.extend([total_inc_packets] * total_packets)
    out_values.extend([total_out_packets] * total_packets)
    total_values.extend([total_packets] * (total_packets))
    total_incoming_percentage.extend([safe_div(total_inc_packets, total_packets)] * (total_packets))
    total_outgoing_percentage.extend([safe_div(total_out_packets, total_packets)] * (total_packets))

    df['total_incoming'] = inc_values
    df['total_outgoing'] = out_values
    df['total_packets'] = total_values
    df['total_incoming_percentage'] = total_incoming_percentage
    df['total_outgoing_percentage'] = total_outgoing_percentage

    return df

def ordering_statistics(df, prev=False):
    if (prev):
        df = n_o_statistics(df, True)

    # For each successive incoming and outgoing packet, the total number of packets seen before it in the sequence
    """
    e.g. 
    direction successive_num_packets
    0 0 
    0 1
    0 2
    1 0 
    0 0
    0 1
    """
    total_seen = 0
    last_dir = -1
    result = []
    curr_index = ""
    for index, row in df.iterrows():
        if row['website-index'] != curr_index:
            total_seen = 0
            last_dir = -1
            curr_index = row['website-index']
        if row.direction == last_dir:
            total_seen += 1
            result.append(total_seen)
        else:
            total_seen = 0
            result.append(total_seen)
            last_dir = row.direction 
    df['successive_num_packets'] = result

    # The average and standard deviation of the in/outgoing packet ordering list
    curr_index = df.at[0, 'website-index']
    outgoing_vals = []
    incoming_vals = []
    incoming_order_std = []
    outgoing_order_std = []
    outgoing_order_avg = []
    incoming_order_avg = []

    for index, row in df.iterrows():
        if (row['website-index'] != curr_index):
            # Get std of in/outgoing_vals and reset
            curr_index = row['website-index']
            out_std = np.std(outgoing_vals)
            in_std = np.std(incoming_vals)
            out_avg = np.mean(outgoing_vals)
            in_avg = np.mean(incoming_vals)
            total_segment_length = len(outgoing_vals) + len(incoming_vals)
            incoming_order_std.extend([in_std] * total_segment_length)
            outgoing_order_std.extend([out_std] * total_segment_length)
            outgoing_order_avg.extend([out_avg] * total_segment_length)
            incoming_order_avg.extend([in_avg] * total_segment_length)

            if row.direction == 1:
                outgoing_vals = [row['successive_num_packets']]
                incoming_vals = []
            else: 
                incoming_vals = [(row['successive_num_packets']) ]
                outgoing_vals = []

        else:
            if row.direction == 1:
                outgoing_vals.append(row['successive_num_packets'])
            else: 
                incoming_vals.append(row['successive_num_packets']) 

    # Repeat for last segment 
    out_std = np.std(outgoing_vals)
    in_std = np.std(incoming_vals)
    out_avg = np.mean(outgoing_vals)
    in_avg = np.mean(incoming_vals)
    total_segment_length = len(outgoing_vals) + len(incoming_vals)
    incoming_order_std.extend([in_std] * total_segment_length)
    outgoing_order_std.extend([out_std] * total_segment_length)
    outgoing_order_avg.extend([out_avg] * total_segment_length)
    incoming_order_avg.extend([in_avg] * total_segment_length)


    df['outgoing_order_std'] = outgoing_order_std
    df['incoming_order_std'] = incoming_order_std
    df['outgoing_order_avg'] = outgoing_order_avg
    df['incoming_order_avg'] = incoming_order_avg


    return df


def first_last_30(df, prev=False):
    if (prev):
        df = ordering_statistics(df, True)

    # Number of incoming/outgoing packets in the first/last 30 packets 
    curr_index = df.at[0, 'website-index']
    num_inc_first_30_vals = []
    num_out_first_30_vals = []
    num_inc_last_30_vals = []
    num_out_last_30_vals = []
    dirs = []
    # Loop through each segment, grab direction column, take first 30, last 30, sum for in/out 
    for index, row in df.iterrows():
        if (row['website-index'] != curr_index):
            curr_index = row['website-index']
            # Sum up dirs
            ins_first_30 = len(list(filter(lambda d: d == 0, dirs[:30])))
            ins_last_30 = len(list(filter(lambda d: d == 0, dirs[-30:])))
            out_first_30 = len(list(filter(lambda d: d == 1, dirs[:30])))
            out_last_30 = len(list(filter(lambda d: d == 1, dirs[-30:])))
            num_packets = len(dirs)
            num_inc_first_30_vals.extend([ins_first_30] * num_packets)
            num_out_first_30_vals.extend([out_first_30] * num_packets)
            num_inc_last_30_vals.extend([ins_last_30] * num_packets)
            num_out_last_30_vals.extend([out_last_30] * num_packets)

            dirs = [row['direction']]
        else:
            dirs.append(row['direction'])

    ins_first_30 = len(list(filter(lambda d: d == 0, dirs[:30])))
    ins_last_30 = len(list(filter(lambda d: d == 0, dirs[-30:])))
    out_first_30 = len(list(filter(lambda d: d == 1, dirs[:30])))
    out_last_30 = len(list(filter(lambda d: d == 1, dirs[-30:])))
    num_packets = len(dirs)
    num_inc_first_30_vals.extend([ins_first_30] * num_packets)
    num_out_first_30_vals.extend([out_first_30] * num_packets)
    num_inc_last_30_vals.extend([ins_last_30] * num_packets)
    num_out_last_30_vals.extend([out_last_30] * num_packets)

    df['num_inc_first_30_vals'] = num_inc_first_30_vals
    df['num_out_first_30_vals'] = num_out_first_30_vals
    df['num_inc_last_30_vals'] = num_inc_last_30_vals
    df['num_out_last_30_vals'] = num_out_last_30_vals

    return df

def get_segments(df):
    ret = []
    start = 0
    curr_index = df.at[0, 'website-index']
    for index, row in df.iterrows():
        if (row['website-index'] != curr_index):
            curr_index = row['website-index']
            ret.append((start, index - 1))
            start = index

    ret.append((start, index))

    return ret

def get_20s_from_segments(segments):
    # Given an array of start:end tuples, return an array of start2:end2 tuples where end2-start2 == 20, or less if not possible
    # e.g. [(0,45)] => [(0, 19), (20, 39), (40, 45)]
    ret = []
    for s in segments:
        start = s[0]
        end = s[1]
        i = start
        while i + 19 <= end:
            ret.append((i, i + 19))
            i += 20
        ret.append((i, end))
    return ret       

def outgoing_concentration(df, prev=False):
    if (prev):
        df = first_last_30(df, True)

    # Number of outgoing packets in each chunk of 20 packets per segment
    # get an array of indexes for each segment 
    segments = get_segments(df)
    segment_20s = get_20s_from_segments(segments)    
    num_outgoing_vals = [] # Don't add this to the data, we only need it to collect statistics
#     debug = []
    for s in segment_20s:
        start = s[0]
        end = s[1]
        num_outs = df.iloc[start:end+1][df.direction == 1].shape[0]
        num_outgoing_vals.append(num_outs)
#         debug.extend([num_outs] * (end - start + 1))


    # We want to get the standard deviation, mean of the num_outgoing_vals for each segment
    # For each segment in segments, we want to obtain the corresponding values in num_outgoing_vals 
    # which are segmentized by 20s
    outgoing_20_std = []
    outgoing_20_avg = []

    for segment in segments:
        start = segment[0]
        end = segment[1]
        values = []
        for i in range(len(segment_20s)):
            seg20 = segment_20s[i]
            if seg20[0] < start:
                continue
            if seg20[0] > end:
                break
            values.append(num_outgoing_vals[i])
        mean = np.mean(values)
        std = np.std(values)
        outgoing_20_avg.extend([mean] * (end - start + 1))
        outgoing_20_std.extend([std] * (end - start + 1))

    df['outgoing_20_avg'] = outgoing_20_avg
    df['outgoing_20_std'] = outgoing_20_std
#     df['debug'] = debug


    return df

def preprocess(df_input): 
    df_processed = outgoing_concentration(df_input, prev=True)
    
    return df_processed


def reformat(df): 
    X_test = df.loc[:, df.columns != 'website-index']
    y_test = df['website-index']
    return X_test, y_test
    
