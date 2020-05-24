#!/bin/bash

PROG="open_website.py"
IFACE="Wi-Fi"
ip_D="192.168.178.22" # local IP address of device D

# duration of tshark
SEC="20"

# correct fields
FIELDS="-e frame.number -e frame.time_relative -e ip.src -e ip.dst -e frame.len \
        -e _ws.col.Protocol -e _ws.col.Info"

# capture filter
CAPT_FILT="-Y ip.addr == ${ip_D} and (udp or tcp)"

# csv flags
CSV_FLAGS="-E header=y -E separator=, -E quote=d -E occurrence=f"

# Make raw_data/ if necessary
mkdir -p ../raw_data

# Run collection scripts
for i in 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19
do
    # Start tshark
    fname="../raw_data/runner_"$i".csv"
    tshark -i $IFACE -a duration:$SEC "$CAPT_FILT" -T fields $FIELDS $CSV_FLAGS > $fname & 

    # Access website
    sleep 2
    python3 $PROG -i $i &

    # Wait for next collection
    sleep 28
done

# Get the latest day
name="../raw_data/run_"
i=1
while [ -d $name$i ] ; do
    i=$((i+1))
done
new_folder=$name$i

# Move data
mkdir $new_folder
mv ../raw_data/runner_* $new_folder
