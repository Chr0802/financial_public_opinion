import pickle
import sys
from pathlib import Path

import numpy as np

BASE_DIR = Path(__file__).resolve().parent
# 预训练字向量文件，默认放在仓库根目录；也可以在命令行用参数指定：
#   python pickleEmbedding.py /path/to/sgns.financial.char
EMBEDDING_SRC_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else BASE_DIR / 'sgns.financial.char'
EMBEDDING_DICT_PATH = BASE_DIR / 'word_embedding.dict'


def main():
    if not EMBEDDING_SRC_PATH.exists():
        sys.exit('未找到字向量文件：{}\n'
                 '请从 https://github.com/Embedding/Chinese-Word-Vectors 下载 sgns.financial.char，'
                 '放到上述路径，或用 python pickleEmbedding.py <字向量文件路径> 指定。'.format(EMBEDDING_SRC_PATH))

    word_embeddings = {}
    with open(EMBEDDING_SRC_PATH, encoding='utf-8-sig') as f:
        head = f.readline().split()
        # 第一行通常是“词表大小 向量维度”的说明行；如果不是，就把它当普通词向量行处理
        if not (len(head) == 2 and head[0].isdigit() and head[1].isdigit()):
            f.seek(0)
        for line in f:
            values = line.split()
            if len(values) < 2:
                continue
            # 第一个元素是词语
            word = values[0]
            embedding = np.asarray(values[1:], dtype='float32')
            word_embeddings[word] = embedding

    with open(EMBEDDING_DICT_PATH, 'wb') as f:
        pickle.dump(word_embeddings, f)
    print('已生成 {}，共 {} 个词向量。'.format(EMBEDDING_DICT_PATH, len(word_embeddings)))


if __name__ == '__main__':
    main()
