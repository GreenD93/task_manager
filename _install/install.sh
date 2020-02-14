#! /bin/bash

# chmod 777 ./install.sh
# after install, modify /etc/nginx/nginx.conf  -> worker_processes 2
# and sudo service nginx restart

# http://confluence.wemakeprice.com/pages/viewpage.action?pageId=83549724 컨플의
# /etc/hosts 변경할 것
# key, config 파일 다운로드
# key복사 : keyfile -> /var/lib/mongodb-mms-automation/keyfile 복사
# config복사: config -> /etc/mongod.conf 복사
# mongo --host 35.190.239.204 -u dlvDealRead -p --authenticationDatabase "praha"

GREEN='\033[1;32m'
NC='\033[0m' # No Color

function print_title {
  echo -e "\n\n\n"
  echo -e "${GREEN}############################################################"
  echo '###' $1
  echo -e "############################################################${NC}"
}

############################################################
cd /home/ubuntu/

print_title "install conda..."
wget https://repo.anaconda.com/miniconda/Miniconda3-4.7.10-Linux-x86_64.sh
bash Miniconda3-4.7.10-Linux-x86_64.sh
rm Miniconda*

source ~/.bashrc
export PATH="/home/ubuntu/miniconda3/bin:$PATH"
export LC_ALL=C

############################################################
print_title "update conda..."
conda update -n base conda

############################################################
print_title "create/activate conda environment ..."
conda create -n app python=3.7 -y

source activate app

############################################################
print_title "upgrade apt-get ..."
sudo apt-get update

sudo apt install gcc ### 조금 위험

############################################################
print_title "upgrade pip ..."
#conda install -c conda-forge pip
conda install -c anaconda pip

############################################################
print_title "install flask"
#conda install -c conda-forge pip
conda install -c anaconda pip

############################################################
print_title "upgrade pip ..."
#conda install -c conda-forge pip
conda install -c anaconda pip

############################################################
print_title "install flask ..."
conda install -c anaconda flask
pip install -U flask-cors

############################################################
print_title "install mysql related ..."
pip install pymysql

############################################################
print_title "install tqdm ..."
pip install tqdm
