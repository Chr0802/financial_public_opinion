from pyhanlp import *
import re

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

if __name__ == "__main__":
    ABS_PATH_list = ['./news/news{}.txt.abstract.txt'.format(i+1) for i in range(10)]
    for path in ABS_PATH_list:
        abs, names, places, orgs = [], [], [], []
        with open(path) as f:
            for line in f.readlines():
                if not re.match(r'\A第\d+条摘要：\Z',line.strip()):
                    abs.append(line.strip())
        names, places, orgs = namedEntityRecognition(abs)
        res = '人名：' + '、'.join(names) + '。\n' + \
            '地名：' + '、'.join(places) + '。\n' + \
            '机构名：' + '、'.join(orgs) + '。\n'
        with open(path.split('.txt')[0]+'.txt.namedEntities.txt', 'w') as f:
            f.write(res)

