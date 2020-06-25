"""
2015年のDBから、日毎ににフラグが立っているツイート数をカウントする
"""
from pymongo import MongoClient
from s_lib import setup_mongo, setup_mecab
from datetime import datetime
from datetime import timedelta

result_dir = '/now24/naruse/out/'

def daterange(_start, _end):
    for n in range((_end - _start).days):
        yield _start + timedelta(n)

def count(db, f_name):
    #日毎のフラグが1のツイート数が入っているリストを返す。リストの要素は"day'\t'month'\t'count"の文字列
    all_day_list = []

    start = datetime.strptime('2015-02-23', '%Y-%m-%d')
    end = datetime.strptime('2015-12-31', '%Y-%m-%d')

    for date in daterange(start, end):
        today = date.isoformat()
        next_day = (date + timedelta(days=1)).isoformat()

        when = {
            'created_at_iso': {
                '$gte': today,
                '$lt': next_day
            }
        }

        month = str(date.month).zfill(2)
        day = str(date.day).zfill(2)

        collection = db['2015-' + m]
        one_day_count = col.find(when).count()

        one_day = '\t'.join([month, day, str(one_day_count)])
        all_day_list.append(one_day)

    return all_day_list

def main():
    tk_icho_path = result_dir + "daily_count_tk_icho.tsv"
    db_tk = setup_mongo('2015_tk_twi')

    all_day_list = count(db_tk, 'icho')

    with open(tk_icho_path, 'w') as outf:
        outf.write('\n'.join(all_day_list))

main()
