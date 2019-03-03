import urllib.request as request
import re
import json
import excelutils
import dbutils
from pyquery import PyQuery as pq
# print('hello world')

list = []
prefix = "http://www.nrc.ac.cn:9090"
# handler 是不一样的，存的数据库也是不一样的
def handler(url, config):
    global list
    url = prefix + url
    html = request.urlopen(url).read().decode("utf-8")
    lines = html.split("\r\n")
    find = False
    data = []
    item = {}
    # 解析对应匹配的行数
    for line in lines:
        # re是python官方自带的模块
        if not find:
            result = re.match(config['startPattern'], line)
            if result:
                find = True
        else:
            result = re.match(config['endPattern'], line)
            if result:
                break
            else:
                # 提取出双引号之间的数据
                result = re.findall("\"(.+?)\"", line)
                item[result[0]] = result[1]
                item[result[2]] = result[3]
                data.append(item)
                # 清空item
                item = {}

    # 使用json解析工具解析data
    # result = json.loads(data)
    list.append(data)
    # 存入数据库
    if config["count"] == len(list):
        insertSql = "insert into " + config["tableName"] + "("
        # 还是需要keys的因为keys
        index = 0
        for key in config["keys"]:
            if index == len(config["keys"]) - 1:
                insertSql += (key + ") values")
            else:
                insertSql += (key + ",")
            index += 1

        index = 0
        for item in list:
            # item 为一个字符串，需要转为数组
            # 这并不是json，只是普通的js对象, 需要处理，怎么处理呢用正则匹配吧
            # a = [
            #     {"ID": "Disease Name","Item Name": "<div style='max-height: 200px;overflow: auto'>Abdominal Colic</div>", },
            # ]
            insertSql += "("
            aindex = 0
            for x in item:
                container = ""
                def iterator(index, elem):
                    nonlocal container
                    container += elem.text

                if aindex == 0:
                    html = pq(x["Item Name"])
                    text = html("div").text()
                    insertSql += ("'" + text + "',")

                    aindex += 1
                else:
                    # 从第三个开始格式不一样了
                    html = x["Item Name"]
                    div = pq(html)
                    a_tags = div("a")
                    a_tags.each(iterator)
                    if aindex == len(item) - 1:
                        if index == len(list) - 1:
                            insertSql += ("'" + container + "');")
                        else:
                            insertSql += ("'" + container + "'),")
                    else:
                        insertSql += ("'" + container + "',")

                    aindex += 1
                    container = ""
            index += 1

        dbutils.insert(insertSql)
        list = []


def iterator(index, elem):
    print(elem.text)


def main():
    excel_path = "C:\\Users\\12494\\Desktop\\diseases.xlsx"
    # 无法通用处理
    herbs_config = {
        "tableName": "herbs",
        "keys": ["disease_name", "disease_genes", "herbs_associated_with_this_disease", "formulas_associated_with_this_disease"],
        "startPattern": "\s*data : \\[$",
        "endPattern": "\s*\\],$",
        "count": 50
    }
    excelutils.read_excel_by_col(excel_path, handler, herbs_config)
    # excelutils.read_excel_by_col(excel_path, handler)
    # excelutils.read_excel_by_col(excel_path, handler)
    # excelutils.read_excel_by_col(excel_path, handler)
    # excelutils.read_excel_by_col(excel_path, handler)


main()
# handler("http://www.baidu.com", "")
# html = pq("<div style='max-height: 200px;overflow: auto'><a href='/ETCM/index.php/Home/Index/yc_details?ywname=MAI DONG' class='tdcolor' target='_blank'>MAI DONG</a><a href='/ETCM/index.php/Home/Index/yc_details?ywname=CHAI HU' class='tdcolor' target='_blank'>; CHAI HU</a></div>")
# html("a").each(iterator)
# print(re.findall("\"(.+?)\"", "\"ID\": \"Disease Name\""))
