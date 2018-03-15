import os
import sys
import subprocess
import time
import glob
import shutil
from py4j.java_gateway import JavaGateway

def get_dict(fname):
    data_dict = {}
    with open(fname) as f:
        for line in f:
            try:
                content = line.split(" ", 2)
                ID = content[0]
                num = content[1]
                data = content[2]
                data_dict[(ID, num)] = data
            except IndexError:
                print("IndexError")
                print(line)
    return data_dict

def start_server():
    # クラスパスを指定して実行
    args=(["java","-cp", '/home/hirose/.pyenv/versions/3.5.4/share/py4j/py4j0.10.6.jar',
           '-jar', './SrcTokenizer.jar'])
    p=subprocess.Popen(args)
    # サーバー起動前に処理が下へ行くのを防ぐ
    time.sleep(3) 
    gateway = JavaGateway(start_callback_server=True)
    return gateway

def shutdown(gateway):
    gateway.shutdown()

bucket = [[50, -1], [100, -1], [150, -1], [200, -1]] 
bucket_st = [[50, 0], [100, 0], [150, 0], [200, 0]] 
MIN_LEN = 1
MAX_LEN = 200
O_MAX_LEN = 200

ONLY_END = False

if __name__ == "__main__":
    if not os.path.exists("data"):
        os.mkdir("data")
    if not os.path.exists("fix"):
        os.mkdir("fix")
    #gateway = start_server()
    #entry_point = gateway.entry_point

    input_data = get_dict("input.txt")
    output_data = get_dict("output.txt")

    for ID_dir in glob.glob("../../Template_Maker/BaseInfo/result/*"): 
        shutil.copyfile(ID_dir+"/q_src.java",
                        "data/"+os.path.basename(ID_dir)+".java")

        shutil.copyfile(ID_dir+"/a_src.java",
                        "data/"+os.path.basename(ID_dir)+"_correct.java")

    for key, line in output_data.items():
        with open("fix/"+key[0]+"_"+key[1]+".txt", "w") as f:
            f.write(line)

    exit()


    # 入力と出力を統合
    tmp_list = []
    for key in input_data.keys():
        try:
            i_d = input_data[key]
            o_d = output_data[key]
            tmp_list.append((i_d, o_d))
        except KeyError:
            print("KeyError")
            print(i_d)
            print(o_d)

    # データの選別
    data_list = []
    for i_d, o_d in tmp_list: 
        i_l = len(i_d.split(" "))
        # トークンの長さによる選別
        if i_l > MAX_LEN or i_l < MIN_LEN:
            print("input Too long")
            continue
              
        o_l = len(o_d.split(" "))
        if o_l > O_MAX_LEN:
            print("output Too long")
            continue

        data_list.append((i_d, o_d))

    # バケツ法のために各バケツが空にならないか確認
    for i_d, o_d in data_list: 
        i_l = len(i_d.split())
        for b, b_s in zip(bucket, bucket_st):
            if i_l < b[0]:
                b[1] = len(o_d.split())+1 if b[1] <= len(o_d.split()) else b[1]
                b_s[1] += 1
                break
    for b in bucket:
        if b[1] < 0:
            print("Bucket Error %d" % (b[0]))
            exit()
    print([tuple(x) for x in bucket])
    print([tuple(x) for x in bucket_st])

    # 半分に分ける
    total = len(data_list)
    half = int(total/2)

    # ONLY_ENDモードならendをoutputに入力する
    if ONLY_END:
        for i, data in enumerate(data_list):
            data = (data[0], "<end> "*10+"\n")
            data_list[i] = data

    with open("train_data_in", "w") as f:
        # for data in data_list[0:half]:
        for data in data_list:
            f.write(data[0])
    with open("train_data_out", "w") as f:
        # for data in data_list[0:half]:
        for data in data_list:
            f.write(data[1])
            # f.write(data[1])

    # ONLY_ENDモードでtestをendだけにする
    test_data_list = []
    if ONLY_END:
        for data in data_list:
            if data[1] == "<end>\n":
                test_data_list.append(data)
            elif data[1].find("<end>") >= 0:
                test_data_list.append(data)
    else:
        test_data_list = data_list

    with open("test_data_in", "w") as f:
        # for data in data_list[half:total]:
        for data in test_data_list:
            f.write(data[0])
    with open("test_data_out", "w") as f:
        # for data in data_list[half:total]:
        for data in test_data_list:
            f.write(data[1])

    shutdown(gateway)
    
    max_len = -1
    for data in tmp_list:
        if max_len < len(data[0].split()):
            max_len = len(data[0].split())
    print("length %d" % max_len) 
