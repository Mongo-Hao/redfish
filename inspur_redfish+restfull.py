import requests
import json
requests.packages.urllib3.disable_warnings()


###原理：cpu、内存、存储分别使用不同的url获取到值，如url不一致只分别修改对应的第一个url即可，后面的详细参数的URL函数自动提取
##sel日志单独使用URL获取

class GetHostInfo(object):
    def __init__(self,ipaddr,username,password):
        self.ip=ipaddr.strip()
        self.URLprefix='https://'+ipaddr.strip()
        self.username=username.strip()
        self.password=password.strip()
        global token    ##同时存在4-5个token链接，每个token链接时间为5分钟，可以自己设置。该token是在响应头获取到的，直接用到redfish认证的header中。
        global CSRFToken  ##该token是在响应的文本或json格式中获取到的，需要经过处理、加工后用到restfull认证的header中。
        global cookie     ##该cookie是在响应头获取到的，需要经过处理、加工后用到restfull认证的header中。
        CSRFToken=0
        cookie=0
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
            '''
            1、X-Auth-Token：该token是在响应头获取到的，直接用到redfish认证的header中；
            2、Set-Cookie：该cookie是在响应头获取到的，需要经过处理、加工后用到restfull或redfish认证的header中。
            3、CSRFToken：该token是在响应的文本或json格式中获取到的，需要经过处理、加工后用到restfull认证的header中。
            '''
            print (re1.json())
            print (re1.headers)
            temp_header = re1.headers
            cookie = temp_header['Set-Cookie']
            token = temp_header['X-Auth-Token']
            print('cookie_init', cookie)
            print('token_init', token)
            temp_text = re1.json()
            CSRFToken = temp_text['CSRFToken']
            print('CSRFToken',CSRFToken)
        else:
            pass
    def Redfish_Redfish_GetInfo(self,URL_suffix):  #定义总获取函数，传参url的后半部分。如'/redfish/v1/Systems/1/Memory'
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
    def Restfull_GetInfo(self,URL_suffix):
        urlset=self.URLprefix+URL_suffix
        if token !=0:
            cook = cookie.split(";")[0].split("=")[1]
            print('cookie__restfull',cookie)
            print('cook__restfull',cook)
            print('CSRFToken__restfull',CSRFToken)
            header = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Connection': 'keep-alive',
                'Cookie': 'refresh_disable=1; QSESSIONID='+cook+'',
                'Host': ''+self.ip+'',
                'Referer': 'https://'+self.ip+'/main.html',
                'X-CSRFTOKEN': ''+CSRFToken+'',
                'X-Requested-With': 'XMLHttpRequest'
                }
            re1=requests.get(urlset,headers=header,verify=False)
            print(re1.status_code)
            return re1.json()
        else:
            pass


def Collect_Info(ipaddr,username,password):
    Inspur_NF5466M5=GetHostInfo(ipaddr,username,password)
    ####处理snmp,使用restfull协议
    select_snmp_total1 = '/api/settings/snmp'
    # select_snmp_total2= '/api/settings/pef/event_filters'
    # select_snmp_total3 ='/api/settings/pef/lan_destinations'
    temp_snmp_result1 = Inspur_NF5466M5.Restfull_GetInfo(select_snmp_total1)
    # temp_snmp_result2= Inspur_NF5466M5.Restfull_GetInfo(select_snmp_total2)
    # temp_snmp_result3= Inspur_NF5466M5.Restfull_GetInfo(select_snmp_total3)
    print(temp_snmp_result1)
    # print (temp_snmp_result2)
    # print (temp_snmp_result3)

    ##测试获取sn，使用redfish协议
    snurl='/redfish/v1/Systems/System1'
    system_total=Inspur_NF5466M5.Redfish_Redfish_GetInfo(snurl)
    #print('system_total', system_total)
    print('SerialNumber', system_total['SerialNumber'])
    ####处理CPU，使用redfish协议
    select_cpu_total = '/redfish/v1/Systems/System1/Processors'
    #print('cpu_total', Inspur_NF5466M5.Redfish_Redfish_GetInfo(select_cpu_total))
    temp_cpu_result1= Inspur_NF5466M5.Redfish_Redfish_GetInfo(select_cpu_total)
    if isinstance(temp_cpu_result1,dict) and ('error' not in  temp_cpu_result1.keys() ):
        cpu_count = temp_cpu_result1['Members@odata.count']
        print('@' * 50)
        print('CPU Count:', cpu_count)
        ##获取多个cpu的URLsuffix值
        #print('select_cpu_single_URLsuffix:',[ x['@odata.id'] for x in temp_cpu_result1['Members']])
        cpu_single_URLsuffix_list=[ x['@odata.id'] for x in temp_cpu_result1['Members']]
        for cpu_single in cpu_single_URLsuffix_list:
            temp_cpu_single_result1 = Inspur_NF5466M5.Redfish_Redfish_GetInfo(cpu_single)
            #print(temp_cpu_single_result1)
            if isinstance(temp_cpu_single_result1, dict) and ('error' not in temp_cpu_single_result1.keys()):
                print('CPU single name：',temp_cpu_single_result1['Socket'])
                print('CPU single ID：',temp_cpu_single_result1['Id'])
                print('CPU single TotalCores(cpus):', temp_cpu_single_result1['TotalCores'])
                print('CPU single Model(cpus):', temp_cpu_single_result1['Model'])

    ####处理内存，使用redfish协议
    # 取出内存个数，字典键'Members@odata.count'
    select_memory_total = '/redfish/v1/Systems/System1/Memory'
    temp_memory_result1=Inspur_NF5466M5.Redfish_Redfish_GetInfo(select_memory_total)
    if isinstance(temp_memory_result1,dict) and ('error' not in  temp_memory_result1.keys() ):
        Mem_count = temp_memory_result1['Members@odata.count']
        print('@' * 50)
        print('Memory Count:', Mem_count)
        #获取Memory的URLsuffix.
        #print('select_memory_single_URLsuffix:', [x['@odata.id'] for x in temp_memory_result1['Members']])
        Mem_single_URLsuffix_list = [x['@odata.id'] for x in temp_memory_result1['Members']]
        #print (Mem_single_URLsuffix_list)
        # 取出类型和大小
        for select_memory_single in Mem_single_URLsuffix_list:
            temp_memory_result2=Inspur_NF5466M5.Redfish_Redfish_GetInfo(select_memory_single)
            #print (temp_memory_result2)
            if isinstance(temp_memory_result2,dict) and ('error' not  in temp_memory_result2.keys() ):
                # return temp_memory_result2['CapacityMiB']/1024   ##M/1024=G
                print('Memory name:',temp_memory_result2['Name'])
                print('Memory ID:',temp_memory_result2['Id'])
                print('Memory Size:', temp_memory_result2['CapacityMiB'])
                print('Memory Type:', temp_memory_result2['MemoryDeviceType'])
    ##测试storage，使用redfish协议
    #select_storages_test = '/redfish/v1/Systems/System1/Storages/0/Drives/0' ##正确的URL
    #select_storages_test = '/redfish/v1/Systems/System1/Storages/1/Drives/0'  ##错误的URL
    #test_storages_result1 = Inspur_NF5466M5.Redfish_Redfish_GetInfo(select_storages_test)
    #print('test',test_storages_result1)
    ####处理存储storages
    select_storages_total='/redfish/v1/Systems/System1/Storages'
    temp_storages_result1 = Inspur_NF5466M5.Redfish_Redfish_GetInfo(select_storages_total)
    #print (temp_storages_result1)
    disk_count =0
    if isinstance(temp_storages_result1, dict) and ('error' not in temp_storages_result1.keys()):
        storage_disk_url=temp_storages_result1['Members'][0]['@odata.id']
        #print ('URL_raid',storage_disk_url)
        temp_disk_result1 = Inspur_NF5466M5.Redfish_Redfish_GetInfo(storage_disk_url)
        storages_single_URLsuffix_list=temp_disk_result1['Drives'] ##取出所有磁盘的URL
        #print(storages_single_URLsuffix_list)    #disk_URLsuffix
        for disk_single in storages_single_URLsuffix_list:
            #print(type(disk_single),disk_single)
            disk_single_URL=disk_single.replace('Storage/1','Storages/0')  ##自动获取的URL盘位错误，storage改为storages,1改为0
            #print(disk_single_URL)
            temp_disk_result2 = Inspur_NF5466M5.Redfish_Redfish_GetInfo(disk_single_URL)
            #print ('temp_disk_result2',temp_disk_result2)
            if isinstance(temp_disk_result2, dict) and ('error' not in temp_disk_result2.keys()):
                print ('disk name：',temp_disk_result2['Model'])
                print ('disk ID：',temp_disk_result2['SerialNumber'])
                print ('disk CapacityBytes：',temp_disk_result2['CapacityBytes'])
                print ('disk MediaType：',temp_disk_result2['MediaType'])

    ##SEL日志处理，使用redfish协议
    # eventlogURL='/redfish/v1/Systems/System1/LogServices'
    # print('log_SEL', Inspur_NF5466M5.Redfish_Redfish_GetInfo(eventlogURL))

if __name__ == '__main__':
    Collect_Info('10.251.199.73', 'root', 'password')
    #Collect_Info('10.251.199.73', 'root', 'password')



