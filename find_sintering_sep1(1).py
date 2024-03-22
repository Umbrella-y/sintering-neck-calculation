import os
import pandas as pd
import numpy as np
import math as math
import warnings
import re
import multiprocessing

warnings.filterwarnings("ignore")
##------------------------------------------------------------
# def findI(files):#查找文件中是否还包含文件头
#     str = "ITEM:"
#     files = os.listdir(files)#创建路径下所有文件的列表
#     files.sort(key = lambda x: int(re.findall('\d+', x)[1]))#按照数字大小排序
#     for file in files:
#         file = filepath + '/'+ file
#         with open(file, 'r', encoding = 'utf-8') as d:
#             contents = d.readlines()
#             firstline = contents[0]
#             flag = str in firstline
#             if flag is True:
#                 return flag
#                 break
##------------------------------------------------------------
# def delete_top(files):#删除每个txt文件的头9行
#     files = os.listdir(files)#创建路径下所有文件的列表
#     files.sort(key = lambda x: int(re.findall('\d+', x)[1]))#按照数字大小排序
#     for file in files:
#         print("\t" + file)#打印输出排序结果
#     for file in files:
#         file = filepath + '/'+ file
#         with open(file, 'r', encoding = 'utf-8') as d:
#             contents = d.readlines()#遍历所有的文件，除了代码输出文件以外的所有文件的每一行
#         with open(file,'w') as d:
#             d.write(''.join(contents[9:]))#删除每个txt文件的头9行
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
def panduan(a,b,c,d):
    if a==b and c==d:
        return 1
    else:
        return 0
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
def find_sintring(filename,binsize,parameter_data,filesave,df1_x_mean,df2_x_mean):
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
    calcu_max_x = int(df1_x_mean/binsize)
    calcu_min_x = int(df2_x_mean/binsize)
    #print(calcu_max_x,calcu_min_x)
    numxmax = df.loc[:,'numx'].max()
    numxmin = df.loc[:,'numx'].min()
    numymax = df.loc[:,'numy'].max()
    numymin = df.loc[:,'numy'].min()
    numzmax = df.loc[:,'numz'].max()
    numzmin = df.loc[:,'numz'].min()
    #print(numxmin,numxmax)
    shaojie_index = 0
    shaojie = pd.DataFrame(columns=['numx','numy','numz','Sintered'])
    for ix in range(calcu_min_x,calcu_max_x,1):#calcu_min_x,calcu_max_x
        for iy in range(numymin,numymax,1):
            for iz in range(numzmin,numzmax,1):
                finite_element[str(ix)+str(iy)+str(iz)] = pd.DataFrame()
                finite_element[str(ix)+str(iy)+str(iz)] = finite_element[str(ix)+str(iy)+str(iz)].append(
                    df[(df['numx'] == int(ix)) & (df['numy'] == int(iy) )& (df['numz'] == int(iz))])
                if finite_element[str(ix)+str(iy)+str(iz)].empty:
                    pass
                else:
                    if len(set(finite_element[str(ix)+str(iy)+str(iz)]['type']))> 1 :
                        df.loc[(df['numx'] == int(ix)) & (df['numy'] == int(iy) )& (df['numz'] == int(iz)),'sintered'] = 1
                        shaojie = shaojie.append({'numx':ix,'numy':iy,'numz':iz,'Sintered':1},ignore_index=True)
                        shaojie_index +=1
                    else:
                        df.loc[(df['numx'] == int(ix)) & (df['numy'] == int(iy) )& (df['numz'] == int(iz)),'sintered'] = 0
                        shaojie = shaojie.append({'numx':ix,'numy':iy,'numz':iz,'Sintered':0},ignore_index=True)
                print('Now at the finite_element:',ix,iy,iz,end = '\r')
    #print(shaojie)
    panduan_index = 0
    for i in shaojie.index:
        if shaojie.loc[i,'Sintered'] == 0:
            pass
        else:
            for j in shaojie.index:
                if shaojie.loc[j,'Sintered'] == 0:
                    pass
                else:
                    print("判断重复项",i,j,end = '\r')
                    if shaojie.loc[i,'numy'] == shaojie.loc[j,'numy'] and shaojie.loc[i,'numz'] == shaojie.loc[j,'numz'] and shaojie.loc[i,'numx'] != shaojie.loc[j,'numx']:
                        panduan_index +=1
                    else:
                        pass
    panduan_index_final = int(panduan_index/2)
    print("重复的烧结指数是：",panduan_index_final)
    print("烧结指数是：",shaojie_index)
    zhenshi_index = shaojie_index-panduan_index_final
    print("真实烧结指数为",zhenshi_index)
    df = df.fillna(0)
    df.to_csv(filesave +'/'+ 'Afterdegree{}'.format(str(re.findall('\d+', filename)[-2]))+'/'+'step{}.atom'.format(str(re.findall('\d+', filename)[-1])),sep=' ',index=False)
    add_header(filesave +'/'+ 'Afterdegree{}'.format(str(re.findall('\d+', filename)[-2]))+'/'+'step{}.atom'.format(str(re.findall('\d+', filename)[-1])),filename)
    shaojie.to_csv(filesave +'/'+ 'Afterdegree{}'.format(str(re.findall('\d+', filename)[-2]))+'/'+'{}.txt'.format(str(re.findall('\d+', filename)[-1])))
    singleball = 'sintering—singleball{}.txt'.format(str(re.findall('\d+', filename)[-2]))
    singleball = filesave +'/'+singleball
    with open(singleball, 'a') as x:
        x.write(str(zhenshi_index))
        x.write(' ')
        x.write(str(re.findall('\d+', filename)[-1]))
        x.write('\n')
        x.close()

##------------------------------------------------------------
def makefile(path):#获取到当前文件的目录，并检查是否有report文件夹，如果不存在则自动新建report文件
    if not os.path.exists(path):
        os.makedirs(path)
##------------------------------------------------------------   
def find_mass_center(filename):   
    boxlow = float(parameter_data[3].split()[0])
    boxhigh = float(parameter_data[3].split()[1])
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
    df1 = df[df['type'].isin([1])]
    df2 = df[df['type'].isin([2])]
    df1_x_mean = df1['x'].mean()
    df1_y_mean = df1['y'].mean()
    df1_z_mean = df1['z'].mean()
    df2_x_mean = df2['x'].mean()
    df2_y_mean = df2['y'].mean()
    df2_z_mean = df2['z'].mean()
    print("质心分别为：",df1_x_mean,df2_x_mean)
    return df1_x_mean,df2_x_mean
    #print(df1_x_mean-df2_x_mean,df1_x_mean,df2_x_mean)
total_filepath = r'.'
filesave = r'.'
filedirs = os.listdir(total_filepath)

for filedir in filedirs:
        filedir = total_filepath+ '/' +filedir
        files = os.listdir(filedir)
        files.sort(key = lambda x: int(re.findall('\d+', x)[-1]))
        sep = 10 ##                      -----------------------------------间隔值
        for file in files[::sep]:
            file = filedir +'/'+ file
            print(file)
            makefile(filesave +'/'+ 'Afterdegree{}'.format(str(re.findall('\d+', file)[-2])))
        for file in files[::sep]:
            file = filedir +'/'+ file
            parameter_data = find_basic(file)
            df1_x_mean,df2_x_mean = find_mass_center(file)
            find_sintring(file,3,parameter_data,filesave,df1_x_mean,df2_x_mean)

