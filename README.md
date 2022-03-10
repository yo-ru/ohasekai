# ohasekai
ohasekai is my take on osu! stable's bancho protocol.

## Setup
Setup is as follows:

```sh
# clone repo
1. git clone https://github.com/yo-ru/ohasekai.git && cd ohasekai
2. git submodule update --init

# install os-related dependencies
3. sudo apt-add-repository ppa:deadsnakes
4. sudo apt install python3.10-dev python3.10-distutils cmake build-essential \ 
            mysql-server nginx certbot

# install py-related dependencies
5. wget https://bootstrap.pypa.io/get-pip.py
6. python3.10 get-pip.py && rm get-pip.py
7. python3.10 -m pip install -r requirements.txt

# import ohasekai's mysql structure to a pre-created database
8. mysql -u yourUsername -p yourDBName < ext/ohasekai.mysql

# configure nginx
sudo cp ext/nginx.conf /etc/nginx/sites-enabled/ohasekai.conf
sudo nano /etc/nginx/sites-enabled/ohaeskai.conf  # NOTE: finish configuring before continuing
sudo service nginx restart

# configure ohasekai
cp .env.example .env
nano .env
```
