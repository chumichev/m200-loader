FROM python:3.9-alpine

WORKDIR /usr/src/m200-loader

COPY requirements.txt ./

RUN \
  apk add --no-cache postgresql-libs &&  \
  apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev &&  \
  pip install --no-cache-dir -r requirements.txt &&  \
  apk --purge del .build-deps

COPY . .

CMD ["python", "./cdr_loader.py"]