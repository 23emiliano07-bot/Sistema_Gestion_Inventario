FROM python:3.10.14-alpine3.19

COPY . /app

WORKDIR /app

COPY ./requirements.txt ./

RUN pip install -r requirements.txt

RUN python manage.py migrate

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]