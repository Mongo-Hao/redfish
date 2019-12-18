
import requests
import json
requests.packages.urllib3.disable_warnings()

##使用一个system总的URL分别获取到cpu、内存、存储三个url.所以只修改system的URL即可
##sel日志单独使用URL获取


class GetHostInfo(object):
    def __init__(self,ipaddr,username,password):
        self.URLprefix='https://'+ipaddr.strip()
        self.username=username.strip()
        self.password=password.strip()
        global token    ##同时存在4-5个token链接，每个token链接时间为5分钟，可以自己设置。
        token=0
        tokenurl=self.URLprefix+'/redfish/v1/Sessions'  ##dell获取token的ID
        print(tokenurl)
        data={
            "UserName":self.username,
            "Password":self.password
            }
        header={
            "Content-Type":"application/json"
            }
        re1=requests.post(tokenurl,json.dumps(data),headers=header,verify=False)
        #re1=requests.post(tokenurl,auth=(self.username,self.password),headers=header,verify=False)
        print (re1.status_code)
        if re1.status_code == 201:
            #print (re1.json())
            #print (re1.headers)
            print (re1.headers['X-Auth-Token'])
            token=re1.headers['X-Auth-Token']
        else:
            pass
    def GetInfo(self,URL_suffix):  #定义总获取函数，传参url的后半部分。如'/redfish/v1/Systems/1/Memory'
        urlset=self.URLprefix+URL_suffix
        if token !=0:
            header = {
                "Content-Type":"application/json",
                "X-Auth-Token":token
                }
            re1=requests.get(urlset,headers=header,verify=False)
            print(re1.status_code)
            return re1.json()
        else:
            pass

def Collect_Info(ipaddr,username,password):
    dell740=GetHostInfo(ipaddr,username,password)
    ####total_system_URL收集/redfish/v1/Systems/System.Embedded.1
    select_system_total = '/redfish/v1/Systems/System.Embedded.1'
    #print('cpu_total', hw2288HV5.GetInfo(select_cpu_total))
    temp_system_result1= dell740.GetInfo(select_system_total)
    if isinstance(temp_system_result1,dict) and ('error' not in  temp_system_result1.keys() ):
        ##处理cpu
        cpu = temp_system_result1['Processors']['@odata.id']  ##获取CPU的URL
        #print ('Processors',dell740.GetInfo(cpu))
        cpu_result1 = dell740.GetInfo(cpu)
        cpu_count = cpu_result1['Members@odata.count']
        cpu_URLsuffix_list = [x['@odata.id'] for x in cpu_result1['Members']]
        print('CPU count:', cpu_count)
        for single_cpuurl in cpu_URLsuffix_list:
            singlecpu_result2= dell740.GetInfo(single_cpuurl)
            if isinstance(singlecpu_result2, dict) and ('error' not in singlecpu_result2.keys()):
                #print ('singlecpu_result2',singlecpu_result2)
                print('CPU single name：', singlecpu_result2['Name'])
                print('CPU single ID：', singlecpu_result2['Id'])
                print('CPU single TotalCores(cpus):', singlecpu_result2['TotalCores'])
                print('CPU single Model(cpus):', singlecpu_result2['Model'])

        ###处理内存
        memory = temp_system_result1['Memory']['@odata.id']  ##获取内存的URL
        memory_result1 = dell740.GetInfo(memory)
        memory_count = memory_result1['Members@odata.count']
        memory_URLsuffix_list = [x['@odata.id'] for x in memory_result1['Members']]
        print ('Memory count:',memory_count)
        for single_memoryurl in memory_URLsuffix_list:
            singlememory_result2 = dell740.GetInfo(single_memoryurl)
            if isinstance(singlememory_result2, dict) and ('error' not in singlememory_result2.keys()):
                #print('singlecpu_result2', singlememory_result2)
                print('Memory name:', singlememory_result2['Name'])
                print('Memory ID:', singlememory_result2['Id'])
                print('Memory Size:', singlememory_result2['CapacityMiB'])
                print('Memory Type:', singlememory_result2['MemoryDeviceType'])


        ##处理存储
        storage = temp_system_result1['Storage']['@odata.id']  ##获取存储URL
        #print ('storage',dell740.GetInfo(storage))
        storage_result1 = dell740.GetInfo(storage)
        storage_URLsuffix_list = [x['@odata.id'] for x in storage_result1['Members']]
        for single_storageurl in storage_URLsuffix_list:
            singlestorage_result2 = dell740.GetInfo(single_storageurl)
            if isinstance(singlestorage_result2, dict) and ('error' not in singlestorage_result2.keys()):
                #print('singlecpu_result2', singlestorage_result2)
                disk_count=singlestorage_result2['Drives@odata.count']
                print('disk count:',disk_count)
                print('storage name:',singlestorage_result2['Id'])
                if disk_count >0: ##有的URL中disk为0，不需要去获取值
                    single_disk_URLsuffix_list = [x['@odata.id'] for x in singlestorage_result2['Drives']]
                    for disk_single in single_disk_URLsuffix_list:
                        single_disk_result1 = dell740.GetInfo(disk_single)
                        if isinstance(single_disk_result1, dict) and ('error' not in single_disk_result1.keys()):
                            #print ('single_disk_result1',single_disk_result1)
                            print('disk name：', single_disk_result1['Name'])
                            print('disk ID：', single_disk_result1['Id'])
                            print('disk CapacityBytes：', single_disk_result1['CapacityBytes'])
                            print('disk MediaType：', single_disk_result1['MediaType'])
                        else:
                            pass
    ##获取sel日志
    logurlsuffix = '/redfish/v1/Managers/iDRAC.Embedded.1/Logs/Sel'  ##日志sel
    sellog=dell740.GetInfo(logurlsuffix)
    if isinstance(sellog,dict) and ('error' not in  sellog.keys() ):
        print('SEL log:',sellog)

if __name__ == '__main__':
    Collect_Info('10.252.209.7', 'username', 'password')
