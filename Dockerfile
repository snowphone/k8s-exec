FROM python:slim

ENV TZ=Asia/Seoul

WORKDIR /app

COPY .     ./

RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "exec.py" ]
