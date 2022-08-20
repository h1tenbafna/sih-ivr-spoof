from xlrd import open_workbook
def lookup(test_number):
    flag = 0
    book = open_workbook("new.xls") #xlsx   
    sheet = book.sheet_by_index(0)
    #test_number = 7083022822
    for row in range(sheet.nrows):
        #print('HELLO')
        if sheet.cell(row, 0).value == test_number:
            #print('number found', test_number)
            flag = 1
    if flag==1:
        return 1
    else:
        return 0
