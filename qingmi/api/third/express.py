# coding: utf-8
""" Third party express apis. """
import sys
import urllib.request
import json
from qingmi.utils import base64_md5

def kdniao(userid, appkey, shipper_code, logistic_code):
    """ 快递鸟 """
    express_api = 'http://api.kdniao.cc/Ebusiness/EbusinessOrderHandle.aspx'
    request_data = dict(
        OrderCode='',
        ShipperCode=shipper_code,
        LogisticCode=logistic_code,
    )
    request_data_str = json.dumps(request_data)
    datasign = base64_md5(request_data_str+appkey)
    data = dict(
        EBusinessID=userid,
        DataType=2,
        RequestType=1002,
        RequestData=request_data_str,
        DataSign=datasign,
    )
    url_values = urllib.parse.urlencode(data)
    express_url = express_api + '?' + url_values
    response = urllib.request.urlopen(express_url)
    context = response.read().decode('utf-8')
    return json.loads(context)
