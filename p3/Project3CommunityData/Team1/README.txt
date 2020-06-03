Project Submission for

Notes:
Instead of Day 1-14, we have Day 1-28, which just includes the second run of each day as a different day. To find the day, just devide by 2 and round up. If it was an even day, its the second submission, odd is the first submission. So for example Day 17 is really 17/2 = 8.5 which rounds to Day 9, and was the first run of that day.

On the submission labled Day 2, the clock on the virtual machine was wrong - even though we ran it at the correct time, the clock had reset, so we went in and changed the timestamps to reflect the true time, but all of the data was left intact.

Finally, there were 4 places where the program failed to parse Pings and or Tracerouts, so we had to replace them with dummy's that had all 0's. In the clean data, we changed each 0.0 to N/A. The places that occurs is

1. Day 13, Sequence 2, Amazon.de Traceroute command
2. Day 13, Sequence 2, BBC Ping command
3. Day 13, Sequence 3, Wikipedia.jp Ping command
4. Day 15, Sequence 2, Walmart Traceroute command
