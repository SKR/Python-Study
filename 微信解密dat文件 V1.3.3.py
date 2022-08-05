# UTF-8  Python3.8
# TIME 2022-08-05 09:26
import os
import binascii
import datetime
import threading
import tkinter
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image,ImageTk
import windnd

#----------------------------------全局变量----------------------------------------------
dir_in=''      #输入目录
dir_out=''     #输出目录
caiyang_dir='' #采样文件路径
work_mode='default' #转换工作模式，默认为全部转换，day是按天建目录分类转换
#---------------------------------窗体调用函数------------------------------------------
def set_caiyang_dir():        #设置采样文件
    global caiyang_dir
    caiyang_dir = filedialog.askopenfilename()
    # caiyang_dir =caiyang_dir.replace('/', '\\')
    print(caiyang_dir)
    print(xor(caiyang_dir))


def get_in_dir():           #获取转换目录
    in_dir_entry.delete(0,END)
    global dir_in #filedialog.askdirectory()
    dir_in = filedialog.askdirectory()
    in_dir_entry.insert(0, dir_in)

def get_out_dir():         #获取输出目录
    out_dir_entry.delete(0, END)
    global dir_out #filedialog.askdirectory()
    dir_out = filedialog.askdirectory()
    out_dir_entry.insert(0, dir_out)

def get_dir_in(files):      #拖动获取转换目录
    in_dir_entry.delete(0, END)
    global dir_in
    msg ='\n'.join((item.decode('gbk') for item in files))
    if os.path.isdir(msg):  # 判断转换目录是否是目录
        dir_in =msg
        in_dir_entry.insert(0, msg.replace('\\', '/'))
        print(dir_in)
    else:
        tkinter.messagebox.showwarning('警告', '您拖动的不是一个目录，而是一个文件，请重新拖动选择“转换目录”！')


def get_dir_out(files):      #拖动获取输出目录
    out_dir_entry.delete(0, END)
    global dir_out
    msg ='\n'.join((item.decode('gbk') for item in files))
    if os.path.isdir(msg):  # 判断转换目录是否是目录
        dir_out =msg
        out_dir_entry.insert(0, msg.replace('\\', '/'))
        print(dir_out)
    else:
        tkinter.messagebox.showwarning('警告', '您拖动的不是一个目录，而是一个文件，请重新拖动选择“转换目录”！')

def open_dir():           #打开输出目录
    start_directory = dir_out
    open = opens_dir(start_directory)
    open.start()

def change_work_mode():   #更改工作模式，是按天分类转换，还是默认转换
    global work_mode
    if(work_mode == 'default'):
        work_mode = 'day'
    else:#(work_mode=='day'):
        work_mode = 'default'

    if(work_mode == 'default'):
        change_work_mode_button['text']='更改输出模式\n当前为 默认'
    elif(work_mode=='day'):
        change_work_mode_button['text']='更改输出模式\n当前为 按天'


def get_start_time():               #获取转换时间段，并开始转换
    global start_time
    global end_time
    start_time = start_time_entry.get()
    end_time = end_time_entry.get()
    if not start_time :
        start_time='2000-01-01 00:00:00'
    if not end_time :
        end_time='2060-12-31 23:59:59'
    if (not dir_in) or (not dir_out):
        start_button['text'] = '转换中'
        tkinter.messagebox.showwarning('警告', '您没有选择转换目录或者输出目录！！！')
        start_button['text'] = '开始转换'
    else:
        start_button['text'] = '转换中'
        Transform=transform(dir_in, start_time, end_time, dir_out)  #创建新线程用以启动转换程序
        Transform.start()                                 #转换程序线程启动
        # main(dir_in, start_time, end_time, dir_out)        #调用转换程序


class opens_dir(threading.Thread):          #定义多线程程序开文件目录类    调用系统打开文件目录
    def __init__(self,starts_directory):
        threading.Thread.__init__(self)
        # global starts_directory
        self.starts_directory=starts_directory
    def run(self):
        if self.starts_directory:
            starts_directory = self.starts_directory.replace('/', '\\')
            print(starts_directory)
            os.system("explorer.exe %s" % starts_directory)  # 调用os的文件管理器打开输出目录
            os.system("exit")  # 调用系统快速关闭命令行窗体显示
        else:
            tkinter.messagebox.showwarning('警告', '没有选择输出目录！！！')

#----------------------------------------解密实现-------------------------------------------
def getFilenum_dat(dir):                       #获取输入目录下文件个数
    number = 0
    for root, dirname, filenames in os.walk(dir):
        for filename in filenames:
            print(filename)
            if os.path.splitext(filename)[1] == '.dat':
                number += 1
    return number


def getFileList(path):                       #获得原文件位置目录并按照时间升序排列#
    dirLists = os.listdir(path)
    if not dirLists:
        return
    else:
        dirLists = sorted(dirLists,key=lambda f: os.path.getmtime(os.path.join(path, f)))
        print('文件数量：{}个\n最新文件名为<{}>'.format(len(dirLists),dirLists[-1]))
        return dirLists

def getFileHex(path,step_from,step_to):                    #获得输入目录文件指定位数十六进制数据，是整个目录里面取最新的文件
    fileName = getFileList(path)[-1]
    fileData = open(path+'/'+fileName,'rb')
    hexstr = binascii.b2a_hex(fileData.read())
    hex = str(hexstr)[step_from:step_to] #获取16进制前多少位，4或6位
    # print('dat十六进制文件头前{}位为:{}'.format(step,hex))
    return hex




def get_file_hex(file_dir,step_from,step_to):                               #获取指定文件的十六进制值
    fileData = open(file_dir, 'rb')
    hexstr = binascii.b2a_hex(fileData.read())
    hex = str(hexstr)[step_from:step_to]  # 获取16进制前多少位，4或6位
    print(hex)
    return hex

def xor(dir):                                             #获取指定文件的密匙
    global work_mode
    hex2_4 = int(get_file_hex(dir,2,4), 16)                 #16进制异或运算#
    hex4_6 = int(get_file_hex(dir,4,6), 16)
                                                        #先取前四位，再取前两位，运算结果一致才算获得解密偏移量#
    jpg = int('ffd8', 16)        # jpeg文件头16进制为ffd8ff
    png = int('8950', 16)        # png文件头16进制为89504E47
    gif = int('4749', 16)        # gif文件头16进制为47494638


    if(hex(hex2_4 ^ int(hex(jpg)[2:4],16)) == hex(hex4_6 ^ int(hex(jpg)[4:6],16))):     #判断文件类型
        print("选中文件为jpg")
        return hex(hex2_4 ^ int(hex(jpg)[2:4],16))
    if(hex(hex2_4 ^ int(hex(png)[2:4],16)) == hex(hex4_6^int(hex(png)[4:6],16))):
        print("选中文件为png")
        return hex(hex2_4 ^ int(hex(png)[2:4],16))
    if(hex(hex2_4 ^ int(hex(gif)[2:4],16)) == hex(hex4_6 ^ int(hex(gif)[4:6],16))):
        print("选中文件为gif")
        return hex(hex2_4 ^ int(hex(gif)[2:4],16))
    else:
        tkinter.messagebox.showwarning('警告', '您设置的转换采样文件有误，请重新选择！！！')



def Xor(dir):                                            #获取输入目录下采密匙
    global work_mode
    hex2_4 = int(getFileHex(dir,2,4), 16)                  #16进制异或运算#
    hex4_6 = int(getFileHex(dir,4,6), 16)
                                                        #先取前四位，再取前两位，运算结果一致才算获得解密偏移量#
    jpg = int('ffd8', 16)        # jpeg文件头16进制为ffd8ff
    png = int('8950', 16)        # png文件头16进制为89504E47
    gif = int('4749', 16)        # gif文件头16进制为47494638

    if (hex(hex2_4 ^ int(hex(jpg)[2:4], 16)) == hex(hex4_6 ^ int(hex(jpg)[4:6], 16))):  #判断文件类型
        print("默认文件为jpg")
        return hex(hex2_4 ^ int(hex(jpg)[2:4], 16))
    if (hex(hex2_4 ^ int(hex(png)[2:4], 16)) == hex(hex4_6 ^ int(hex(png)[4:6], 16))):
        print("默认文件为png")
        return hex(hex2_4 ^ int(hex(png)[2:4], 16))
    if (hex(hex2_4 ^ int(hex(gif)[2:4], 16)) == hex(hex4_6 ^ int(hex(gif)[4:6], 16))):
        print("默认文件为gif")
        return hex(hex2_4 ^ int(hex(gif)[2:4], 16))
    else:
        dt = datetime.datetime.now()
        dt = dt.strftime('%Y-%m-%d %H:%M:%S')
        detail_list.insert(END, '[' + dt + ']' + '  ''转换错误！！！\n')
        tkinter.messagebox.showwarning('警告', '默认文件有误，请点击“设置采样文件”，设置好采样文件，再进行转换！！！')
        start_button['text'] = '开始转换'



def is_img(step,dir):          #判断是否为图片文件

    fileData = open(dir,'rb')
    hexstr = binascii.b2a_hex(fileData.read())
    hex = str(hexstr)[2:4] #获取16进制前多少位，4或6位
    print('当前dat十六进制文件头前2位为:{}'.format(hex))


    hex_2 = int(hex,16)

    if(hex_2 ^ step ==int('ff',16) or hex_2 ^ step ==int('89',16) or hex_2 ^ step ==int('47',16)  ):
        return True
    else:
        return False

def convertImg(file,fileName,step,file_out):                #写入图片文件#
    dat = open(file, "rb")
    out=file_out+'/'+fileName + '.jpg'
    newFile = open(out, "wb")

    for cur in dat:
        for hex in cur:
            originHex = hex ^ step
            newFile.write(bytes([originHex]))

    dat.close()
    newFile.close()
    print('转换完成文件：{}'.format(out))


def main(dir,date1,date2,file_out):               #转换主程序
    global caiyang_dir
    dt = datetime.datetime.now()
    dt = dt.strftime('%Y-%m-%d %H:%M:%S')
    detail_list.insert(END, '[' + dt + ']' + '  ''转换中.......\n')
    files = os.listdir(dir)
    format_ = '%Y-%m-%d %H:%M:%S'      #时间字符串格式
    if(caiyang_dir):
        step = int(xor(caiyang_dir), 16)
        print("使用的采集文件：{}".format(caiyang_dir))
    else:
        step = int(Xor(dir),16)
        print("使用的采集文件：{}".format(dir))
    print('十进制偏移量为{}'.format(step))
    i = 0
    for fn in files:                 #遍历输入目录文件
        _path = dir + '/' + fn
        _time = os.path.getmtime(_path)
        dt_time = datetime.datetime.fromtimestamp(_time).strftime(format_)  #文件时间戳转字符串
        print(_path)

        if dt_time < date1 or dt_time > date2:
            continue

        if not os.path.isdir(_path):
            if(is_img(step,_path)):
                print('当前文件: {}' .format(_path))
                convertImg(_path,fn,step,file_out)
                i+=1
            else:
                detail_list.insert(END, '[' + dt + ']' + '  ''文件出错：{}\n'.format(fn))
    dt = datetime.datetime.now()
    dt = dt.strftime('%Y-%m-%d %H:%M:%S')
    detail_list.insert(END, '[' + dt + ']' + '  ''本次转换文件数量：{}个\n'.format(i))
    tkinter.messagebox.showinfo('转换完成', '转换完成，共转换{}个文件'.format(i))  # 转换完成后提示
    # print('总计转换图片文件{}个'.format(i))


def main_day(dir,date1,date2,file_out):               #按照天转换主程序
    global caiyang_dir
    dt = datetime.datetime.now()
    dt = dt.strftime('%Y-%m-%d %H:%M:%S')
    detail_list.insert(END, '[' + dt + ']' + '  ''转换中.......\n')
    files = os.listdir(dir)
    format_ = '%Y-%m-%d'      #时间字符串格式
    if(caiyang_dir):
        step = int(xor(caiyang_dir), 16)
        print("使用的采集文件：{}".format(caiyang_dir))
    else:
        step = int(Xor(dir),16)
        print("使用的采集文件：{}".format(dir))
    print('十进制偏移量为{}'.format(step))
    i = 0
    for fn in files:                 #遍历输入目录文件
        _path = dir + '/' + fn
        _time = os.path.getmtime(_path)
        dt_time = datetime.date.fromtimestamp(_time).strftime(format_)  #文件时间戳转字符串
        print(_path)

        if dt_time < date1 or dt_time > date2:
            continue

        if not os.path.isdir(_path):
            if(is_img(step,_path)):       #判断是否是3种图片
                print('当前文件: {}' .format(_path))
                file_out_dir=file_out+'/'+dt_time
                if(not os.path.exists(file_out_dir)):
                    os.mkdir(file_out_dir)
                convertImg(_path,fn,step,file_out_dir)
                i+=1
            else:
                detail_list.insert(END, '[' + dt + ']' + '  ''文件出错：{}\n'.format(fn))
    dt = datetime.datetime.now()
    dt = dt.strftime('%Y-%m-%d %H:%M:%S')
    detail_list.insert(END, '[' + dt + ']' + '  ''本次转换文件数量：{}个\n'.format(i))
    tkinter.messagebox.showinfo('转换完成', '转换完成，共转换{}个文件'.format(i))  # 转换完成后提示
    # print('总计转换图片文件{}个'.format(i))

class transform(threading.Thread):               #多线程启用转换程序，从而不影响主程序  多线程转换程序
    def __init__(self,dir,date1,date2,file_out):
        threading.Thread.__init__(self)
        global pdir
        global pdate1
        global pdate2
        global pfile_out
        pdir=dir
        pdate1=date1
        pdate2=date2
        pfile_out=file_out
    def run(self):
        if any((name.endswith('.dat')) for name in os.listdir(pdir)):
            if(work_mode=='default'):
                main(pdir,pdate1,pdate2,pfile_out)
            elif(work_mode=='day'):
                main_day(pdir, pdate1, pdate2, pfile_out)
            start_button['text'] = '开始转换'
        else:
            start_button['text'] = '开始转换'
            tkinter.messagebox.showwarning('警告', '所选文件夹内没有DAT文件或者目录选择错误，请重新选择“转换目录”！')

#----------------------------------窗体菜单栏调用函数-------------------------------------------------
def how_messagebox():
    tkinter.messagebox.showinfo('使用说明', '注意：\n    （1）本软件可将PC端微信加密的图片（dat文件）转换成可被打开的图片格式。\n    （2）一次转换只能转换同微信一ID的文件，因为微信不同ID所使用的加密密匙不同。\n    '
                                        '（3）设置好“转换目录”和“输出目录”，时间筛选选填，点击“开始转换”按钮，软件会自动识别文件类型，无需手动选择。\n    '
                                        '（4）如果自动转换出错，此时需要手动选择采样文件，点击“设置采样dat文件”按钮，选择合适的dat的文件，再次执行转换即可。\n\n  (微信文件目录为C:\\Users\\***(系统账户名字)\\Documents\\WeChat Files\\******(微信号)\\FileStorage\\Image\\(日期))\n\n'
                                        '注：最新版本微信目录可能为C:\\Users\\***(系统账户名字)\\Documents\\WeChat Files\\******(微信号)\\FileStorage\\MsgAttach\\****(一长串没有规律的字母加数字的组合)\\Image\\(日期)')

def communication_messagebox():          #联系作者
    branch1 = Toplevel()
    branch1.geometry('450x265+' + str(screen_center_width) + '+' + str(screen_center_height + 40))  # 长x高 x坐标 y坐标  初始值455x450+533+155
    branch1.title('联系作者')
    branch1.resizable(0,0)
    path1 = os.getcwd() + '\\' + 'data' + '\\' + 'QQ.dat'
    global photo1,photo2
    image1 = Image.open(path1)
    photo1 = ImageTk.PhotoImage(image1)
    photo = Label(branch1, image=photo1)
    photo.place(height=225, width=200, x=18, y=20)

    path2=os.getcwd()+'\\'+'data'+'\\'+'Wechat.dat'
    image2 = Image.open(path2)
    photo2 = ImageTk.PhotoImage(image2)
    _photo = Label(branch1, image=photo2)
    _photo.place(height=225, width=200, x=232, y=20)





def donation_messagebox():          #支持作者
    branch1 = Toplevel()
    branch1.geometry('450x265+' + str(screen_center_width) + '+' + str(screen_center_height + 40))  # 长x高 x坐标 y坐标  初始值455x450+533+155
    branch1.title('支持作者')
    branch1.resizable(0,0)
    path1 = os.getcwd() + '\\' + 'data' + '\\' + 'Alipay.dat'
    global photo1,photo2
    image1 = Image.open(path1)
    photo1 = ImageTk.PhotoImage(image1)
    photo = Label(branch1, image=photo1)
    photo.place(height=225, width=200, x=18, y=20)

    path2=os.getcwd()+'\\'+'data'+'\\'+'Wechatpay.dat'
    image2 = Image.open(path2)
    photo2 = ImageTk.PhotoImage(image2)
    _photo = Label(branch1, image=photo2)
    _photo.place(height=225, width=200, x=232, y=20)  #默认参数 height=225, width=200, x=232, y=20
    #tkinter.messagebox.showinfo('捐赠', '如果您觉得好用的话，不妨支持一下开发者！\n\t')

def about_messagebox():
    tkinter.messagebox.showinfo('关于软件', '本软件由本人制作，本软件永久免费，严禁倒卖!\n'
                                      '\t本项目已经开源至Github\n'
                                      '开源地址：https://github.com/SKR/Python-Study\n'
                                      '软件版本：1.3.3\n'
                                      '编译时间：2022年8月4日 22时29分25秒\n\n'
                                      '\t©Powered by Jiang\n')

def author_messagebox():
    tkinter.messagebox.showinfo('关于作者', '作者是一名即将入学的普通的研一新生！')

def thanks_messagebox():
    tkinter.messagebox.showinfo('致谢', '感谢  “ 叶元 ”老哥，提供了一些文件样本，使得小程序更加完善！\n'
                                       '感谢  “夜猫舰长”小姐姐，反馈的使用体验信息！')

def clear_rubbish():
    path= os.getcwd() + '\\' + 'bat' + '\\' + '清理系统垃圾.bat'
    class clear_rubbish(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
        def run(self):
            tkinter.messagebox.showinfo('清理垃圾', '点击确认开始清理')
            os.system(path)
            tkinter.messagebox.showinfo('清理垃圾', '清理完成！')
    C1=clear_rubbish()
    C1.start()

def update_messagebox():
    tkinter.messagebox.showinfo('1.3.3版本更新说明', '（1）新增  针对不同格式jpg、png、gif加密文件的支持。\n'
                                               '（2）优化  自动识别文件类型\n'
                                               '（3）增加  输出按天分类转换\n'
                                               '（4）修复  选择文件夹内没有DAT文件时候的提示，提升使用体验\n'
                                               '（5）完善  拖动获取转换目录、输出目录功能'
                                               '（6）修复  已知BUG\n ')


#--------------------------------------GUI主窗体--------------------------------------------------

root=Tk()

#----------------------------------------获取屏幕居中坐标-------------------------------------------
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
screen_center_width = round((screen_width-455)/2)
screen_center_height =round((screen_height-500)/2)

# windnd.hook_dropfiles(root,func=get_dir_in)
root.geometry('455x500+' + str(screen_center_width) + '+' + str(screen_center_height))   # 长x高 x坐标 y坐标  初始值455x460+533+155  第二值455x500
root.title('微信dat转图片转换器 v1.3.2 ©Powered by Jiang')
root.resizable(0,0)

#---------------------------------------输入控件--------------------------------------------------
in_dir_button=Button(root,text='选择转换文件夹',font=('微软雅黑',10),command=get_in_dir)
in_dir_button.place(height=30,width=110,x=330,y=40)
in_dir_lab=Label(root,text='请选择转换目录',font=('微软雅黑',9))
in_dir_lab.place(x=10,y=19)
in_dir_tips_lab=Label(root,text='提示：可以将文件夹直接拖进框里！',font=('微软雅黑',9))
in_dir_tips_lab.place(x=120,y=19)
in_dir_entry=Entry(root,font=('微软雅黑',9))
in_dir_entry.place(height=30,width=300,x=10,y=40)
windnd.hook_dropfiles(in_dir_entry,func=get_dir_in)

#--------------------------------------开始时间窗口--------------------------------------------------

start_time_lab=Label(root,text='请输入转换文件的开始日期',font=('微软雅黑',10))
start_time_lab.place(x=15,y=170)
start_time_entry=Entry(root,font=('微软雅黑',10))
start_time_entry.place(height=30,width=140,x=26,y=200)


#----------------------------------------输出控件----------------------------------------------------
out_dir_button=Button(root,text='选择输出文件夹',font=('微软雅黑',10),command=get_out_dir)
out_dir_button.place(height=30,width=110,x=330,y=115)
out_dir_lab=Label(root,text='请选择输出目录',font=('微软雅黑',9))
out_dir_lab.place(x=10,y=93)
out_dir_entry=Entry(root,font=('微软雅黑',9))
out_dir_entry.place(height=30,width=300,x=10,y=115)
windnd.hook_dropfiles(out_dir_entry,func=get_dir_out)

#-----------------------------------------结束时间---------------------------------------------------
end_time_lab=Label(root,text='请输入转换文件的结束日期',font=('微软雅黑',10))
end_time_lab.place(x=280,y=170)
end_time_entry=Entry(root,font=('微软雅黑',10))
end_time_entry.place(height=30,width=140,x=290,y=200)

R_time_lab=Label(root,text='~',font=('微软雅黑',30))
R_time_lab.place(x=210,y=180)

#-------------------------------------------时间格式小提示-----------------------------------------------------
tips1_time_lab=Label(root,text='时间例如“2020-01-01 08:02:03”',font=('微软雅黑',10))
tips1_time_lab.place(x=120,y=235)

tips2_time_lab=Label(root,text='提示：不填时间将全部转换，一定将前边的‘0’写上，否则无法正确筛选',font=('微软雅黑',9))
tips2_time_lab.place(x=30,y=260)

tips3_lab=Label(root,text='（警告：输出目录不能为转换目录的子目录）',font=('微软雅黑',8),foreground ='red')
tips3_lab.place(x=100,y=93)

#--------------------------------------------开始按钮控件------------------------------------------------------
start_button=Button(root,text='开始转换',font=('微软雅黑',10),command=get_start_time)
start_button.place(height=40,width=70,x=186,y=293)

open_dir_button=Button(root,text='打开输出目录',font=('微软雅黑',10),command=open_dir)
open_dir_button.place(height=30,width=90,x=260,y=299)

change_work_mode_button=Button(root,text='更改输出模式\n当前为 默认',font=('微软雅黑',9),command=change_work_mode)
change_work_mode_button.place(height=40,width=90,x=90,y=293)

open_dir_button=Button(root,text='设置采样dat文件',font=('微软雅黑',9),command=set_caiyang_dir)
open_dir_button.place(height=24,width=110,x=330,y=12)
#--------------------------------------------显示细节---------------------------------------------------------

detail_list_frame=LabelFrame(root,text='转换记录',font=('微软雅黑',10))
detail_list_frame.place(height=160,width=440,x=8,y=334)  #y=334

detail_list=Listbox(root)
detail_list.place(height=131,width=430,x=12,y=354)#y=354

detail_list_scrollbar=Scrollbar(detail_list)
detail_list_scrollbar.pack(side=RIGHT,fill=BOTH)
detail_list_scrollbar.config(command=detail_list.yview)
detail_list.config(yscrollcommand=detail_list_scrollbar.set)
dt = datetime.datetime.now()
dt = dt.strftime('%Y-%m-%d %H:%M:%S')
detail_list.insert(END, '[' + dt + ']' + '  系统初始化完成，端口：8484 ')

#--------------------------------------------窗体菜单栏--------------------------------------------------------
m1=Menu(root)
menu_menu1=Menu(m1)
menu_menu2=Menu(m1)
menu_menu3=Menu(m1)

menu_menu1.add_command(label='使用说明(U)', command=how_messagebox)
menu_menu1.add_command(label='联系作者(C)', command=communication_messagebox)
menu_menu1.add_command(label='支持作者(D)', command=donation_messagebox)
menu_menu1.add_command(label='关于软件(A)',command=about_messagebox)
menu_menu1.add_separator()        #添加分割线
menu_menu1.add_command(label='退出(X)',command=root.quit)

menu_menu2.add_command(label='清理系统垃圾(C)',command=clear_rubbish)

menu_menu3.add_command(label= '更新说明(U)',command=update_messagebox)
menu_menu3.add_command(label= '关于作者(A)',command=author_messagebox)
menu_menu3.add_command(label= '致谢(T)',command=thanks_messagebox)

m1.add_cascade(label='菜单(M)',menu = menu_menu1)
m1.add_cascade(label='工具箱(T)',menu =menu_menu2 )
m1.add_cascade(label='关于(A)',menu =menu_menu3 )

root['menu']=m1

#-----------------------------主方法-----------------------------
if __name__=="__main__":

    root.mainloop()
