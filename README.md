# Todoism使用

(可选)创建`.env`文件:
```.env
SECRET_KEY=
DATABASE_URI=
```
设置hosts文件
```
0.0.0.0  todoism.site
```
运行
```
pipenv install --dev
pipenv shell
flask translate compile
flask run
```

访问[http://api.todoism.site:8000/v1/](http://api.todoism.site:8000/v1/)获取接口信息.
