"""
教師データ(2014)のツイート内に含まれる各単語のsoaとpmiを求め関連語を出力する。
2つの品詞を使う
"""

import os
from s_lib import setup_mongo
import sys, math, collections
from tqdm import tqdm

def calc_pmi(sw, w, s, N):
  pmi = math.log2(((sw + 1) * N) / (w * s))
  return(pmi)

def calc_soa(sw, ns_w, w, s, ns, N):
    #  soa = math.log2(((sw + 1) * ns)/((ns_w + 1) * s))
    soa = calc_pmi(sw, w, s, N) - calc_pmi(ns_w, w, ns, N)
    return(soa)

def main():
    db = setup_mongo('2014_sakura_twi_1208')
    pname = 'hk'
    col = db['season_' + pname]
    s_twis = list(col.find({'sakura_twi': 1}))
    ns_twis = list(col.find({'sakura_twi': 0}))


    swords = []
    n_and_s_words = {}
    for s_twi in s_twis:
        swords.extend(s_twi['morpho_text'].split(' '))
    uniq_swords = list(set(swords))
    for ns_twi in ns_twis:
        morpho = ns_twi['morpho_text'].split(' ')
        for w in uniq_swords:
            if w in morpho:
                n_and_s_words[w] = n_and_s_words[w] + 1 if w in n_and_s_words else 1

    swords_count = collections.Counter(swords) # season_wordの出現回数のカウントをした。
    len_stwins = len(s_twis)
    len_nstwins = len(ns_twis)
    N = s + ns

    pmi_of_word = {}
    for sword, count in swords_count.items():
        if sword in keywords[flag]: #対象語のpmiの計算を飛ばす
            continue
        count_in_stwis = count
        count_in_nstwis = n_and_s_words[swordw] if word in n_and_s_words else 0
        count_in_all = count_in_stwis + count_in_nstwis
        if not any([count_in_all < 1, len_stwins < 1]):
            pmi_of_word[word] = calc_pmi(count_in_stwis, count_in_all, len_stwins, N)

    sorted_pmi = sorted(pmi_of_word.items(), key=lambda x:(x[1], x[0]), reverse=True)


    result_dir = '/now24/naruse/'

    os.makedirs(result_dir + 'pmi/', exist_ok=True)
    with open(result_dir + 'pmi/' + 'test_pmi.txt', 'w') as f:
        for w, pmi in sorted_pmi:
            f.write(f'{w}, {pmi}\n')

main()
