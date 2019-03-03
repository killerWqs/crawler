import xlrd


def read_excel_by_col(filepath, handler, config):
    excelfile = xlrd.open_workbook(filepath)
    print(excelfile.sheet_names())

    sheet1 = excelfile.sheet_by_index(0)
    colscount = sheet1.ncols
    index_col = 0

    while index_col < colscount:
        colvalues = sheet1.col_values(index_col)
        # 这里用来处理回调函数
        for colvalue in colvalues:
            handler(colvalue, config)
        index_col = index_col + 1
    return 'hello world'


def read_excel_by_row(filepath, handler):
    return
