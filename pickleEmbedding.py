import pickle
import numpy as np

word_embeddings = {}
EMBEDDING_DICT_PATH = 'E:/sgns.financial.char/sgns.financial.char'

with open(EMBEDDING_DICT_PATH, encoding='utf-8') as f:
    for line in f:
        # 把第一行的内容去掉
        if '467389 300\n' not in line:
            values = line.split()
            # 第一个元素是词语
            word = values[0]
            embedding = np.asarray(values[1:], dtype='float32')
            word_embeddings[word] = embedding
with open('word_embedding.dict', 'wb') as f:
    pickle.dump(word_embeddings, f)