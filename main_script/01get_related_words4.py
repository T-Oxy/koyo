"""
教師データ(2014)のツイート内に含まれる各単語のsoaとpmiを求め関連語を出力する。
4つの品詞を使う
"""
import time
import os
from s_lib import setup_mongo
import sys, math, collections
from tqdm import tqdm
import datetime as dt
from datetime import timedelta
import pandas as pd

sakura = ['桜', 'さくら', 'サクラ']
icho = ["いちょう", "イチョウ", "銀杏"]
kaede = ["かえで", "カエデ", "楓"]
sonota = ["こうよう", "もみじ", "紅葉", "黄葉", "コウヨウ", "モミジ"]
koyo = icho + kaede + sonota

# 分割にも対応するために、開始日と終了日ではなく、正解日(datetime型)すべてを入れておく。
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

keywords = {
    "sakura": sakura,
    "icho": icho,
    "kaede": kaede,
    "sonota": sonota,
    "koyo": icho+kaede+sonota,
}

def calc_pmi(sw, w, s, N):
  pmi = math.log2(((sw + 1) * N) / (w * s))
  return(pmi)

def calc_soa(sw, ns_w, w, s, ns, N):
    #  soa = math.log2(((sw + 1) * ns)/((ns_w + 1) * s))
    soa = calc_pmi(sw, w, s, N) - calc_pmi(ns_w, w, ns, N)
    return(soa)

def main():
    prefs = ["tk"] # , "hk", "is"
    flags = ["koyo"] # "icho", "kaede", "sonota",

    # db = setup_mongo('2014_koyo_twi')
    db = setup_mongo('2014_twi_naruse')

    for flag in tqdm(flags, desc="flag"):
        if flag == "koyo":
            season_pipe = {'$or': [ {'icho': 1}, {'kaede': 1}, {'sonota': 1} ]}
            unseason_pipe = { '$and': [ {'icho': 0}, {'kaede': 0}, {'sonota': 0} ]}
        else:
            season_pipe = {flag: 1}
            unseason_pipe = {flag: 0}

        for pref in tqdm(prefs, desc="pref"):
            s_twis = []  # 旬ツイートのリスト
            ns_twis = []  # 非旬ツイートのリスト
            swords = []
            n_and_s_words = {}
            col = db[pref]

            for date in tqdm(correct_dates[pref][flag], desc="dates"):
                today = date.isoformat()
                next_day = (date + dt.timedelta(days=1)).isoformat()

                season_pipe['created_at_iso'] = {
                    '$gte': today,
                    '$lt': next_day
                }
                unseason_pipe['created_at_iso'] = {
                    '$gte': today,
                    '$lt': next_day
                }
                s_twis.extend(list(col.find(season_pipe)))
                ns_twis.extend(list(col.find(unseason_pipe)))

                # print(f"\n旬ツイート: {len(s_twis)}")
                # print(f"非旬ツイート: {len(ns_twis)}")

            print(f"\n総旬ツイート: {len(s_twis)}")
            print(f"\n総非旬ツイート: {len(ns_twis)}")

            for s_twi in s_twis:
                swords.extend(s_twi['morphos_4class'].split(' '))

            start = time.time()
            uniq_swords = list(set(swords))
            for ns_twi in tqdm(ns_twis, desc="ns_twis"):
                morpho = ns_twi['morphos_4class'].split(' ')
                for w in uniq_swords:
                    if w in morpho:
                        n_and_s_words[w] = n_and_s_words[w] + 1 if w in n_and_s_words else 1
            # swords(旧:words): 旬ツイートに含まれていた語のリスト。重複あり
            # uniq_swords(旧:uwords): 旬ツイートに含まれていた語のリスト。重複なし
            # n_and_s_words(旧:ns_words): 非旬ツイート && 旬ツイートに含まれている語がkeyでその出現数がvalue
            elapsed_time = time.time() - start
            print (f"{pref}, {flag}")
            print (f"elapsed_time: {elapsed_time}[sec]")

            swords_count = collections.Counter(swords) # season_wordの出現回数のカウントをした。
            N = len(s_twis) + len(ns_twis)
            # swords_count(旧:sw_count): 旬ツイートの語がkeyで、出現回数がvalue
            # len(s_twis)(旧:s): 旬ツイートの数
            # len(ns_twis)(旧:ns): 非旬ツイートの数
            # N: ツイート総数

            print("03")
            pmi_of_word = {}
            for sword, count in swords_count.items():
                if sword in keywords[flag]: #対象語のpmiの計算を飛ばす
                    continue
                count_in_stwis = count
                count_in_nstwis = n_and_s_words[sword] if sword in n_and_s_words else 0
                count_in_all = count_in_stwis + count_in_nstwis
                if not any([count_in_all < 1, len(s_twis) < 1]):
                    pmi_of_word[sword] = calc_pmi(count_in_stwis, count_in_all, len(s_twis), N)

            sorted_pmi = sorted(pmi_of_word.items(), key=lambda x:x[1], reverse=True)

            # count_in_stwis(旧:sw): 関連語の旬ツイートでの出現回数。
            # count_in_nstwis(旧:ns_w): 関連語の非旬ツイートでの出現回数。
            # count_in_all(旧:wc): 関連語の全ツイートでの出現回数。
            # sorted_pmi: keyが関連語、valueがそのpmiの辞書。pmiが大きい順

            soa_of_word = {}
            for sword, count in swords_count.items():
                if sword in keywords[flag]: #対象語のsoaの計算を飛ばす
                    continue
                count_in_stwis = count
                count_in_nstwis = n_and_s_words[sword] if sword in n_and_s_words else 0
                count_in_all = count_in_stwis + count_in_nstwis
                if not any([count_in_all < 1, len(s_twis) < 1, len(ns_twis) < 1]):
                    soa_of_word[sword] = calc_soa(count_in_stwis, count_in_nstwis, count_in_all, len(s_twis), len(ns_twis), N)

            sorted_soa = sorted(soa_of_word.items(), key=lambda x:x[1], reverse=True)

            result_dir = '/now24/naruse/koyo/result/related_words/'
            os.makedirs(result_dir, exist_ok=True)
            with open(result_dir + f'{flag}_{pref}_4pmi.txt', 'w') as f:
                for w, pmi in sorted_pmi:
                    f.write(f'{w}, {pmi}\n')
            os.makedirs(result_dir, exist_ok=True)
            with open(result_dir + f'{flag}_{pref}_4soa.txt', 'w') as f:
                for w, soa in sorted_soa:
                    f.write(f'{w}, {soa}\n')

            print(f"{result_dir} に出力しました。")

main()
