import datetime
import win32com.client
import os
import WebSphere
import AML


def call_marco():
    print('开始数据清洗...')
    path = os.getcwd()
    xl = win32com.client.Dispatch('Excel.Application')
    xl.visible = 0
    xlbook = xl.Workbooks.Open(path + '\Bin\VBA.xlsm')
    xl.Application.Run('VBA.xlsm!模块1.Data_Cleaning')    # xl.ExecuteExcel4Macro()执行带参数的过程
    print('清洗完成，开始入库...')
    xl.Application.Run('VBA.xlsm!模块1.Import_WebSphere')
    #       xl.Application.Run('VBA.xlsm!模块1.Import_AML')
    xlbook.Close()
    del xl


def impt_web_days(ystday, process_dict, orgid_dict):
    userPwd = 'password'
    finished = {}

    for userid in process_dict.keys():
        islogin = 1
        loginweb = WebSphere.login(userid, userPwd)
        if loginweb == 200:
            print('登录成功!')
        else:
            print('登录不成功，程序终止!')
            islogin = 0
        for data_name in process_dict[userid]:
                search_dat = WebSphere.search(data_name, orgid_dict[userid], ystday, ystday)
                if not search_dat[2]:
                    print(ystday + '无数据')
                    continue
                text = WebSphere.batch_download(data_name, search_dat[0], search_dat[1], search_dat[2])
                WebSphere.store(text, orgid_dict[userid], data_name, ystday)
                finished[userid].append(data_name)
        WebSphere.login_off()
    return finished, islogin


def impt_aml_days(ystday,sysids):
    islogin = 1
    loginaml = AML.login()
    if loginaml == 200:
        print('登录成功!')
    else:
        print('登录不成功，程序终止!')
        islogin = 0
    check = []
    for sysid in sysids:
        san_list = AML.getlist(ystday, ystday, sysid)
        if san_list['total'] == 0:
            check.append(sysid)
            print(sysid + '***'+str(ystday) + '***无业务发生')
            continue
        print(sysid + '***' + str(ystday) + '***' + str(san_list['total']) + '笔案例,开始抓取...')
        case_rows = []
        black_rows = []
        i = 0
        while i <= len(san_list['rows'])-1:
            caseid = san_list['rows'][i]['CAD_CASEID']
            case_info = AML.getcase(caseid, sysid, i)
            case_rows.append(case_info[0])
            black_rows.append(case_info[1])
            i = i + 1
            #print(i)
        print('抓取' + sysid + '案例完成,开始写入文件...')
        AML.store(ystday, sysid, black_rows, case_rows)
    AML.login_off()
    return check, islogin


def main():
    ystday = datetime.date.today() + datetime.timedelta(-1)
    ystday = str(ystday.strftime('%Y%m%d'))
    aml_sysids = ['BANCS', 'CIPSS']     # BANCS(汇出-GX)，BANCS(汇入-HQ),BCIPS(汇出-GX),BCIPS(汇入-HQ),RCPS(汇入-GX
    process_dict = {
                    'QS021ZG': ['PYID0030', 'PYID0040', 'PYID0280'],
                    'zh01': ['PYID0040', 'PYID0280']
                    }
    orgid_dict = {'QS021ZG': '', 'zh01': '00350'}
    impt_web_days(ystday, process_dict, orgid_dict)
    impt_aml_days(ystday, aml_sysids)
    call_marco()


if __name__ == '__main__':
    main()
