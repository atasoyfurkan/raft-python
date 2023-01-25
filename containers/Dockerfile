FROM python:3.10-alpine3.16

WORKDIR /usr/src/app
COPY Pipfile Pipfile.lock ./

RUN pip3 install --no-cache-dir --upgrade pip pipenv && \
  pipenv requirements > requirements.txt && \
  pip install --no-cache -r requirements.txt

COPY . /usr/src/app/

CMD [ "python3", "./main.py" ]