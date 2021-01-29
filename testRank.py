import numpy as np
import pandas as pd
import networkx as nx
import jieba
from sklearn.metrics.pairwise import cosine_similarity
import time
import pickle
import re,os
from itertools import chain

# 按篇章读取新闻
def readNews(path):
    sentences_list = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            if line.strip():
                # 把元素按照[。！；？]进行分隔，得到句子。
                line_split = re.split(r'[。！；？]', line.strip())
                # [。！；？]这些符号也会划分出来，把它们去掉。
                line_split = [line.strip() for line in line_split if
                              line.strip() not in ['。', '！', '？', '；'] and len(line.strip()) > 1]
                sentences_list.append(line_split)
    return list(chain.from_iterable(sentences_list))

# 按句子进行分词
def seg_depart(sentence, stopwords):
    # 去掉非汉字字符
    sentence = re.sub(r'[^\u4e00-\u9fa5]+','',sentence)
    sentence_depart = jieba.cut(sentence.strip())
    word_list = []
    for word in sentence_depart:
        if word not in stopwords:
            word_list.append(word)
    # 如果句子整个被过滤掉了，如：'02-2717:56'被过滤，那就返回[],保持句子的数量不变
    return word_list

# 生成文章的句向量
def sentenceEmbedding(sentence_word_list, embedding_dict):
    sentence_vectors = []
    for i in sentence_word_list:
        if len(i) != 0:
            # 如果句子中的词语不在字典中，那就把embedding设为300维元素为0的向量。
            # 得到句子中全部词的词向量后，求平均值，得到句子的向量表示
            v = sum([embedding_dict.get(w, np.zeros((300,))) for w in i]) / (len(i))
        else:
            # 如果句子为[]，那么就向量表示为300维元素为0个向量。
            v = np.zeros((300,))
        sentence_vectors.append(v)
    return sentence_vectors

def computeTextRankScores(sentence_vectors):
    mat_size = len(sentence_vectors)
    # 计算句子之间的余弦相似度，构成相似度矩阵
    sim_mat = np.zeros([mat_size, mat_size])
    for i in range(mat_size):
        for j in range(mat_size):
            if i != j:
                sim_mat[i][j] = cosine_similarity(sentence_vectors[i].reshape(1, 300), sentence_vectors[j].reshape(1, 300))[0, 0]

    # 迭代得到句子的textrank值，排序并取出摘要. 利用句子相似度矩阵构建图结构，句子为节点，句子相似度为转移概率
    nx_graph = nx.from_numpy_array(sim_mat)
    # 得到所有句子的textrank值
    scores = nx.pagerank(nx_graph)
    return scores

def generateAbstract(file_path_list, stopwords_path, embedding_dict_path):

    # 创建停用词列表
    print('正在加载停用词列表......',end='')
    stopwords = [line.strip() for line in open(stopwords_path, encoding='utf8').readlines()]
    print('\r停用词列表加载完毕！')

    # 加载词向量embedding_dict
    print('正在加载词嵌入向量......', end='')
    with open(embedding_dict_path,'rb') as f:
        word_embeddings = pickle.load(f)
    print('\r词嵌入向量加载完毕！')

    # 逐篇生成摘要并保存
    for index, file in enumerate(file_path_list):
        print('正在处理第{0}文章{1}......'.format(index+1, file), end='')
        sentence_list = readNews(file)
        sentence_words_list = map(lambda x:seg_depart(x,stopwords), sentence_list)
        sentence_vectors = sentenceEmbedding(sentence_words_list, word_embeddings)
        tk_scores = computeTextRankScores(sentence_vectors)
        ranked_sentences = sorted(((tk_scores[i],s) for i,s in enumerate(sentence_list)), reverse=True)
        with open('{}.abstract.txt'.format(file), 'w') as f:
            for i in range(10):
                f.write('第{0}条摘要：\n{1}\n'.format(i+1, ranked_sentences[i][1]))
        print('\r文章{}摘要已生成！'.format(file))





if __name__ == '__main__':

    FILE_PATH_list = ['./news/news{}.txt'.format(i+1) for i in range(10)]
    STOPWORDS_PATH = 'E:/textRank/stopwords/cn_stopwords.txt'
    EMBEDDING_DICT_PATH = './word_embedding.dict'

    generateAbstract(FILE_PATH_list, STOPWORDS_PATH, EMBEDDING_DICT_PATH)