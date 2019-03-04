import xlrd
from pyquery import PyQuery as pq
import re


# handler 是通用处理，type_handler 是特殊处理
def read_excel_by_col(filepath, handler, config, type_handler):
    excelfile = xlrd.open_workbook(filepath)
    print(excelfile.sheet_names())

    sheet1 = excelfile.sheet_by_index(0)
    colscount = sheet1.ncols
    index_col = 0

    while index_col < colscount:
        colvalues = sheet1.col_values(index_col)
        # 这里用来处理回调函数
        count = len(colvalues)
        for colvalue in colvalues:
            handler(colvalue, config, count, index_col, type_handler)
            index_col += 1
            print(index_col)
    return 'hello world'


def read_excel_by_row(filepath, handler):
    return
