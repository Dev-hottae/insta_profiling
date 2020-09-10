import pandas as pd
import numpy as np
from collections import Counter

class UserFiltering:
    def __init__(self, hashtags, N_category, df):
        self.hashtags = hashtags
        self.N_category = N_category
        self.df = df

    def del_tags(self, tags, hashtag):
        lst = []
        for tag in tags:
            if tag not in hashtag:
                lst.append(tag)
        return lst

    def del_freq(self, freq, hashtag):
        dic = {}
        for (w, i) in freq.items():
            if w not in hashtag:
                dic[w] = i
        return dic

    def del_hashtag(self, num_df, hashtag):
        df = self.df[num_df]
        tags = df.tags.apply(lambda x: self.del_tags(x, hashtag))
        freq = df.freq.apply(lambda x: self.del_freq(x, hashtag))
        df['tags'] = tags
        df['freq'] = freq
        return df

    # 1) 검색 해시태그 제거
    def delete_hashtag(self):
        df = [0 for i in range(self.N_category)]
        for i in range(self.N_category):
            df[i] = self.del_hashtag(i, self.hashtags[i])
        return df

    def filtering(self, N): # N: 각 직업을 대표하는 voca에서 상위 몇 개를 뽑아낼지
        df = self.delete_hashtag()

        # 2) unique tags의 빈도수
        freq_whole = [0 for i in range(self.N_category)]
        for i in range(self.N_category):
            tmp = []
            for t in df[i].tags:
                tmp.extend(t)
            freq_whole[i] = Counter(tmp)

        # 3) 단어의 등장 문서수가 직업군의 절반을 넘을 경우, 해당 단어를 제거한 새로운 voca dictionary 생성
        voca = [0 for i in range(self.N_category)]
        freq_other = [0 for i in range(self.N_category)]
        for i in range(self.N_category):
            voca[i] = {}
            freq_other[i] = {}

        for num in range(self.N_category):
            for (w, n) in freq_whole[num].items():
                w_freq = 1
                for i in range(self.N_category):
                    if i != num:
                        if w in freq_whole[i]:
                            w_freq += 1
                freq_other[num][w] = w_freq
                if w_freq <= self.N_category//2:
                    voca[num][w] = n
        
        voca_top = [0 for i in range(self.N_category)]
        for i in range(self.N_category):
            voca_top[i] = dict(Counter(voca[i]).most_common(N))

        # 4) negative dictionary 생성: 타 직업군을 대표하는 단어
        neg = [0 for i in range(self.N_category)]
        for i in range(self.N_category):
            neg[i] = Counter()

        for i in range(self.N_category):
            for j in range(self.N_category):
                if j != i:
                    neg[i] += Counter(voca_top[j])

        # 5) negative voca에 변형된 sigmoid 적용: neg voca에 많이 등장할수록 중요도를 낮춤
        for i in range(self.N_category):
            n_job = len(df[i])
            for j, tag in enumerate(self.hashtags):
                if j != i:
                    for t in tag:
                        neg[i][t] = n_job
        
        neg_sig = [0 for i in range(self.N_category)]
        for i in range(self.N_category):
            neg_sig[i] = {}

        for i in range(self.N_category):
            nega = neg[i]
            point = nega.most_common(N)[N//2][1] # sigmoid 변곡점: neg 상위 N개의 중위값에 해당하는 빈도수
            for (w, n) in nega.items():
                neg_sig[i][w] = 1 / (1 + np.exp(n) - point)

        # 6) scoring: score = 평균(해시태그 사용 빈도수 x tf-idf x neg_sig)
        for i in range(self.N_category):
            df[i]['score'] = 0

        tf_idf = [0 for i in range(self.N_category)]
        for i in range(self.N_category):
            tf_idf[i] = {}
            for (w, n) in freq_whole[i].items():
                tf = n
                idf = np.log( self.N_category / (1 + freq_other[i][w]) )
                tf_idf[i][w] = tf * idf
        
        def scoring(freq_row, num_df):
            score = 0
            N_tags = sum(freq_row.values())
            ti = tf_idf[num_df]

            for (w, n) in freq_row.items():
                tf_idf_score = ti[w]
                try:
                    nega = neg_sig[num_df][w]
                except:
                    nega = 1
                score += tf_idf_score * nega / N_tags
            
            return score

        for i in range(self.N_category-2): # 주부, 백수 제외
            df[i]['score'] = df[i]['freq'].apply(lambda x: scoring(x, i))

        return df, voca_top