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
def handler(url, config, count, currentIndex, type_handler):
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
                # 如果为空格则跳过
                if line.strip() == "":
                    continue
                result = re.findall("\"(.*?)\"", line)

                item[result[0]] = result[1]
                item[result[2]] = result[3]
                data.append(item)
                # 清空item
                item = {}

    # 使用json解析工具解析data
    # result = json.loads(data)
    list.append(data)
    # 存入数据库
    if config["count"] == len(list) or currentIndex == count - 1:
        insertSql = "insert into " + config["tableName"] + "("
        # 还是需要keys的因为keys
        index = 0
        for key in config["keys"]:
            if index == len(config["keys"]) - 1:
                insertSql += ("`" + key + "`) values")
            else:
                insertSql += ("`" + key + "`,")
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
                # 这都是值传递，问题来了，怎么搞，可以传对象啊，感觉好蠢
                insertSql = type_handler(index, aindex, insertSql, x, item)
                aindex += 1
            index += 1

        dbutils.insert(insertSql)
        list = []


def disease_handler(index, aindex, insertSql, x, item):
    container = ""

    def iterator(index, elem):
        nonlocal container
        container += re.sub("'", "\\'", elem.text)

    # 这里需要提取出来
    if aindex == 0:
        # item name中 可能有单引号
        html = pq(x["Item Name"])
        text = html("div").text()
        insertSql += ("'" + re.sub("'", "\\'", text) + "',")

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

        return insertSql


# index 为25长度的容器的遍历顺序， aindex为item的遍历顺序， x为item的字段， item为list的成员
# python 没有包装对象
def herb_handler(index, aindex, insertSql, x, item):
    container = ""

    def iterator(index, elem):
        nonlocal container
        if elem.text is not None:
            container += re.sub("'", "\\'", elem.text)

    # 并不需要aindex
    # python 中没有switch语句
    html = pq(x["ID"]).text()

    # 会按照解析的顺序往里插入
    if (html == "Components" or html == "Candidate Target Genes"
            or html == "Diseases Associated with This Herb" or html == "Formulas Containing This Herb"):
        if x["Item Name"] == "":
            insertSql += "'',"
            return insertSql
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
        return insertSql
    else:
        if x["Item Name"] == "":
            insertSql += "'',"
            return insertSql
        html = pq(x["Item Name"])
        text = html("div").text()
        if text is not None:
            insertSql += ("'" + re.sub("'", "\\'", text) + "',")
        else:
            insertSql += "'',"

        return insertSql

def formulas_handler(index, aindex, insertSql, x, item):
    container = ""

    def iterator(index, elem):
        nonlocal container
        if elem.text is not None:
            container += re.sub("'", "\\'", elem.text)

    # 并不需要aindex
    # python 中没有switch语句
    html = pq(x["ID"]).text()

    # 会按照解析的顺序往里插入
    if (html == "Herbs Contained in This Formula (Chinese)" or html == "Herbs Contained in This Formula (Chinese Pinyin)"
            or html == "Candidate Target Genes" or html == "Diseases Associated with This Formula"):
        if x["Item Name"] == "":
            insertSql += "'',"
            return insertSql
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
        return insertSql
    else:
        if x["Item Name"] == "":
            insertSql += "'',"
            return insertSql
        html = pq(x["Item Name"])
        text = html("div").text()
        if text is not None:
            insertSql += ("'" + re.sub("'", "\\'", text) + "',")
        else:
            insertSql += "'',"

        return insertSql

def target_handler(index, aindex, insertSql, x, item):
    container = ""

    def iterator(index, elem):
        nonlocal container
        if elem.text is not None:
            container += re.sub("'", "\\'", elem.text)

    # 并不需要aindex
    # python 中没有switch语句
    html = pq(x["ID"]).text()

    # 会按照解析的顺序往里插入
    if (
            html == "Herbs Contained in This Formula (Chinese)" or html == "Herbs Contained in This Formula (Chinese Pinyin)"
            or html == "Candidate Target Genes" or html == "Diseases Associated with This Formula"):
        if x["Item Name"] == "":
            insertSql += "'',"
            return insertSql
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
        return insertSql
    else:
        if x["Item Name"] == "":
            insertSql += "'',"
            return insertSql
        html = pq(x["Item Name"])
        text = html("div").text()
        if text is not None:
            insertSql += ("'" + re.sub("'", "\\'", text) + "',")
        else:
            insertSql += "'',"

        return insertSql


def ingredients_handler(index, aindex, insertSql, x, item):
    container = ""

    def iterator(index, elem):
        nonlocal container
        if elem.text is not None:
            container += re.sub("'", "\\'", elem.text)

    # 并不需要aindex
    # python 中没有switch语句
    html = pq(x["ID"]).text()

    # 会按照解析的顺序往里插入 ingredients 有些特殊
    if (html == "Formulas Containing This Ingredient" or html == "External Link to PubChem" or html == "External Link to ChEMBL"
            or html == "References" or html == "Herbs Containing This Ingredient" or html == "Diseases Associated with This Ingredient"
                or html == "Candidate Target Genes"):
        if x["Item Name"] == "":
            insertSql += "'',"
            return insertSql

        if x["Item Name"] == "N/A":
            insertSql += "N/A"
            return insertSql

        if x["Item Name"] == "This ingredient hao no candidate target genes with the prediction confidence index more than 0.80.":
            insertSql += "This ingredient hao no candidate target genes with the prediction confidence index more than 0.80."
            return insertSql
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
        return insertSql
    else:
        if x["Item Name"] == "":
            insertSql += "'',"
            return insertSql
        html = pq(x["Item Name"])
        text = html("div").text()
        if text is not None:
            insertSql += ("'" + re.sub("'", "\\'", text) + "',")
        else:
            insertSql += "'',"

        return insertSql

def iterator(index, elem):
    print(elem.text)


def main():
    excel_path = "C:\\Users\\Administrator\\Desktop\\中药库.xlsx"
    # 无法通用处理
    diseases_config = {
        "tableName": "diseases",
        "keys": ["disease_name", "disease_genes", "herbs_associated_with_this_disease",
                 "formulas_associated_with_this_disease"],
        "startPattern": "\s*data : \\[$",
        "endPattern": "\s*\\],$",
        "count": 25
    }

    herbs_config = {
        "tableName": "herbs",
        "keys": ["herb_name_in_chinese", "herb_name_in_pinyin", "herb_name_in_ladin", "type", "description_in_chinese",
                 "description_in_english", "habitat_in_chinese", "habitat_in_english", "collection_time", "appearance",
                 "specifications", "components", "property", "flavor", "meridian_tropism", "indications",
                 "candidate_target_genes", "database_cross_references", "diseases_associated_with_this_herb",
                 "formulas_containing_this_herb"],
        "startPattern": "\s*data : \\[$",
        "endPattern": "\s*\\],$",
        "count": 25
    }

    formulas_config = {
        "tableName": "formulas",
        "keys": ["formula_name_in_chinese", "formula_name_in_pinyin", "dosage_form", "herbs_contained_in_this_formula_(Chinese)",
                 "herbs_contained_in_this_formula_(Chinese Pinyin)", "administration", "type", "syndromes_in_chinese", "syndromes_in_english",
                 "indications_in_chinese", "indications_in_english", "candidate_target_genes", "diseases_associated_with_this_formula"],
        "startPattern": "\s*data : \\[$",
        "endPattern": "\s*\\],$",
        "count": 25
    }

    target_config = {
        "tableName": "target",
        "keys": [],
        "startPattern": "\s*data : \\[$",
        "endPattern": "\s*\\],$",
        "count": 25
    }

    ingredients_config = {
        "tableName": "ingredients",
        "keys": ["Ingredient Name in English", "2D-Structure", "Molecular Formula", "Molecular Weight", "ALogP", "LogD",
                 "Molecular Solubility", "Molecular Volume", "Molecular Surface Area", "Molecular Polar Surface Area",
                 "Num Rotatable Bonds", "Num H Acceptors", "Num H Donors", "ADMET Absorption Level", "ADMET BBB Level", "ADMET BBB",
                 "ADMET Solubility", "ADMET Solubility Level", "ADMET Hepatotoxicity", "ADMET Hepatotoxicity Probability",
                 "ADMET CYP2D6", "ADMET CYP2D6 Probability", "ADMET PPB Level", "Druglikeness Weight", "Druglikeness Grading",
                 "Candidate Target Genes", "Diseases Associated with This Ingredient", "CAS No.", "External Link to PubChem",
                 "External Link to ChEMBL", "References", "Herbs Containing This Ingredient", "Formulas Containing This Ingredient"],
        "startPattern": "\s*data : \\[$",
        "endPattern": "\s*\\],$",
        "count": 25
    }

    # excelutils.read_excel_by_col(excel_path, handler, diseases_config, )
    # excelutils.read_excel_by_col(excel_path, handler, herbs_config, herb_handler)
    # excelutils.read_excel_by_col(excel_path, handler, formulas_config, formulas_handler)
    # excelutils.read_excel_by_col(excel_path, handler, target_config, target_handler)
    excelutils.read_excel_by_col(excel_path, handler, ingredients_config, ingredients_handler)


main()
# handler("http://www.baidu.com", "")
# html = pq("<div style='max-height: 200px;overflow: auto'><a href='/ETCM/index.php/Home/Index/yc_details?ywname=MAI DONG' class='tdcolor' target='_blank'>MAI DONG</a><a href='/ETCM/index.php/Home/Index/yc_details?ywname=CHAI HU' class='tdcolor' target='_blank'>; CHAI HU</a></div>")
# html("a").each(iterator)
# print(re.findall("\"(.+?)\"", "\"ID\": \"Disease Name\""))
