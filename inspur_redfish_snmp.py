import json
import requests
requests.packages.urllib3.disable_warnings()
'''
脚本中使用了redfish协议获取到token和cookie，然后去找redfish的snmp的URL时候发现没有对应的信息，随即使用postman工具获取到restfull协议的url，然后使用redfish获取的token和cookie，拿着restfull协议的URL去获取对应的信息。
'''
class GetHostInfo(object):
    def __init__(self,ipaddr,username,password):
        self.ipaddr=ipaddr
        self.URLprefix='https://'+ipaddr.strip()
        self.username=username.strip()
        self.password=password.strip()
        global token   
        global cook
        cook=0
        token=0
        tokenurl=self.URLprefix+'/redfish/v1/SessionService/Sessions'
        print(tokenurl)
        data={
            "UserName":self.username,
            "Password":self.password
            }
        header={
            "Content-Type":"application/json"
            }
        re1=requests.post(tokenurl,json.dumps(data),headers=header,verify=False)
        print (re1.status_code)
        if re1.status_code == 201:
            #print (re1.json())
            #print (re1.headers)
            temp_header = re1.headers
            cookie = temp_header['Set-Cookie']
            temp_token = re1.json()
            token = temp_token['CSRFToken']
            cook = cookie.split(";")[0].split("=")[1]
            print('cookie',cookie)
            print('cook',cook)
            print('token',token)
        else:
            pass
    def GetInfo(self,URL_suffix):  #定义总获取函数，传参url的后半部分。如'/redfish/v1/Systems/1/Memory'
        urlset=self.URLprefix+URL_suffix
        if token !=0:
            header = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Connection': 'keep-alive',
                'Cookie': 'refresh_disable=1; QSESSIONID='+cook+'',
                'Host': ''+self.ipaddr+'',
                'Referer': 'https://'+self.ipaddr+'/main.html',
                'X-CSRFTOKEN': ''+token+'',
                'X-Requested-With': 'XMLHttpRequest'
                }
            re1=requests.get(urlset,headers=header,verify=False)
            print(re1.status_code)
            return (re1.json())
        else:
            pass


def Collect_Info(ipaddr,username,password):
    INSPUR=GetHostInfo(ipaddr,username,password)
    ####处理snmp
    select_snmp_total1='/api/settings/snmp'
    select_snmp_total2= '/api/settings/pef/event_filters'
    select_snmp_total3 ='/api/settings/pef/lan_destinations'
    temp_snmp_result1= INSPUR.GetInfo(select_snmp_total1)
    temp_snmp_result2= INSPUR.GetInfo(select_snmp_total2)
    temp_snmp_result3= INSPUR.GetInfo(select_snmp_total3)
    print (temp_snmp_result1)
    #print (temp_snmp_result2)
    print (temp_snmp_result3)


if __name__ == '__main__':
    Collect_Info('10.251.199.73', 'root', 'password')
