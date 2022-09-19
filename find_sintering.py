import os
import pandas as pd
import numpy as np
import math as math
import warnings
import re
warnings.filterwarnings("ignore")
##------------------------------------------------------------
def findI(files):#查找文件中是否还包含文件头
    str = "ITEM:"
    files = os.listdir(files)#创建路径下所有文件的列表
    files.sort(key = lambda x: int(re.findall('\d+', x)[1]))#按照数字大小排序
    for file in files:
        file = filepath + '/'+ file
        with open(file, 'r', encoding = 'utf-8') as d:
            contents = d.readlines()
            firstline = contents[0]
            flag = str in firstline
            if flag is True:
                return flag
                break
##------------------------------------------------------------
def delete_top(files):#删除每个txt文件的头9行
    files = os.listdir(files)#创建路径下所有文件的列表
    files.sort(key = lambda x: int(re.findall('\d+', x)[1]))#按照数字大小排序
    for file in files:
        print("\t" + file)#打印输出排序结果
    for file in files:
        file = filepath + '/'+ file
        with open(file, 'r', encoding = 'utf-8') as d:
            contents = d.readlines()#遍历所有的文件，除了代码输出文件以外的所有文件的每一行
        with open(file,'w') as d:
            d.write(''.join(contents[9:]))#删除每个txt文件的头9行
##------------------------------------------------------------
def find_basic (filename):##输出文件的基本信息，时间步，尺寸和原子数目
    dict_parameters = {}#'TIMESTEP':'','NUMBER OF ATOMS':'','BOX':''
    with open (filename,'r', encoding='utf-8') as d:
        contents = d.readlines()
        i=0
        for line in contents[:6]:
            judge = 'ITEM'
            flag = judge in line
            if flag is True:
                continue
            else:
                i+=1
                dict_parameters[i] = line
    return dict_parameters
##------------------------------------------------------------
##定义函数——名称为：加，除，乘
def add(a,b,c):
        return a + b + c
##------------------------------------------------------------
def sub(a,b):
        return a/b
##------------------------------------------------------------
def mag(a,b):
        return a*b
##------------------------------------------------------------
def add_header(filename,originalfile):
    with open(filename, "r+") as file:
        old = file.readlines()[1:]
        #print(old)
        file.seek(0)
        with open(originalfile,'r') as w:
            head = w.readlines()[:8]
        file.writelines(head)
        add = "ITEM: ATOMS id type x y z c_a c_b numx numy numz sintered\n"
        file.write(add)
        file.writelines(old)
##------------------------------------------------------------       
def find_sintring(filename,binsize,parameter_data,filesave):
    finite_element = globals()
    boxlow = float(parameter_data[3].split()[0])
    boxhigh = float(parameter_data[3].split()[1])
    binsize = float(binsize)
    print('Process at file:',filename,'/n Box height:',boxlow,boxhigh,end= '\n')
    with open (filename,'r', encoding='utf-8') as d:
        contents = d.readlines()
        firstline = contents[0]
        flag = 'ITEM' in firstline
        if flag is True:
            contentsnew = contents[8:]
        else:
            contentsnew = contents
    contentsnew[0] = contentsnew[0][11:-1]
    res=contentsnew[0].strip(' ')
    res=res.strip(' ')
    res=res.split(' ')
    data = pd.read_table(filename,sep = '\s+', skiprows = 9, names = res )
    df = pd.DataFrame(data, columns=['id', 'type', 'x', 'y', 'z','c_a','c_b'])
    df.loc[:,'numx']= sub(df.loc[:,'x'],binsize).astype(int)
    df.loc[:,'numy']= sub(df.loc[:,'y'],binsize).astype(int)
    df.loc[:,'numz']= sub(df.loc[:,'z'],binsize).astype(int)
    numxmax = df.loc[:,'numx'].max()
    numxmin = df.loc[:,'numx'].min()
    numymax = df.loc[:,'numy'].max()
    numymin = df.loc[:,'numy'].min()
    numzmax = df.loc[:,'numz'].max()
    numzmin = df.loc[:,'numz'].min()
    shaojie_index = 0
    shaojie = pd.DataFrame(columns=['numx','numy','numz','Sintered'])
    for ix in range(numxmin,numxmax,1):
        for iy in range(numymin,numymax,1):
            for iz in range(numzmin,numzmax,1):
                finite_element[str(ix)+str(iy)+str(iz)] = pd.DataFrame()
                finite_element[str(ix)+str(iy)+str(iz)] = finite_element[str(ix)+str(iy)+str(iz)].append(
                    df[(df['numx'] == int(ix)) & (df['numy'] == int(iy) )& (df['numz'] == int(iz))])
                if finite_element[str(ix)+str(iy)+str(iz)].empty:
                    pass
                else:
                    if len(set(finite_element[str(ix)+str(iy)+str(iz)]['type']))> 1:
                        df.loc[(df['numx'] == int(ix)) & (df['numy'] == int(iy) )& (df['numz'] == int(iz)),'sintered'] = 1
                        shaojie = shaojie.append({'numx':ix,'numy':iy,'numz':iz,'Sintered':1},ignore_index=True)
                        shaojie_index +=1
                    else:
                        df.loc[(df['numx'] == int(ix)) & (df['numy'] == int(iy) )& (df['numz'] == int(iz)),'sintered'] = 0
                        shaojie = shaojie.append({'numx':ix,'numy':iy,'numz':iz,'Sintered':0},ignore_index=True)
                print('Now at the finite_element:',ix,iy,iz,end = '\r')
    df = df.fillna(0)
    df.to_csv(filesave +'/'+ 'Afterdegree{}'.format(str(re.findall('\d+', filename)[-2]))+'/'+'step{}.atom'.format(str(re.findall('\d+', filename)[-1])),sep=' ',index=False)
    add_header(filesave +'/'+ 'Afterdegree{}'.format(str(re.findall('\d+', filename)[-2]))+'/'+'step{}.atom'.format(str(re.findall('\d+', filename)[-1])),filename)
    shaojie.to_csv(filesave +'/'+ 'Afterdegree{}'.format(str(re.findall('\d+', filename)[-2]))+'/'+'{}.txt'.format(str(re.findall('\d+', filename)[-1])))
    singleball = 'sintering—singleball{}.txt'.format(str(re.findall('\d+', filename)[-2]))
    singleball = filesave +'/'+singleball
    with open(singleball, 'a') as x:
        x.write(str(shaojie_index))
        x.write(' ')
        x.write(str(re.findall('\d+', filename)[-2]))
        x.write('\n')
        x.close()

##------------------------------------------------------------
total_filepath = r'E:\2022.9.16.2ball\2022.9.14.2ball\result'
filesave = r'E:\2022.9.16.2ball\2022.9.19.jisuan'
filedirs = os.listdir(total_filepath)
for filedir in filedirs:
    filedir = total_filepath+ '/' +filedir
    files = os.listdir(filedir)
    files.sort(key = lambda x: int(re.findall('\d+', x)[-1]))
    for file in files:
        file = filedir +'/'+ file
        os.mkdir(filesave +'/'+ 'Afterdegree{}'.format(str(re.findall('\d+', file)[-2])))
        break
    for file in files:
        file = filedir +'/'+ file
        parameter_data = find_basic(file)
        find_sintring(file,2.5,parameter_data,filesave)
##------------------------------------------------------------
