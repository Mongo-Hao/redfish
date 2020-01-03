
import requests
import json
requests.packages.urllib3.disable_warnings()

'''
以下有三个类，分别是redfish协议测试、restfull协议测试、以及两个合并测试。
'''

##redfish认证过程和获取参数
class redfish_getinfo(object):
    def __init__(self,ipaddr,username,password):
        self.ip=ipaddr.strip()
        self.URLprefix='https://'+ipaddr.strip()
        self.username=username.strip()
        self.password=password.strip()
        global token
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
            print ('redfish_info',re1.json())
            print ('redfish_header',re1.headers)
            temp_header = re1.headers
            token= temp_header['X-Auth-Token']
            print('redfish_token', token)
        else:
            pass
    def redfish_info(self,URL_suffix):  #定义总获取函数，传参url的后半部分。如'/redfish/v1/Systems/1/Memory'
        urlset=self.URLprefix+URL_suffix
        if token !=0:
            header = {
                "Content-Type":"application/json",
                "X-Auth-Token":token
                }
            re1=requests.get(urlset,headers=header,verify=False)
            #print(re1.status_code)
            return (re1.json())
        else:
            pass
##restfull认证过程和获取参数
class restfull_info(object):
    def __init__(self,ipaddr,username,password):
        self.ip=ipaddr.strip()
        self.username=username
        self.password=password
        self.URLprefix='http://' + ipaddr.strip()
        global CSRFToken   ##同时存在4-5个token链接，每个token链接时间为5分钟，可以自己设置。
        global cookie
        CSRFToken=0
        cookie=0
        tokenurl=self.URLprefix+'/api/session'
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Content-Length': '39',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Host': '' + self.ip + '',
            'Origin': 'http://' + self.ip + '',
            'Referer': 'http://' + self.ip + '/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        print(tokenurl)
        data={
            "username":self.username,
            "password":self.password
            }
        re1=requests.post(tokenurl,data=data,headers=headers,verify=False)
        print (re1.status_code)
        if re1.status_code == 200:
            #print (re1.json())
            # print(re1.status_code)
            # print(re1.json())
            # print('header:', re1.headers)
            # temp = re1.json()
            # print(temp['CSRFToken'])
            print(re1.headers)
            print (re1.json())
            temp_header=re1.headers
            cookie=temp_header['Set-Cookie']
            temp_token=re1.json()
            CSRFToken=temp_token['CSRFToken']
            print ('restfull_cookie',cookie)
            print ('restfull_CSRFToken',CSRFToken)
        else:
            pass
    def restfull_info(self,URL_suffix):  #定义总获取函数，传参url的后半部分。如'/redfish/v1/Systems/1/Memory'
        urlset=self.URLprefix + URL_suffix.strip()
        #print(urlset)
        # print ('token:',token)
        # print ('cookie:',cookie)
        if cookie != 0  and token != 0 :
            cook = cookie.split(";")[0].split("=")[1]
            print ('restfull_cook',cook)
            header = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Connection': 'keep-alive',
                'Cookie': 'refresh_disable=1; QSESSIONID='+cook+'',
                'Host': ''+self.ip+'',
                'Referer': 'http://'+self.ip+'/',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
                'X-CSRFTOKEN': ''+CSRFToken+'',
                'X-Requested-With': 'XMLHttpRequest'
                }
            re1=requests.get(urlset,headers=header,verify=False)
            print(re1.status_code)
            return (re1.json())
        else:
            pass

##合并restfull与redfish为一个类。
class GetHostInfo(object):
    def __init__(self,ipaddr,username,password):
        self.ip=ipaddr.strip()
        self.URLprefix='https://'+ipaddr.strip()
        self.username=username.strip()
        self.password=password.strip()
        global redfish_token
        global restfull_CSRFToken
        global restfull_cookie
        restfull_CSRFToken=0
        restfull_cookie=0
        redfish_token=0     ##该token是加密的
        ##以下是redfish的认证过程
        redfishurl=self.URLprefix+'/redfish/v1/SessionService/Sessions'
        print(redfishurl)
        data={
            "UserName":self.username,
            "Password":self.password
            }
        header={
            "Content-Type":"application/json"
            }
        re1=requests.post(redfishurl,json.dumps(data),headers=header,verify=False)
        print(re1.status_code)
        if re1.status_code == 201:
            print('redfish_info', re1.json())
            print('redfish_header', re1.headers)
            temp_header = re1.headers
            redfish_token = temp_header['X-Auth-Token']
            print('redfish_token', redfish_token)
        else:
            pass
        ##以下是restfull的认证过程
        restfullurl = self.URLprefix + '/api/session'
        restheaders = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Content-Length': '39',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Host': '' + self.ip + '',
            'Origin': 'http://' + self.ip + '',
            'Referer': 'http://' + self.ip + '/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        print(restfullurl)
        data = {
            "username": self.username,
            "password": self.password
        }
        re1 = requests.post(restfullurl, data=data, headers=restheaders, verify=False)
        print(re1.status_code)
        if re1.status_code == 200:
            # print (re1.json())
            # print(re1.status_code)
            # print(re1.json())
            # print('header:', re1.headers)
            # temp = re1.json()
            # print(temp['CSRFToken'])
            print(re1.headers)
            print(re1.json())
            temp_header = re1.headers
            restfull_cookie = temp_header['Set-Cookie']
            temp_token = re1.json()
            restfull_CSRFToken = temp_token['CSRFToken']
            print('restfull_cookie', restfull_cookie)
            print('restfull_CSRFToken', restfull_CSRFToken)
        else:
            pass

    def redfish_info(self,URL_suffix):  #定义总获取函数，传参url的后半部分。如'/redfish/v1/Systems/1/Memory'
        urlset=self.URLprefix+URL_suffix
        if token !=0:
            header = {
                "Content-Type":"application/json",
                "X-Auth-Token":redfish_token
                }
            re1=requests.get(urlset,headers=header,verify=False)
            #print(re1.status_code)
            return (re1.json())
        else:
            pass
    def restfull_info(self,URL_suffix):
        urlset=self.URLprefix+URL_suffix
        if token !=0:
            cook = restfull_cookie.split(";")[0].split("=")[1]
            print('cookie__restfull',restfull_cookie)
            print('cook__restfull',cook)
            print('CSRFToken__restfull',restfull_CSRFToken)
            header = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Connection': 'keep-alive',
                'Cookie': 'refresh_disable=1; QSESSIONID='+cook+'',
                'Host': ''+self.ip+'',
                'Referer': 'https://'+self.ip+'/main.html',
                'X-CSRFTOKEN': ''+restfull_CSRFToken+'',
                'X-Requested-With': 'XMLHttpRequest'
                }
            re1=requests.get(urlset,headers=header,verify=False)
            print(re1.status_code)
            return re1.json()
        else:
            pass


##redfish获取参数的测试
##使用一个system总的URL分别获取到cpu、内存、存储三个url.所以只修改system的URL即可
##sel日志单独使用URL获取
def Collect_Iredfish_getinfonfo(ipaddr,username,password):
    H3CR4900=redfish_getinfo(ipaddr,username,password)
    ####total_system_URL收集/redfish/v1/Systems/1
    select_system_total = '/redfish/v1/Systems/1'
    #print('cpu_total', hw2288HV5.Redfish_GetInfo(select_cpu_total))
    temp_system_result1= H3CR4900.redfish_info(select_system_total)
    if isinstance(temp_system_result1,dict) and ('error' not in  temp_system_result1.keys() ):
        ##处理cpu
        cpu = temp_system_result1['Processors']['@odata.id']  ##获取CPU的URL
        #print ('Processors',H3CR4900.Redfish_GetInfo(cpu))
        cpu_result1 = H3CR4900.redfish_info(cpu)
        cpu_count = cpu_result1['Members@odata.count']
        cpu_URLsuffix_list = [x['@odata.id'] for x in cpu_result1['Members']]
        print('CPU count:', cpu_count)
        for single_cpuurl in cpu_URLsuffix_list:
            singlecpu_result2= H3CR4900.redfish_info(single_cpuurl)
            if isinstance(singlecpu_result2, dict) and ('error' not in singlecpu_result2.keys()):
                #print ('singlecpu_result2',singlecpu_result2)
                print('CPU single name：', singlecpu_result2['Name'])
                print('CPU single ID：', singlecpu_result2['Id'])
                print('CPU single TotalCores(cpus):', singlecpu_result2['TotalCores'])
                print('CPU single Model(cpus):', singlecpu_result2['Model'])

        ###处理内存
        memory = temp_system_result1['Memory']['@odata.id']  ##获取内存的URL
        memory_result1 = H3CR4900.redfish_info(memory)
        memory_count = memory_result1['Members@odata.count']
        memory_URLsuffix_list = [x['@odata.id'] for x in memory_result1['Members']]
        print ('Memory count:',memory_count)
        for single_memoryurl in memory_URLsuffix_list:
            singlememory_result2 = H3CR4900.redfish_info(single_memoryurl)
            if isinstance(singlememory_result2, dict) and ('error' not in singlememory_result2.keys()):
                #print('singlecpu_result2', singlememory_result2)
                print('Memory name:', singlememory_result2['Name'])
                print('Memory ID:', singlememory_result2['Id'])
                print('Memory Size:', singlememory_result2['CapacityMiB'])
                print('Memory Type:', singlememory_result2['MemoryDeviceType'])


        ##处理存储
        storage = temp_system_result1['Storage']['@odata.id']  ##获取存储URL
        #print ('storage',H3CR4900.Redfish_GetInfo(storage))
        storage_result1 = H3CR4900.redfish_info(storage)
        storage_URLsuffix_list = [x['@odata.id'] for x in storage_result1['Members']]
        for single_storageurl in storage_URLsuffix_list:
            singlestorage_result2 = H3CR4900.redfish_info(single_storageurl)
            if isinstance(singlestorage_result2, dict) and ('error' not in singlestorage_result2.keys()):
                #print('singlecpu_result2', singlestorage_result2)
                disk_count=singlestorage_result2['Drives@odata.count']
                print('disk count:',disk_count)
                print('storage name:',singlestorage_result2['Id'])
                if disk_count >0: ##有的URL中disk为0，不需要去获取值
                    single_disk_URLsuffix_list = [x['@odata.id'] for x in singlestorage_result2['Drives']]
                    for disk_single in single_disk_URLsuffix_list:
                        single_disk_result1 = H3CR4900.redfish_info(disk_single)
                        if isinstance(single_disk_result1, dict) and ('error' not in single_disk_result1.keys()):
                            #print ('single_disk_result1',single_disk_result1)
                            print('disk name：', single_disk_result1['Name'])
                            print('disk ID：', single_disk_result1['Id'])
                            print('disk CapacityBytes：', single_disk_result1['CapacityBytes'])
                            print('disk MediaType：', single_disk_result1['MediaType'])
                        else:
                            pass
    ##获取sel日志   需要四个url执行。
    # logurlsuffix = '/redfish/v1/Managers/iDRAC.Embedded.1/Logs/Sel'  ##日志sel
    # sellog=H3CR4900.Redfish_GetInfo(logurlsuffix)
    # if isinstance(sellog,dict) and ('error' not in  sellog.keys() ):
    #     print('SEL log:',sellog)

if __name__ == '__main__':
    # Collect_Info('10.251.214.12', 'ydview', 'yd@sj1507')
    ##以下是redfish和restfull的分别测试
    redfish_system ='/redfish/v1/Systems/1'
    restfull_cpuage='/api/system/cupsdata'
    restfull_info=restfull_info('10.251.214.12','ydview', 'yd@sj1507')
    redfish_info=redfish_getinfo('10.251.214.12','ydview', 'yd@sj1507')
    print ('restfull',restfull_info.restfull_info(restfull_cpuage))
    print ('redfish',redfish_info.redfish_info(redfish_system))
    ##以下是restful和redfish合并后
    redfish_resfull=GetHostInfo('10.251.214.11','ydview', 'yd@sj1507')
    print('restfull', redfish_resfull.restfull_info(restfull_cpuage))
    print('redfish', redfish_resfull.redfish_info(redfish_system))

