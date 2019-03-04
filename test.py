import re
import dbutils
import urllib.request as request

# print(re.match("\s*data : \\[$", "                                        data : ["))
#
# print(re.sub("'", "\\'", "lalala'wqs"))
#
# dbutils.insert("insert into test (name) values ('lalala')")
#
# print("    ".strip() == "")
#
# print(re.match('\"(.+?)\"', '{\"ID\":\"<div id=\'L7717\' >Indications</div>\",\"Item Name\":\"123\"},'))
#
# re.sub("'", "\\'", None)
url = "http://www.nrc.ac.cn:9090/ETCM/index.php/Home/Index/jyjb_details.html?id=1"

html = request.urlopen(url).read().decode("utf-8")

print(html)