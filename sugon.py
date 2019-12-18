import requests
requests.packages.urllib3.disable_warnings()

class GetHostInfo(object):
    def __init__(self,ipaddr,username,password):
        self.username=username
        self.password=password
        self.URLprefix='http://' + ipaddr.strip()
        global token    ##同时存在4-5个token链接，每个token链接时间为5分钟，可以自己设置。
        global cookie
        token=0
        cookie=0
        tokenurl=self.URLprefix+'/api/session'
        print(tokenurl)
        data={
            "username":self.username,
            "password":self.password
            }
        re1=requests.post(tokenurl,data=data,verify=False)
        print (re1.status_code)
        if re1.status_code == 200:
            #print (re1.json())
            # print(re1.status_code)
            # print(re1.json())
            # print('header:', re1.headers)
            # temp = re1.json()
            # print(temp['CSRFToken'])
            #print(re1.headers)
            #print (re1.json())
            temp_header=re1.headers
            cookie=temp_header['Set-Cookie']
            temp_token=re1.json()
            token=temp_token['CSRFToken']
            print (cookie)
            print (token)
        else:
            pass
    def GetInfo(self,URL_suffix):  #定义总获取函数，传参url的后半部分。如'/redfish/v1/Systems/1/Memory'
        urlset=self.URLprefix + URL_suffix.strip()
        #print(urlset)
        # print ('token:',token)
        # print ('cookie:',cookie)
        if cookie != 0  and token != 0 :
            header = {
                "Content-Type":"application/json,text/javascript",
                'X-Requested-With':'XMLHttpRequest',
                "X-CSRFTOKEN":token,
                "Cookie":cookie
                }
            re1=requests.get(urlset,headers=header,verify=False)
            print(re1.status_code)
            return (re1.json())
        else:
            pass

def Collect_Info(ipaddr,username,password):
    SuGon=GetHostInfo(ipaddr,username,password)
    ####处理CPU
    select_cpu_total = '/api/serverrepo/cpus'
    #print('cpu_total', SuGon.GetInfo(select_cpu_total))
    temp_cpu_result1= SuGon.GetInfo(select_cpu_total)
    if isinstance(temp_cpu_result1,list) :
        cpu_count = len(temp_cpu_result1)
        print('@' * 50)
        print('CPU Count:', cpu_count)
        for cpu_single in temp_cpu_result1:
            if isinstance(cpu_single, dict):
                print('CPU single name：',cpu_single['Location'])
                print('CPU single ID：',cpu_single['id'])
                print('CPU single TotalCores(cpus):', cpu_single['CoreThread'])
                print('CPU single Model(cpus):', cpu_single['BrandName'])
    ####处理内存
    select_mem_total = '/api/serverrepo/mems'
    # print('mem_total', SuGon.GetInfo(select_mem_total))
    temp_mem_result1 = SuGon.GetInfo(select_mem_total)
    memory_count=0
    if isinstance(temp_mem_result1, list):
        mem_count = len(temp_mem_result1)
        print('@' * 50)
        print('Memory Count(exist):', mem_count)
        for mem_single in temp_mem_result1:
            if isinstance(mem_single, dict):
                Memory_Size = mem_single['Size']
                #print ('Memory_Size AAAAA',Memory_Size)
                if Memory_Size:
                    memory_count+=1
                    print('Memory name:', mem_single['Location'])
                    print('Memory ID:', mem_single['id'])
                    print('Memory Size:', Memory_Size)
                    print('Memory Type:', mem_single['DimmType'])
                else:
                    pass
    print('Memory Count(alive):', memory_count)
    ####处理存储,无raid的查询
    select_storage_total = '/api/serverrepo/hdds'
    # print('storage_total', SuGon.GetInfo(select_storage_total))
    temp_storage_result1 = SuGon.GetInfo(select_storage_total)
    if isinstance(temp_storage_result1, list):
        mem_count = len(temp_storage_result1)
        print('@' * 50)
        print('Storage Count:', mem_count)
        for storage_single in temp_storage_result1:
            if isinstance(storage_single, dict):
                print('Storage name:', storage_single['Location'])
                print('Storage ID:', storage_single['id'])
                print('Storage Size:', storage_single['Size'])
                print('Storage Type:', storage_single['Mode'])
    ##处理日志
    selecteventlog = '/api/logs/eventlog'  ##post
    selectselinfo = '/api/logs/selinfo'  ##get
    print('selectselinfo', SuGon.GetInfo(selectselinfo))
    print('selecteventlog', SuGon.GetInfo(selecteventlog))

if __name__ == '__main__':
    Collect_Info('10.249.177.29', 'username', 'password')


