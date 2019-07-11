"""通过端口号查杀对应程序
   author: yufei
   date: 2019-05-09
"""
from tkinter import *
import tkinter.messagebox as messagebox
from tkinter import ttk
import os
import re


class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()
        # 设置窗口标题:
        self.master.title('端口查杀程序')
        width = 700
        height = 450
        screenwidth = self.master.winfo_screenwidth()
        screenheight = self.master.winfo_screenheight()
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.master.geometry(size)

    # 创建组件
    def createWidgets(self):
        fr1 = Frame(self, pady=6)
        fr2 = Frame(self, pady=6)
        fr1.pack(side='top')
        fr2.pack(side='bottom', expand=YES, fill=BOTH)
        self.label = Label(fr1, text='端口号/程序名:')
        self.label.pack(side=LEFT, padx=3)
        self.port_input = Entry(fr1)
        self.port_input.pack(side=LEFT, padx=6)
        self.alert_button = Button(fr1, text='查询', width=6, command=self.search)
        self.alert_button.pack(side=LEFT, padx=6)
        self.kill_button = Button(fr1, text='关闭程序', width=10, command=self.kill)
        self.kill_button.pack(side=LEFT, padx=6)
        self.search_and_kill_utton = Button(fr1, text='一键查杀', width=10, command=self.search_kill)
        self.search_and_kill_utton.pack(side=LEFT, padx=6)
        self.with_name = BooleanVar()
        self.with_name_check = Checkbutton(fr1, text='同名称一并关闭', variable=self.with_name)
        self.with_name_check.pack(side=LEFT, padx=6)
        columns = ("id", "name", "pid")
        self.table = ttk.Treeview(fr2, show="headings", height=17, columns=columns)
        self.table.column("id", width=60, anchor='center')  # 表示列,不显示
        self.table.column("name", width=350, anchor='center')  # 表示列,不显示
        self.table.column("pid", width=200, anchor='center')
        self.table.heading("id", text="序号")  # 显示表头
        self.table.heading("name", text="程序名称")  # 显示表头
        self.table.heading("pid", text="进程号")
        self.table.pack(side=LEFT, expand=YES, fill=BOTH)

    ## 查找端口的pid
    def find_pro(self):
        find_port = 'netstat -aon | findstr %s' % self.port_input.get()
        result = os.popen(find_port)
        text = result.read()
        datalist = text.strip().split('\n')

        # print(datalist)
        datalist = list(filter(self.is_real, datalist))
        datalist = map(self.getPid, datalist)
        datalist = self.getDetail(set(datalist))
        print(datalist)
        return datalist

    # 通过程序名称查询明细
    def find_by_name(self):
        l = []
        count = 0
        name = self.port_input.get()
        index_start = name.rfind('.')
        if index_start == -1:
            name += '.exe'
        find_pro = 'tasklist -fi "imagename eq %s"' % name
        result = os.popen(find_pro)
        text = result.read()
        datalist2 = text.strip().split('\n')
        print(datalist2)
        for m in datalist2:
            itemList = re.split(r'\s+', m.strip())
            if len(itemList) >= 4 and itemList[0] == name:
                count = count + 1
                l.append({'id': str(count), 'name': itemList[0], 'pid': itemList[1]})

        return l

    # 查询进程明细
    def getDetail(self, datalist):
        l = []
        count = 0
        for i in datalist:
            # find_pro = 'tasklist|findstr %s' % i
            find_pro = 'tasklist -fi "pid eq %s"' % i
            result = os.popen(find_pro)
            text = result.read()
            datalist2 = text.strip().split('\n')
            print(datalist2)
            for m in datalist2:
                itemList = re.split(r'\s+', m.strip())
                if len(itemList) >= 4 and itemList[1] == i:
                    count = count + 1
                    l.append({'id': str(count), 'name': itemList[0], 'pid': itemList[1]})
        return l

    # 查询pid
    def getPid(self, item):
        itemList = re.split(r'\s+', item.strip())
        if len(itemList) >= 5:
            return itemList[4]
        return ''

    # 过滤指定端口程序
    def is_real(self, item):
        itemList = re.split(r'\s+', item.strip())
        if len(itemList) >= 5:
            index_start = itemList[1].rfind(':')
            if index_start != -1 and index_start + 1 < len(itemList[1]) and itemList[1][index_start + 1:len(
                    itemList[1])] == self.port_input.get():
                return True
        return False

    # 通过程序名杀进程
    def kill_pro_by_name(self, name):
        # 占用端口的pid
        find_kill = 'taskkill -f -im %s' % name
        print(find_kill)
        result = os.popen(find_kill)
        return result.read()

    # 通过pid杀进程
    def kill_pro(self, pid, name):
        # 占用端口的pid
        find_kill = 'taskkill -f -pid %s' % pid
        if self.with_name.get() == True:
            find_kill = 'taskkill -f -im %s' % name
        print(find_kill)
        result = os.popen(find_kill)
        return result.read()
        # os.popen('kill -9 {0}'.format(int(pid)))

        # for i in range(len(out)):
        #     print(out[i][3])

    # 清除界面数据
    def clear_table(self):
        x = self.table.get_children()
        for item in x:
            self.table.delete(item)

    # 通过端口查询并展示
    def search(self):
        port = self.port_input.get()
        datalist = []
        if port == '':
            messagebox.showinfo('信息', '请输入端口号或程序名称')
            return
        elif port.isnumeric():
            datalist = self.find_pro()
        else:
            datalist = self.find_by_name()
        # 刷新页面
        self.clear_table()

        for i in datalist:
            self.table.insert('', 'end', values=[i['id'], i['name'], i['pid']])

    # 查杀指定行程序
    def kill(self):
        l = self.table.selection()
        if len(l) > 0:
            item_text = self.table.item(l[0], "values")
            print(item_text[2])  # 输出所选行的第3列的值
            re = self.kill_pro(item_text[2], item_text[1])
            print(re)
            messagebox.showinfo('信息', re)
            self.search()
        else:
            messagebox.showinfo('信息', '请选择程序')

    # 一键查杀
    def search_kill(self):
        port = self.port_input.get()
        datalist = []
        re = ''
        if port == '':
            messagebox.showinfo('信息', '请输入端口号或程序名称')
            return
        elif port.isnumeric():
            # 通过pid
            datalist = self.find_pro()
            if len(datalist) > 0:
                re = self.kill_pro(datalist[0]['pid'], datalist[0]['name'])
                print(re)
        else:
            # 通过程序名
            datalist = self.find_by_name()
            if len(datalist) > 0:
                re = self.kill_pro_by_name(datalist[0]['name'])
                print(re)

        # 刷新页面
        self.clear_table()
        messagebox.showinfo('信息', re)


if __name__ == '__main__':
    app = Application()
    # 主消息循环:
    app.mainloop()
