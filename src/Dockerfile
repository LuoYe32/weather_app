FROM python:3.9

WORKDIR /weather_app

COPY ./requirements.txt /src/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt

COPY ./src /weather_app/src

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]