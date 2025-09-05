import io
import os
import random
import shutil
import time
import subprocess


class SysOperation():

    def popen_cmd(self,cmd, buffering=-1):
        if not isinstance(cmd, str):  # 判断输入谁否为字符串，不是则报错
            raise TypeError("invalid cmd type (%s, expected string)" % type(cmd))
        if buffering == 0 or buffering is None:  # 判断缓冲区大小是否为0和空，是则报错
            raise ValueError("popen() does not support unbuffered streams")
        proc = subprocess.Popen(cmd,  # 输入的cmd命令
                                shell=True,  # 通过操作系统的 shell 执行指定的命令
                                stdout=subprocess.PIPE,  # 将结果标准输出
                                bufsize=buffering)  # -1，使用系统默认的缓冲区大小
        print(f'CMD命令：{cmd} --执行成功')
        return os._wrap_close(io.TextIOWrapper(proc.stdout), proc)  # 返回执行结果对象

    def newFilename(self, filename):
        '''生成新的文件名'''
        list_f = filename.split(".")
        str1 = list_f[0]
        str2 = list_f[1]
        ranStr = random.sample('abcdefghijklmnopqrstuvwxyz', 4)
        str3 = "".join(ranStr)
        newfilename = str1 + str3 + "." + str2
        print("生成的新字符串为：%s"%newfilename)
        return newfilename

    def file_add(self,path2,filename,opt=1,concent=None):
        '''新建文件'''
        cmd1 = path2[:2]
        if opt ==1:
            self.popen_cmd("%s & cd %s & type nul > %s"%(cmd1,path2,filename))
            print("空文件新建执行完成，文件：%s"%filename)
        elif opt ==2:
            self.popen_cmd("%s & cd %s & echo %s > %s"%(cmd1,path2,concent,filename))
            print("内容文件新建执行完成，文件：%s"%filename)

    def open_file(self,path):
        '''打开文件并关闭'''
        try:
            os.startfile(path)
        except:
            subprocess.Popen(['xdg-open',path])

    def file_copy(self,filepath,path):
        '''文件复制'''
        try:
            copypath = shutil.copy(filepath,path)
            print("文件复制成功，路径：%s"%copypath)
            return copypath
        except Exception as e:
            print("文件复制失败")
            print(e)

    def file_cut(self,filepath,path):
        '''文件剪切'''
        try:
            copypath = shutil.move(filepath,path)
            print("文件剪切成功，路径：%s"%copypath)
            return copypath
        except Exception as e:
            print("文件剪切失败")
            raise e

    def file_all_dele(self,path):
        '''删除所有文件'''
        for filename in os.listdir(path):
            os.unlink(path+"\\"+filename)
        print("所有文件删除成功，路径：%s" % path)

    def start_process(self,process):
        '''开启windows进程'''
        self.popen_cmd("start %s"%process)
        print("进程开启：%s"%process)

    def close_process(self,process,isforce = False):
        '''关闭windows进程'''
        if isforce == False:
            self.popen_cmd("taskkill /t /im %s"%process)
            print("关闭进程，进程：%s"%process)
        elif isforce == True:
            self.popen_cmd("taskkill /f /t /im %s"%process)
            print("强制关闭进程，进程：%s"%process)


if __name__ == "__main__":
    ''''''
    sys = SysOperation()
    a = sys.popen_cmd("dir")
    print(a.read())