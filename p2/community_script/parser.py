#!/usr/bin/env/python3
# Edited by Max Bronckers
import datetime
import os

def parse_runner(fname, day, run, site_idx, start):
    WEBSITES = [
    "youtube",
    "yahoo",
    "facebook",
    "reddit",
    "netflix",
    "ebay",
    "instructure",
    "twitch",
    "live",
    "stackoverflow",
    "linkedin",
    "irs",
    "imdb",
    "nytimes",
    "cnn",
    "salesforce",
    "okta",
    "wikipedia",
    "imgur",
    "dropbox",
    "zillow",
    "etsy",
    "hulu",
    "quizlet",
    "homedepot"]

    data = []
    outlines = []

    with open(fname, "r") as f:
        data = f.readlines()[1:]

        for d in data:
            elems = [s[1:-1] for s in d.split(",")]

            ip = "192.168.178.22"
            if elems[5] == "HTTP" and (elems[2] == ip or elems[3] == ip):
                site = WEBSITES[site_idx]

                direction = 1 if elems[2] == "192.168.178.22" else 0
                size = elems[4]
                time = elems[1]

                line = f"{site},{time},{direction},{size}\n"
                outlines.append(line)

    return data, outlines, start

def main():
    for day in range(1, 4):
        day_ins = ["frame.number,frame.time,ip.src,ip.dst,frame.len,_ws.col.Protocol,_ws.col.Info\n"]
        day_outs = ["website index,time,direction,packet size\n"]

        for run in range(1, 11):
            run_ins = ["frame.number,frame.time,ip.src,ip.dst,frame.len,_ws.col.Protocol,_ws.col.Info\n"]
            run_outs = ["website index,time,direction,packet size\n"]

            start = None

            for site_idx in range(20):
                runner = f"../raw_data/day_{day}/run_{run}/runner_{site_idx}.csv"

                i, o, start = parse_runner(runner, day, run, site_idx, start)
                run_ins += i
                run_outs += o
                day_ins += i
                day_outs += o

            out_raw = f"../parsed_data/day_{day}/run_{run}_raw.csv"
            out_parsed = f"../parsed_data/day_{day}/run_{run}_parsed.csv"
            os.makedirs(os.path.dirname(out_raw), exist_ok=True)

            with open(out_raw, "w") as f:
                f.writelines(run_ins)

            with open(out_parsed, "w") as f:
                f.writelines(run_outs)

        out_raw = f"../aggregate_data/day_{day}_raw.csv"
        out_parsed = f"../aggregate_data/day_{day}_parsed.csv"
        os.makedirs(os.path.dirname(out_raw), exist_ok=True)

        with open(out_raw, "w") as f:
            f.writelines(day_ins)

        with open(out_parsed, "w") as f:
            f.writelines(day_outs)

if __name__ == "__main__":
    main()

    