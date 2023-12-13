FROM python:3.8-slim-buster

WORKDIR /serverless-monitoring

COPY requirements.txt serverless-monitoring/requirements.txt

RUN pip3 install -r serverless-monitoring/requirements.txt

COPY . serverless-monitoring/

CMD ["python", "runtime.py"]