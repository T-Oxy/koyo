import os
import datetime as dt
from datetime import timedelta
import pandas as pd
from s_lib import setup_mongo

icho_tk = [pd.to_datetime(date) for date in pd.date_range(start="2014-11-25", end="2014-12-08", tz="Japan", freq="D")]
icho_hk = [pd.to_datetime(date) for date in pd.date_range(start="2014-10-30", end="2014-11-03", tz="Japan", freq="D")]
icho_is = [pd.to_datetime(date) for date in pd.date_range(start="2014-11-13", end="2014-11-21", tz="Japan", freq="D")]

kaede_tk = [pd.to_datetime(date) for date in pd.date_range(start="2014-11-25", end="2014-12-18", tz="Japan", freq="D")]
kaede_hk = [pd.to_datetime(date) for date in pd.date_range(start="2014-10-30", end="2014-11-03", tz="Japan", freq="D")]
kaede_is = [pd.to_datetime(date) for date in pd.date_range(start="2014-11-26", end="2014-11-29", tz="Japan", freq="D")]

koyo_tk = list(set(icho_tk + kaede_tk))
koyo_hk = list(set(icho_hk + kaede_hk))
koyo_is = list(set(icho_is + kaede_is))

correct_dates = {
    "tk": {"icho": icho_tk, "kaede": kaede_tk, "sonota": koyo_tk, "koyo": koyo_tk},
    "hk": {"icho": icho_hk, "kaede": kaede_hk, "sonota": koyo_hk, "koyo": koyo_hk},
    "is": {"icho": icho_is, "kaede": kaede_is, "sonota": koyo_is, "koyo": koyo_is},
    }

def main():
    db = setup_mongo('2014_twi_naruse')

    print("検索したい県名を入力してください[tk, hk, is]: ")
    pref = input()
    col = db[pref]

    while 1:
        print("検索したい形態素を入力してください: ")
        searchword = input()

        if seachword == "":
            continue

        for date in correct_dates[pref]["koyo"]:
            next_date = date + dt.timedelta(days=1)
            where = {
            'created_at_iso': {
                '$gte': date.isoformat(),
                '$lt': next_date.isoformat()
                }
            }
            # '$or': [ {'icho': 1}, {'kaede': 1}, {'sonota': 1} ]

            for tw in col.find(where):
                morphos = tw["morphos_4class"].split(" ")
                if searchword in morphos:
                    print("-----------")
                    print("text: \n" + tw["text"])
                    print("morpho: \n" + tw["morpho_text"])
                    print("time: \n" + tw["created_at_iso"])
                    print("-----------")

main()
