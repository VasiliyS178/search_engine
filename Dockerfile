FROM python:3.13-alpine

WORKDIR /src

COPY requirements.txt .

RUN pip3 install --no-cache-dir --upgrade -r requirements.txt

COPY ./src .

CMD ["fastapi", "dev", "main.py", "--port", "8080", "--host", "0.0.0.0"]