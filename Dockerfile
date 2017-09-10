FROM python:3.6-alpine

WORKDIR /usr/src/app
COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY src .

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0", "main:app"]
