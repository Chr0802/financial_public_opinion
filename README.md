# financial_public_opinion

中文财经新闻的**抽取式摘要 + 命名实体识别**小项目。用 TextRank 从每篇新闻中挑出最重要的句子生成摘要，再用 HanLP 从摘要中提取人名、地名和机构名。

## 处理流程

```
news/newsN.txt
   │  testRank.py   —— 句子向量 + TextRank
   ▼
news/newsN.txt.abstract.txt          （每篇 top-10 句摘要）
   │  NER.py        —— HanLP 命名实体识别
   ▼
news/newsN.txt.namedEntities.txt     （人名 / 地名 / 机构名）
```

## 目录结构

```
.
├── testRank.py             # 摘要生成：切句 → 分词 → 句向量 → 相似度图 → PageRank
├── NER.py                  # 对摘要做命名实体识别
├── pickleEmbedding.py      # 把预训练字向量文件转成 word_embedding.dict
├── news/                   # 新闻原文及生成的摘要、实体结果
├── stopwords/              # 中文停用词表（默认使用 cn_stopwords.txt）
└── .gitignore              # 忽略词向量等大文件
```

## 环境依赖

- Python 3
- numpy、scikit-learn、networkx、jieba、pyhanlp

```bash
pip install numpy scikit-learn networkx jieba pyhanlp
```

`pyhanlp` 需要本机安装 Java，首次运行会自动下载 HanLP 数据包。

## 使用方法

所有命令都在仓库根目录执行。

### 1. 准备词向量

下载预训练的中文字向量 [Chinese-Word-Vectors](https://github.com/Embedding/Chinese-Word-Vectors) 中的 `sgns.financial.char`（金融领域字向量，约 46 万词 × 300 维），放到仓库根目录：

```bash
python pickleEmbedding.py                    # 默认读取 ./sgns.financial.char
python pickleEmbedding.py /path/to/sgns.financial.char   # 或手动指定路径
```

成功后生成 `word_embedding.dict`（已加入 `.gitignore`）。

> 项目把句向量维度固定为 300，需要使用 300 维的字向量文件。

### 2. 放入新闻原文

把新闻保存为 `news/newsN.txt`（N 为数字，UTF-8 编码，带 BOM 也可）。脚本会自动扫描匹配 `news\d+\.txt` 的文件，按序号处理。

每篇新闻建议至少有 10 个句子，否则摘要不足 10 条会报错。

### 3. 生成摘要

```bash
python testRank.py
```

输出 `news/newsN.txt.abstract.txt`，包含按 TextRank 分数排序的前 10 句（不是原文顺序）。

摘要生成过程：

1. 按 `。！；？` 把新闻切成句子；
2. jieba 分词，去掉停用词和非汉字字符；
3. 句子中每个词的词向量取平均，得到 300 维句向量（未登录词按零向量处理）；
4. 以句子为节点、句间余弦相似度为边权构建图，用 PageRank 计算句子权重。

### 4. 提取实体

```bash
python NER.py
```

输出 `news/newsN.txt.namedEntities.txt`，格式为：

```
人名：…
地名：…
机构名：…
```

识别结果按 HanLP 词性标注分类：`nr/nrf/nrj` → 人名，`ns` → 地名，`nt` → 机构名。

## 说明

- 所有输入输出均使用 UTF-8 编码。
- `word_embedding.dict` 和 `sgns.financial.char` 体积较大，不纳入版本库。
- 摘要和实体识别结果（`news/*.abstract.txt`、`news/*.namedEntities.txt`）已随仓库提交，可直接查看。
