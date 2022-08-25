FROM python:slim

COPY TheInfiniteWebsite.py /theinfinitewebpage/TheInfiniteWebsite.py

COPY requirements.txt /theinfinitewebpage/requirements.txt

WORKDIR /theinfinitewebpage

RUN pip install -r requirements.txt

CMD ["python3","TheInfiniteWebsite.py"]
