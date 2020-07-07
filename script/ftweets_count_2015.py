"""
2015年のDBから、日毎の""フラグが立っている""ツイート数をカウントする
"""
from pymongo import MongoClient
from s_lib import setup_mongo, setup_mecab
from datetime import datetime
from datetime import timedelta

result_dir = '/now24/naruse/out/'

def daterange(_start, _end):
    for n in range((_end - _start).days):
        yield _start + timedelta(n)

def count_flag(db, f_name):
    #日毎のフラグが1のツイート数が入っているリストを返す。リストの要素は"day'\t'month'\t'count"の文字列
    all_day_list = []

    start = datetime.strptime('2015-02-17', '%Y-%m-%d')
    end = datetime.strptime('2015-12-31', '%Y-%m-%d')

    for date in daterange(start, end):
        today = date.isoformat()
        next_day = (date + timedelta(days=1)).isoformat()

        if f_name != "all":
            where = {
                'created_at_iso': {
                    '$gte': today,
                    '$lt': next_day
                },
                f_name : 1
            }
        else:
            where = {
                'created_at_iso': {
                    '$gte': today,
                    '$lt': next_day
                },
                "icho" : 1,
                "kaede" : 1,
                "others" : 1
            }

        month = str(date.month).zfill(2)
        day = str(date.day).zfill(2)

        col = db['2015-' + month]
        one_day_count = col.find(where).count()

        one_day = '\t'.join([month, day, str(one_day_count)])
        all_day_list.append(one_day)

    return all_day_list

def main():
    pname_list = ['hk', 'tk', 'is']
    flags = ['kaede', 'icho', 'others', 'all']

    for pname in pname_list:
        db = setup_mongo('2015_' + pname + '_twi')

        for flag in flags:
            path = result_dir + "daily_count_" + pname + "_" + flag + ".tsv"
            all_day_list = count_flag(db, flag)
            with open(path, 'w') as out:
                out.write('\n'.join(all_day_list))

main()
