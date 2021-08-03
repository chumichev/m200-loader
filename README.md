# m200-loader

Сохраняет в базу данных данные поступающие от АТС М-200

``` 
docker build -t m200-cdr-loader .
docker run -d --rm --name cdr_loader m200-cdr-loader
```