import os
import time
import pandas as pd
import numpy as np
import ovito
from ovito.io import import_file, export_file
from ovito.modifiers import CalculateDisplacementsModifier, ExpressionSelectionModifier
print("Hello, this is OVITO %i.%i.%i" % ovito.version)
##---------------------------------------------------------------------------------------
def mkdir(path):
    '''
    创建指定的文件夹
    :param path: 文件夹路径，字符串格式
    :return: True(新建成功) or False(文件夹已存在，新建失败)
    '''
    # 引入模块
    import os
    # 去除首位空格
    path = path.strip()
    # 去除尾部 \ 符号
    path = path.rstrip("\\")
    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists = os.path.exists(path)
    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
         # 创建目录操作函数
        os.makedirs(path)
        print(path + ' 创建成功')
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        print(path + ' 目录已存在')
        return False
##---------------------------------------------------------------------------------------
def find_jumpatom_sinteringneck(filepath):
    filesave = filepath
    filepath = filepath + '/calculated'
    filestream = os.listdir(filepath)
    mkdir(filesave+'/save')
    ##---------------------------------------------------------------------------------------
    for fileseq in filestream:
        criterion_name = filepath + '/' +fileseq
        if os.path.isdir(criterion_name) is True:
            starttime = time.time()
            filename = fileseq
            fileseq = filepath + '/' +fileseq +'/' +'step*.atom'
            #读入lammps的轨迹文件，导入pipeline(ovito计算流), *通配符代表步长，从零开始
            print(fileseq)
            pipeline = import_file(fileseq)
            #打印轨迹文件总个数
            print("total_num_frames: %f" % pipeline.source.num_frames)
            pipeline.modifiers.append(CalculateDisplacementsModifier(use_frame_offset = True, frame_offset = -50))
            pipeline.modifiers.append(ExpressionSelectionModifier(expression = 'DisplacementMagnitude>=3.2&&Position.X>=-10&&Position.X<=10'))
            for frame in range(51,pipeline.source.num_frames):
                data = pipeline.compute(frame)
                step = str(frame)
                file1 = open(filesave + '/' + 'save' + '/' + "JumpAtom_{}.txt".format(filename),('a+'))
                file1.write(str(step))
                file1.write(' ')
                print(str(data.attributes['ExpressionSelection.count']),end='\r')
                file1.write(str(data.attributes['ExpressionSelection.count']))
                file1.write('\r')
            endtime = time.time()
            print('Time Elasped:',endtime-starttime,'Current Filestream:',filename)
            print('OK')
        else:
            print('Not a direction')
            pass
##---------------------------------------------------------------------------------------
filepath = r'E:\双球模拟数据整合\2022.10.24.duowendu\2022.10.24.duowendu\2022.10.24.2ball.600K2'
##---------------------------------------------------------------------------------------
def concat_datas(filepath):
    filesaves = os.listdir(filepath+'/save')
    all_data = pd.DataFrame()
    for file in filesaves:
        filename = filepath + '/save/'+ file
        r_data1 = pd.read_table(filename,sep='\s+',names=['Timestep','Count'])
        all_data.loc[:,'{}'.format(file)] = r_data1['Count']
        print(all_data)
    all_data.to_csv(filepath +'/'+ 'Results_jumpingAtoms.csv')

find_jumpatom_sinteringneck(filepath)
concat_datas(filepath)

