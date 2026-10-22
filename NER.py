from pyhanlp import *
import re, sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
NEWS_DIR = BASE_DIR / 'news'

# document = "水利部水资源司司长陈明忠9月29日在国务院新闻办举行的新闻发布会上透露，" \
#            "根据刚刚完成了水资源管理制度的考核，有部分省接近了红线的指标，" \
#            "有部分省超过红线的指标。对一些超过红线的地方，陈明忠表示，对一些取用水项目进行区域的限批，" \
#            "严格地进行水资源论证和取水许可的批准。"
# print(HanLP.extractKeyword(document, 2))
# # 自动摘要
# print(HanLP.extractSummary(document, 3))
# # 依存句法分析
# print(HanLP.parseDependency("徐先生还具体帮助他确定了把画雄鹰、松鼠和麻雀作为主攻目标。"))

def namedEntityRecognition(sentences):
    segment = HanLP.newSegment().enableNameRecognize(True).enablePlaceRecognize(True).enableOrganizationRecognize(True)
    name_list, place_list, org_list = [], [], []
    for sentence in sentences:
        term_list = segment.seg(sentence)
        for term in term_list:
            nature, word = str(term.nature), term.word
            if nature in ['nr', 'nrf', 'nrj']:
                name_list.append(word)
            elif nature == 'ns':
                place_list.append(word)
            elif nature == 'nt':
                org_list.append(word)
    return set(name_list), set(place_list), set(org_list)

def listAbstractFiles(news_dir):
    # 只匹配 testRank.py 生成的 news1.txt.abstract.txt 这类文件，并按序号排序
    pattern = re.compile(r'news(\d+)\.txt\.abstract\.txt')
    files = []
    for path in Path(news_dir).iterdir():
        m = pattern.fullmatch(path.name)
        if m:
            files.append((int(m.group(1)), path))
    return [path for _, path in sorted(files)]

if __name__ == "__main__":
    ABS_PATH_list = listAbstractFiles(NEWS_DIR)
    if not ABS_PATH_list:
        sys.exit('未找到摘要文件（{}/*.abstract.txt），请先运行 testRank.py 生成摘要。'.format(NEWS_DIR))
    for path in ABS_PATH_list:
        abstract = []
        with open(path, encoding='utf-8') as f:
            for line in f.readlines():
                if not re.match(r'\A第\d+条摘要：\Z',line.strip()):
                    abstract.append(line.strip())
        names, places, orgs = namedEntityRecognition(abstract)
        res = '人名：' + '、'.join(sorted(names)) + '。\n' + \
            '地名：' + '、'.join(sorted(places)) + '。\n' + \
            '机构名：' + '、'.join(sorted(orgs)) + '。\n'
        out_path = path.with_name(path.name.replace('.txt.abstract.txt', '.txt.namedEntities.txt'))
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(res)
