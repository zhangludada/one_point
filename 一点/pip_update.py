import concurrent.futures
import os

#写入更新列表
cmd="python3 -m pip list -o > pip txt"
os.system(cmd)
with open("../pip.txt",mode='r') as f:
    txt=f.read().split("\n")[2:]
#更新列表
pip_list=list(i.split(' ')[0] for i in txt)

def update(package):
    cmd=f"python3 -m pip --proxy http://127.0.0.1:8169 install --upgrade {package}"
    os.system(cmd)

def main():
    with concurrent.futures.ThreadPoolExecutor(5) as executor:
        res=executor.map(update,pip_list)

main()
