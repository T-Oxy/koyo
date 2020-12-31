"""
教師データのツイート内に含まれる各単語と
'桜'の関連度を計算する
"""

from s_lib import setup_mongo
import sys, math, collections


def calc_pmi(sw, w, s, N):
  pmi = math.log2(((sw + 1) * N) / (w * s))
  return(pmi)


def calc_soa(sw, ns_w, w, s, ns, N):
    #  soa = math.log2(((sw + 1) * ns)/((ns_w + 1) * s))
    soa = calc_pmi(sw, w, s, N) - calc_pmi(ns_w, w, ns, N)
    return(soa)


def main():
    args = sys.argv

    db = setup_mongo('2014_sakura_twi_1208')
    pname = 'hk'

    col = db['season_' + pname]
    s_twis = list(col.find({'sakura_twi': 1}))
    ns_twis = list(col.find({'sakura_twi': 0}))

    """
    s_twins: 旬ツイート
    ns_twins: 非旬ツイート
    """

    words = []
    ns_words = {} # 辞書
    for s_twi in s_twis:
        words.extend(s_twi['morpho_text'].split(' '))
    uwords = list(set(words))
    for ns_twi in ns_twis:
        morpho = ns_twi['morpho_text'].split(' ')
        for w in uwords:
            if w in morpho:
                ns_words[w] = ns_words[w] + 1 if w in ns_words else 1

    """
    words: 旬ツイートに含まれていた語。重複あり
    uwords: 旬ツイートに含まれていた語。重複なし
    ns_words: 非旬ツイートに含まれていた語がkeyでその出現数がvalue
    """

    sw_count = collections.Counter(words)
    s = len(s_twis)
    ns = len(ns_twis)
    N = s + ns

    """
    sw_count: 旬ツイートの語がkeyで、出現回数がvalue
    s: 旬ツイートの数
    ns: 非旬ツイートの数
    N: ツイート総数
    """

    pmi_of_word = {}
    for w, c in sw_count.items():
        if w in ['桜', 'さくら', 'サクラ']:
            continue
        sw = c
        ns_w = ns_words[w] if w in ns_words else 0
        wc = sw + ns_w
        if not any([wc < 1, s < 1]): # ある語が1以上かつ旬ツイートが1以上(分母になるので0ダメ)
            pmi_of_word[w] = calc_pmi(sw, wc, s, N)
    sorted_pmi = sorted(pmi_of_word.items(), key=lambda x:x[1], reverse=True)

    """
    sw: ある語の旬ツイートでの出現回数。※対象語の場合は処理しない
    ns_w: ある語が非旬ツイートでの出現回数。※対象語の場合は処理しない
    wc: ある語の全ツイートでの出現回数。
    sorted_pmi: keyが語、valueがそのpmiの辞書。pmiが大きい順
    """

    with open('/now24/a.saito/tmp/' + pname + '_pmi.txt', 'w') as f:
        for w, pmi in sorted_pmi:
            f.write(f'{w}, {pmi}\n')

    soa_of_word = {}
    for w, c in sw_count.items():
        if w in ['桜', 'さくら', 'サクラ']:
            continue
        sw = c
        ns_w = ns_words[w] if w in ns_words else 0
        wc = sw + ns_w
        if not s < 1:
            soa_of_word[w] = calc_soa(sw, ns_w, wc, s, ns, N)
    sorted_soa = sorted(soa_of_word.items(), key=lambda x:x[1], reverse=True)
    with open('/now24/a.saito/tmp/' + pname + '_soa.txt', 'w') as f:
        for w, soa in sorted_soa:
            f.write(f'{w}, {soa}\n')


main()
