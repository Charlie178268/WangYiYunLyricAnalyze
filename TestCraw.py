#encoding=utf-8
import  requests
import json
from bs4 import BeautifulSoup
import re   #提供正则
import collections
import jieba #提供分词功能
#提供绘图
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
#提供绘图用字体
from matplotlib.font_manager import FontProperties

#解决编码问题
import sys
reload(sys)
sys.setdefaultencoding('utf8')

#实现从网易云音乐歌手信息页面抓取热门50首歌，然后获取这50首歌的歌词，统计出出现次数最多的词
#抓取网址可以用谷歌自带的抓包工具查看返回状态为200的网址


#网络爬虫先要找入口地址，从入口地址处抓取数据

#这个地址要口令登录，所以要破解口令，比较麻烦，所以采取下一种
#lyricUrl = 'http://music.163.com/weapi/song/lyric?csrf_token='

#此入口可以直接根据id获取歌词的json字符串
#注意python语句都要缩进
def downloadLyricBySongId(id):
    url = "http://music.163.com/api/song/lyric?"+'id='+str(id)+'&lv=1&kv=1&tv=-1'
    r = requests.get(url)
    # print (r.text)
    json_obj = r.text
    #采用json解析获取的字符串
    jsonText = json.loads(json_obj)
    lyc = jsonText['lrc']['lyric']
    #使用正则去掉时间信息
    pat = re.compile(r'\[.*\]')
    #使用pat规则把lyc里面符合规则的字符串替换为空
    lyc = re.sub(pat, "", lyc)
    lyc = lyc.strip()   #用于移除字符串头尾指定的字符，默认为空格
    return lyc

#从歌手信息的网页中获取热门50首单曲的id，分别获取其歌词，然后保存到记事本中，便于我们分析
def getAirtistSongsId(airtistId):
    url = 'http://music.163.com/artist?id='+str(airtistId)
    #提取其热门单曲Html
    r = requests.get(url).text
    #使用BeautifulSoup将信息格式化为lxml,注意使用api要安装BeautifulSoup4和lxml库
    #pip install beautifulsoup4
    #pip install lxml
    bs_obj = BeautifulSoup(r, 'lxml')
    t = bs_obj.find('textarea')
#    print (t)
    #正则，替换()为[],替换'为"
    musics = json.loads(t.text.replace('(', '[').replace(')', ']').replace('\'', '"'))
    #print (musics)
    ids = {}
    for music in musics:
        #print (music['name'])
        ids[music['name']] = music['id']
    return ids

# 使用结巴分词对文本进行分词
def cutWordByJieba(new_text):
    # 使用精确模式进行结巴分词，即分解出有意义的词语
    word_cut = jieba.cut(new_text, cut_all=False)
    word_list = list(word_cut)
    return word_list

# 获取停用词
def MakeWordsSet(words_file):
    words_set = set()
    with open(words_file, 'r') as fp:
        for line in fp.readlines():
            word = line.strip().decode("utf-8")
            if len(word) > 0 and word not in words_set:  # 去重
                words_set.add(word)
    return words_set

# 从训练集分词结果中去除停用词，选取特征词
def words_dict(all_words_list, stopwords_set=set()):
    feature_words = []
    n = 1
    for t in range(0, len(all_words_list), 1):
        if n > 2000:  # feature_words的维度
            break
        if not all_words_list[t].isdigit() and all_words_list[t] not in stopwords_set and 1 < len(
                all_words_list[t]) < 5:
            feature_words.append(all_words_list[t])
            n += 1
    return feature_words

#画饼状图
def drawPie(season_dict):
    font = FontProperties(fname=r"C:\\WINDOWS\\Fonts\\simsun.ttc", size=14)  # C:\WINDOWS\Fonts
    labels = ['Spring', 'Summer', 'Autumn', 'Winter']
    X = [0, 0, 0, 0]
    sum = 0
    for index in range(0, 4):
        sum += season_dict[index]
    for index in range(0, 4):
        X[index] = season_dict[index]*100/sum
        print X[index]
    fig = plt.figure()
    plt.pie(X, labels=labels, autopct='%1.2f%%')  # 画饼图（数据，数据对应的标签，百分数保留两位小数点）
    plt.title("季节分布图", fontproperties=font)
    plt.show()
    plt.savefig("PieChart.png")

    return

# 入口
if __name__ == '__main__':
    #id为5770是许巍的歌手信息
    ids = getAirtistSongsId(5770)
    #遍历打印所有歌词
    strAllLyric = ''
    for item in ids:
        lyric = downloadLyricBySongId( ids[item] )
        strAllLyric += lyric

    word_list = cutWordByJieba(strAllLyric)

    # 获取停用词
    stopwords_file = './stopwords_cn.txt'
    stopwords_set = MakeWordsSet(stopwords_file)
    feature_words = words_dict(word_list, stopwords_set)

    #for item in word_list:
    #    print item
    #统计词数
    all_words_dict = {}
    # 统计春夏秋冬出现频率
    season_dict = [0, 0, 0, 0]
    for word in feature_words:
        if all_words_dict.has_key(word):
            all_words_dict[word] += 1
        else:
            all_words_dict[word] = 1
        if word.encode('utf8') == "春天":
            season_dict[0]+=1
        elif word.encode('utf8') == '夏天':
            season_dict[1]+=1
        elif word.encode('utf8') == '秋天':
            season_dict[2]+=1
        elif word.encode('utf8') == '冬天':
            season_dict[3]+=1

    # key函数利用词频进行降序排序
    all_words_sort_list = sorted(all_words_dict.items(), key=lambda f: f[1], reverse=True)  # 内建函数sorted参数需为list
    #输出关键词和出现次数
    #for item in all_words_sort_list:
    #    print item[0]+"---"+str(item[1])
    #输出春夏秋冬
    print '春天---'+str(season_dict[0])
    print '夏天---'+str(season_dict[1])
    print '秋天---'+str(season_dict[2])
    print '冬天---'+str(season_dict[3])
    drawPie(season_dict)

#待实现的功能
#统计歌手最喜欢的季节
#最喜欢的城市
#情绪正负面
#做成统计图展示




