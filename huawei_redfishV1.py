import requests
import json
import re
requests.packages.urllib3.disable_warnings()


###版本:修改了cpu、内存、存储的URL分别通过一个system总URL自动获取到，不需要分别修改三个URL。
##sel日志单独使用URL获取

class GetHostInfo(object):
    def __init__(self,ipaddr,username,password):
        self.URLprefix='https://'+ipaddr.strip()
        self.username=username.strip()
        self.password=password.strip()
        global token    ##同时存在4-5个token链接，每个token链接时间为5分钟，可以自己设置。
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
        #print (re1.status_code)
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
            #print(re1.status_code)
            return (re1.json())
        else:
            pass
    def selectlog(self):   ##查询SEL日志,13版pdf815页
        ##post https://device_ip/redfish/v1/Systems/system_id/LogServices/LogService_id/Actions/Oem/Huawei/LogService.QuerySelLogEntries
        url_selcetSELlog = self.URLprefix+'/redfish/v1/Systems/1/LogServices/Log1/Actions/Oem/Huawei/LogService.QuerySelLogEntries'  ##LogService_id==Log1
        if token != 0:
            header = {
                "Content-Type": "application/json",
                "X-Auth-Token": token
            }
            # "StartEntryId": StartEntryId_value,  ##查询sel日志的起始条数，必选项。从1开始，且不大于日志总数
            # "EntriesCount": EntriesCount_value,  ##日志条数，大于0的整数
            # "SelLevel": SelLevelvalue,  ##日志级别，非必选，四类：Informational、Minor、Major、Critical
            # "SelObjectType": SelObjectTypevalue,  ##主题类型，非必选
            # "SelBeginTime": SelBeginTime_value,  ##起始时间，非必选，支持的日期格式：yyyy-MM-dd HH:mm:ss
            # "SelEndTime": SelEndTimevalue,  ##结束时间，非必选，支持的日期格式：yyyy-MM-dd HH:mm:ss
            # "SelSearchString": SelSearchStringvalue  ##关键字，非必选
            ###################ssh iBMC#####################
            #iBMC:/->ipmcget -d sel -v info          ##显示日志信息
            # SEL Information
            # Version               :  1.0.0
            # Current Event Number  :  97            ##97个条目，redfish协议查不出多少条目
            # Max Event Number      :  4000
            #iBMC:/->ipmcget -d sel -v list          ##显示所有条目，数据库格式
            #iBMC:/->ipmcget -d sel -v suggestion 1  ##1为event number.
            # iBMC:/->ipmcset -d sel -v clear        ##清空历史记录
            # WARNING: The operation may have many adverse effects.
            # Do you want to continue?[Y/N]:Y
            # Clear SEL records successfully.
            # iBMC:/->
            data={
                "StartEntryId":1,
                "EntriesCount":1
            }
            re1 = requests.post(url_selcetSELlog ,json.dumps(data), headers=header, verify=False)
            print('SelectLog_StatusCode', re1.status_code)
            return re1.json()




def Collect_Info(ipaddr,username,password):
    hw2288HV5=GetHostInfo(ipaddr,username,password)
    ##system
    select_system_total = '/redfish/v1/Systems/1'
    # print('select_system_total', hw2288HV5.GetInfo(select_system_total))
    temp_system_result1 = hw2288HV5.GetInfo(select_system_total)
    if isinstance(temp_system_result1, dict) and ('error' not in temp_system_result1.keys()):
        #print('system_result1',temp_system_result1)
        ####处理CPU
        select_cpu_total = temp_system_result1['Processors']['@odata.id']  ##获取CPU的URL
        #select_cpu_total = '/redfish/v1/Systems/1/Processors'
        #print('cpu_total', hw2288HV5.GetInfo(select_cpu_total))
        temp_cpu_result1= hw2288HV5.GetInfo(select_cpu_total)
        if isinstance(temp_cpu_result1,dict) and ('error' not in  temp_cpu_result1.keys() ):
            cpu_count = temp_cpu_result1['Members@odata.count']
            print('@' * 50)
            print('CPU Count:', cpu_count)
            ##获取多个cpu的URLsuffix值
            #print('select_cpu_single_URLsuffix:',[ x['@odata.id'] for x in temp_cpu_result1['Members']])
            cpu_single_URLsuffix_list=[ x['@odata.id'] for x in temp_cpu_result1['Members']]
            for cpu_single in cpu_single_URLsuffix_list:
                temp_cpu_single_result1 = hw2288HV5.GetInfo(cpu_single)
                #print(temp_cpu_single_result1)
                if isinstance(temp_cpu_single_result1, dict) and ('error' not in temp_cpu_single_result1.keys()):
                    print('CPU single name：',temp_cpu_single_result1['Name'])
                    print('CPU single ID：',temp_cpu_single_result1['Id'])
                    print('CPU single TotalCores(cpus):', temp_cpu_single_result1['TotalCores'])
                    print('CPU single Model(cpus):', temp_cpu_single_result1['Model'])

        ####处理内存
        # 取出内存个数，字典键'Members@odata.count'
        select_memory_total = temp_system_result1['Memory']['@odata.id']  ##获取memory的URL
        #select_memory_total = '/redfish/v1/Systems/1/Memory'
        temp_memory_result1=hw2288HV5.GetInfo(select_memory_total)
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
                temp_memory_result2=hw2288HV5.GetInfo(select_memory_single)
                #print (temp_memory_result2)
                if isinstance(temp_memory_result2,dict) and ('error' not  in temp_memory_result2.keys() ):
                    # return temp_memory_result2['CapacityMiB']/1024   ##M/1024=G
                    print('Memory name:',temp_memory_result2['Name'])
                    print('Memory ID:',temp_memory_result2['Id'])
                    print('Memory Size:', temp_memory_result2['CapacityMiB'])
                    print('Memory Type:', temp_memory_result2['MemoryDeviceType'])
        ####处理存储storages
        select_storages_total = temp_system_result1['Storage']['@odata.id']  ##获取storage的URL
        #select_storages_total='/redfish/v1/Systems/1/Storages'
        temp_storages_result1 = hw2288HV5.GetInfo(select_storages_total)
        #print (temp_storages_result1)
        if isinstance(temp_storages_result1, dict) and ('error' not in temp_storages_result1.keys()):
            storages_raid_count = temp_storages_result1['Members@odata.count']
            print('@' * 50)
            print('Storages Raidzone Count:', storages_raid_count) #'StorageControllers@odata.count'
            # 获取storages raidzonename的URLsuffix.
            #print('select_storages_raidzone_name_URLsuffix:', [x['@odata.id'] for x in temp_storages_result1['Members']])
            storages_single_URLsuffix_list = [x['@odata.id'] for x in temp_storages_result1['Members']]
            #print(storages_single_URLsuffix_list)    #raidzone的URLsuffix
            # 取出raidzone中磁盘的类型和大小
            for select_storages_raidzone_single in storages_single_URLsuffix_list:
                temp_storages_raiddisk_result2 = hw2288HV5.GetInfo(select_storages_raidzone_single)
                #print (temp_storages_raiddisk_result2)
                print ('@'*60)
                print ('raidzone name:',temp_storages_raiddisk_result2['Name'])
                print ('raidzone ID:',temp_storages_raiddisk_result2['Id'])
                print ('raidzone disk count:',temp_storages_raiddisk_result2['Drives@odata.count'])
                if isinstance(temp_storages_raiddisk_result2, dict) and ('error' not in temp_storages_raiddisk_result2.keys()):
                    storages_singledisk_URLsuffix_list = [x['@odata.id'] for x in temp_storages_raiddisk_result2['Drives']]
                    #print ('storages_singledisk-URLsuffix',storages_singledisk_URLsuffix_list)
                    for storages_singledisk in storages_singledisk_URLsuffix_list:
                        temp_storages_singledisk_result2 = hw2288HV5.GetInfo(storages_singledisk)
                        #print('temp_storages_singledisk_result2 :',temp_storages_singledisk_result2)
                        if isinstance(temp_storages_singledisk_result2, dict) and ('error' not in temp_storages_singledisk_result2.keys()):
                            print ('disk name：',temp_storages_singledisk_result2['Name'])
                            print ('disk ID：',temp_storages_singledisk_result2['Id'])
                            print ('disk CapacityBytes：',temp_storages_singledisk_result2['CapacityBytes'])
                            print ('disk MediaType：',temp_storages_singledisk_result2['MediaType'])

        ##获取设备标签 主机名
        hostname='/redfish/v1/Managers/1/NetworkProtocol'
        temp_hostname_result1 = hw2288HV5.GetInfo(hostname)
        # print (temp_logss_result1)
        if isinstance(temp_hostname_result1, dict) and ( 'error' not in temp_hostname_result1.keys()):
            print('hostname',temp_hostname_result1['HostName'])
        ##SEL日志处理
        log_SEL=hw2288HV5.selectlog()   ##查询出sel_log的一定范围的
        if isinstance(log_SEL, dict):
            str_log = str(log_SEL)
            #print(str_log)
            try:
                SelLog_number_result = re.findall(r"'number'\:\W\d+", str_log)
                SelLog_number=(SelLog_number_result[0].replace("'number': ",''))
                print ('SelLog_number :',SelLog_number)
            except:
                pass

if __name__ == '__main__':
    Collect_Info('10.2.1.1', 'username', 'password')    ##华为，两个raid组。
    #Collect_Info('10.2.1.1', 'username', 'ypassword')     ##华为，单个raid组。





