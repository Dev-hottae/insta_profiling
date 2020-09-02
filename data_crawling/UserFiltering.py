import pandas as pd
import numpy as np
from collections import Counter

# 각 직업별 검색 해시태그(여러 개 가능) 및 직업 카테고리 수
hashtags = [["군인"], ["교사"], ["중2"]]
N_category = 3

# 예제 데이터
path = 'C:/Users/bogyung/Downloads/crawling/test/'
df0 = pd.read_json(path + 'tags_goonin.json')
df1 = pd.read_json(path + 'tags_gyosa.json')
df2 = pd.read_json(path + 'tags_joong2.json')

def del_tags(tags, hashtag):
    lst = []
    for tag in tags:
        if tag not in hashtag:
            lst.append(tag)
    return lst

def del_freq(freq, hashtag):
    dic = {}
    for (w, i) in freq.items():
        if w not in hashtag:
            dic[w] = i
    return dic

def del_hashtag(num_df, hashtag):
    df = globals()['df{}'.format(num_df)]
    tags = df.tags.apply(lambda x: del_tags(x, hashtag))
    freq = df.freq.apply(lambda x: del_freq(x, hashtag))
    df['tags'] = tags
    df['freq'] = freq
    return df

def UserFiltering(N_category, N): # N: 각 직업을 대표하는 voca에서 상위 몇 개를 뽑아낼지
    
    # 1) 검색 해시태그 제거
    for i in range(N_category):
        globals()['df{}'.format(i)] = del_hashtag(i, hashtags[i])

    # 2) unique tags의 빈도수
    for i in range(N_category):
        tmp = []
        for t in globals()['df{}'.format(i)].tags:
            tmp.extend(t)
        globals()['freq_whole{}'.format(i)] = Counter(tmp)

    # 3) 단어의 등장 문서수가 직업군의 절반을 넘을 경우, 해당 단어를 제거한 새로운 voca dictionary 생성
    for i in range(N_category):
        globals()['voca{}'.format(i)] = {}
        globals()['freq_other{}'.format(i)] = {}

    for num in range(N_category):
        for (w, n) in globals()['freq_whole{}'.format(num)].items():
            w_freq = 1
            for i in range(N_category):
                if i != num:
                    if w in globals()['freq_whole{}'.format(i)]:
                        w_freq += 1
            globals()['freq_other{}'.format(num)][w] = w_freq
            if w_freq <= N_category//2:
                globals()['voca{}'.format(num)][w] = n
            
    for i in range(N_category):
        globals()['voca{}_top'.format(i)] = dict(Counter(globals()['voca{}'.format(i)]).most_common(N))

    # 4) negative dictionary 생성: 타 직업군을 대표하는 단어
    for i in range(N_category):
        globals()['neg{}'.format(i)] = Counter()

    for i in range(N_category):
        for j in range(N_category):
            if j != i:
                globals()['neg{}'.format(i)] += Counter(globals()['voca{}_top'.format(j)])

    # 5) negative voca에 변형된 sigmoid 적용: neg voca에 많이 등장할수록 중요도를 낮춤
    for i in range(N_category):
        n_job = len(globals()[f'df{i}'])
        for j, tag in enumerate(hashtags):
            if j != i:
                for t in tag:
                    globals()[f'neg{i}'][t] = n_job

    for i in range(N_category):
        globals()['neg{}_sig'.format(i)] = {}

    for i in range(N_category):
        neg = globals()['neg{}'.format(i)]
        point = neg.most_common(N)[N//2][1] # sigmoid 변곡점: neg 상위 N개의 중위값에 해당하는 빈도수
        for (w, n) in neg.items():
            globals()['neg{}_sig'.format(i)][w] = 1 / (1 + np.exp(n) - point)

    # 6) scoring: score = 평균(해시태그 사용 빈도수 x tf-idf x neg_sig)
    for i in range(N_category):
        globals()['df{}'.format(i)]['score'] = 0

    for i in range(N_category):
        globals()['tf_idf{}'.format(i)] = {}
        for (w, n) in globals()['freq_whole{}'.format(i)].items():
            tf = n
            idf = np.log( N_category / (1 + globals()['freq_other{}'.format(i)][w]) )
            globals()['tf_idf{}'.format(i)][w] = tf * idf
    
    def scoring(freq_row, num_df):
        score = 0
        N_tags = sum(freq_row.values())
        ti = globals()[f'tf_idf{num_df}']

        for (w, n) in freq_row.items():
            tf_idf = ti[w]
            try:
                neg = globals()['neg{}_sig'.format(num_df)][w]
            except:
                neg = 1
            score += tf_idf * neg / N_tags
        
        return score

    for i in range(N_category-2): # 주부, 백수 제외
        globals()['df{}'.format(i)]['score'] = globals()['df{}'.format(i)]['freq'].apply(lambda x: scoring(x, i))

    return df0, df1, df2 # N_category 수 만큼 지정

df0, df1, df2 = UserFiltering(N_category = 3, N = 10)