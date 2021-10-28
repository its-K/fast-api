
FROM python:latest

WORKDIR /code

COPY app/requirements.txt /code/requirements.txt


RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt


COPY app /code/app

ENV PYTHONPATH "${PYTHONPATH}:/code/app"


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]