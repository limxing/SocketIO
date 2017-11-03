import tushare as ts


def getNotices(code):
    return ts.get_notices(code=code)
