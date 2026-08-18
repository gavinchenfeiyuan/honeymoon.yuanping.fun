# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime, timedelta

compensate = -25

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH_JSON = os.path.join(BASE, "path.json")


def load_plan():
    with open(PATH_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("plan", [])


def now_local():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def parse_date(ymd):
    return datetime.strptime(ymd, "%y%m%d").date()


def days_diff(ymd):
    today = datetime.now().date()
    d = parse_date(ymd)
    return (d - today).days + compensate


def compensated_date(ymd, ndays):
    d = parse_date(ymd)
    return d + timedelta(days=ndays)


if __name__ == "__main__":
    print("本地时间:", now_local())
    print()
    for p in load_plan():
        name = p.get("name", "")
        coordinate = p.get("coordinate", "")
        date = p.get("date", "")
        diff = days_diff(date) if date else None
        diff_str = f"{diff:+d}d" if diff is not None else ""
        cdate = compensated_date(date, compensate) if date else ""
        print(f"{diff_str:>6s}  {date}  {cdate}  {name}, {coordinate}")
