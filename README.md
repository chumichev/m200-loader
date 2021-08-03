# m200-loader

Сохраняет в базу данных данные поступающие от АТС М-200

Установка

1. Клонировать этот репозиторий
```git
git clone https://github.com/chumichev/m200-loader.git
```

2. Переименовать settings.default.py в settings.py
```shell
mv settings.default.py settings.py
```

3. Сконфигурировать параметры подключения к модулям АТС и параметры базы данных в settings.py
4. Собрать образ и запустить контейнер
```
docker build -t m200-cdr-loader .
docker run -d --restart=always --name cdr_loader m200-cdr-loader
```