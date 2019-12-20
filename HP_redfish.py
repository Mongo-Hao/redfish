import requests
import json
requests.packages.urllib3.disable_warnings()

###
###原理：cpu、内存、存储分别使用不同的url获取到值，如url不一致只分别修改对应的第一个url即可，后面的详细参数的URL函数自动提取
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

def Collect_Info(ipaddr,username,password):
    HPDL380G5=GetHostInfo(ipaddr,username,password)
    ####处理CPU
    select_cpu_total = '/redfish/v1/Systems/1/Processors'
    #print('cpu_total', HPDL380G5.GetInfo(select_cpu_total))
    temp_cpu_result1= HPDL380G5.GetInfo(select_cpu_total)
    if isinstance(temp_cpu_result1,dict) and ('error' not in  temp_cpu_result1.keys() ):
        cpu_count = temp_cpu_result1['Members@odata.count']
        print('@' * 50)
        print('CPU Count:', cpu_count)
        ##获取多个cpu的URLsuffix值
        #print('select_cpu_single_URLsuffix:',[ x['@odata.id'] for x in temp_cpu_result1['Members']])
        cpu_single_URLsuffix_list=[ x['@odata.id'] for x in temp_cpu_result1['Members']]
        for cpu_single in cpu_single_URLsuffix_list:
            temp_cpu_single_result1 = HPDL380G5.GetInfo(cpu_single)
            #print(temp_cpu_single_result1)
            if isinstance(temp_cpu_single_result1, dict) and ('error' not in temp_cpu_single_result1.keys()):
                print('CPU single name：',temp_cpu_single_result1['Name'])
                print('CPU single ID：',temp_cpu_single_result1['Id'])
                print('CPU single TotalCores(cpus):', temp_cpu_single_result1['TotalCores'])
                print('CPU single Model(cpus):', temp_cpu_single_result1['Model'])

    ####处理内存
    # 取出内存个数，字典键'Members@odata.count'
    select_memory_total = '/redfish/v1/Systems/1/Memory'
    temp_memory_result1=HPDL380G5.GetInfo(select_memory_total)
    #print('temp_memory_result1',temp_memory_result1)
    memory_count = 0
    if isinstance(temp_memory_result1,dict) and ('error' not in  temp_memory_result1.keys() ):
        Mem_count = temp_memory_result1['Members@odata.count']   ##包含容量为0的内存
        print('@' * 50)
        print('Memory Total Count(exist):', Mem_count)
        #获取Memory的URLsuffix.
        #print('select_memory_single_URLsuffix:', [x['@odata.id'] for x in temp_memory_result1['Members']])
        Mem_single_URLsuffix_list = [x['@odata.id'] for x in temp_memory_result1['Members']]
        #print (Mem_single_URLsuffix_list)
        # 取出类型和大小
        for select_memory_single in Mem_single_URLsuffix_list:
            temp_memory_result2=HPDL380G5.GetInfo(select_memory_single)
            #print (temp_memory_result2)
            if isinstance(temp_memory_result2,dict) and ('error' not  in temp_memory_result2.keys() ):
                Memory_Size = temp_memory_result2['CapacityMiB']
                if Memory_Size != 0 :  #默认容量为0的也打印。
                    # return temp_memory_result2['CapacityMiB']/1024   ##M/1024=G
                    print('Memory name:',temp_memory_result2['Name'])
                    print('Memory ID:',temp_memory_result2['Id'])
                    print('Memory Size:',Memory_Size)
                    print('Memory Type:', temp_memory_result2['MemoryType'])
                    memory_count += 1
    print ('Memory Total Count(alive):', memory_count)
    ####处理存储storages  (配置raid和未配置raid)
    select_storages_total='/redfish/v1/Systems/1/storage'
    temp_storages_result1 = HPDL380G5.GetInfo(select_storages_total)
    #print ('temp_storages_result1',temp_storages_result1)
    if isinstance(temp_storages_result1, dict) and ('error' not in temp_storages_result1.keys()):
        #storages_raid_count = temp_storages_result1['Members@odata.count']
        if 'raid' in  temp_storages_result1:
            storages_raid_count = temp_storages_result1['Members@odata.count']
            print('@' *50)
            print('Storages Raidzone Count:', storages_raid_count) #'StorageControllers@odata.count'
            # 获取storages raidzonename的URLsuffix.
            #print('select_storages_raidzone_name_URLsuffix:', [x['@odata.id'] for x in temp_storages_result1['Members']])
            storages_single_URLsuffix_list = [x['@odata.id'] for x in temp_storages_result1['Members']]
            #print(storages_single_URLsuffix_list)    #raidzone的URLsuffix
            # 取出raidzone中磁盘的类型和大小
            for select_storages_raidzone_single in storages_single_URLsuffix_list:
                temp_storages_raiddisk_result2 = HPDL380G5.GetInfo(select_storages_raidzone_single)
                #print (temp_storages_raiddisk_result2)
                print ('@'*60)
                print ('raidzone name:',temp_storages_raiddisk_result2['Name'])
                print ('raidzone ID:',temp_storages_raiddisk_result2['Id'])
                print ('raidzone disk count:',temp_storages_raiddisk_result2['Drives@odata.count'])
                if isinstance(temp_storages_raiddisk_result2, dict) and ('error' not in temp_storages_raiddisk_result2.keys()):
                    storages_singledisk_URLsuffix_list = [x['@odata.id'] for x in temp_storages_raiddisk_result2['Drives']]
                    #print ('storages_singledisk-URLsuffix',storages_singledisk_URLsuffix_list)
                    for storages_singledisk in storages_singledisk_URLsuffix_list:
                        temp_storages_singledisk_result2 = HPDL380G5.GetInfo(storages_singledisk)
                        #print('temp_storages_singledisk_result2 :',temp_storages_singledisk_result2)
                        if isinstance(temp_storages_singledisk_result2, dict) and ('error' not in temp_storages_singledisk_result2.keys()):
                            print ('disk name：',temp_storages_singledisk_result2['Name'])
                            print ('disk ID：',temp_storages_singledisk_result2['Id'])
                            print ('disk CapacityBytes：',temp_storages_singledisk_result2['CapacityGB'])
                            print ('disk MediaType：',temp_storages_singledisk_result2['MediaType'])
        elif 'raid' not in temp_storages_result1:     ##未配置raid
            select_storages_total5 = '/redfish/v1/Systems/1/SmartStorage/ArrayControllers/0/DiskDrives'
            temp_storages_result5 = HPDL380G5.GetInfo(select_storages_total5)
            #print('temp_storages_result5', temp_storages_result5)
            storages_raid_count = temp_storages_result5['Members@odata.count']
            print('Not Raid, Disk Count:', storages_raid_count)
            if isinstance(temp_storages_result5, dict) and ('error' not in temp_storages_result5.keys()):
                disk_single_URLsuffix_list1 = [x['@odata.id'] for x in temp_storages_result5['Members']]
                for disk_single in disk_single_URLsuffix_list1:
                    single_disk_result3 = HPDL380G5.GetInfo(disk_single)
                    #print('single_disk_result3 :',single_disk_result3)
                    if isinstance(single_disk_result3, dict) and ( 'error' not in single_disk_result3.keys()):
                        print('disk name：', single_disk_result3['Name'])
                        print('disk ID：', single_disk_result3['Id'])
                        print('disk CapacityBytes：', single_disk_result3['CapacityGB'])
                        print('disk MediaType：', single_disk_result3['MediaType'])

    ##SEL日志处理
    select_event_log = '/redfish/v1/managers/1/logservices/iel/entries'
    ##"/redfish/v1/Systems/1/LogServices/iml/Actions/LogService.ClearLog/" ##清除
    event_log_result1 = HPDL380G5.GetInfo(select_event_log)
    # print ('event_log_result1',event_log_result1)
    if isinstance(event_log_result1, dict) and ('error' not in event_log_result1.keys()):
        print('event_log_result1',event_log_result1)

if __name__ == '__main__':
    Collect_Info('10.251.214.44', 'ydview', 'yd@sj1507')




