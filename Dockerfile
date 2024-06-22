FROM python:3.10

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app
COPY ./assets /code/assets

CMD ["fastapi", "run", "app/api/main.py", "--port", "80"]