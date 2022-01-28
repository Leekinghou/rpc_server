# rpc_server

```
git clone git@github.com:Leekinghou/beehive.git
```

## 添加bee_client子模块
```
cd beehive
git submodule add git@github.com:Leekinghou/bee_client.git
```

## 创建虚拟环境
```
virtualenv --no-site-packages venv --python=python3.6
source venv/bin/activate
```

## 安装验证识别依赖
```
cd beehive
pip install -r requirements.txt
cp config_example.yml config.yml
# modify config.yml
python run.py -c config.yml cracker
```