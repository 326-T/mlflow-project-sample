FROM python:3.10 AS deps
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

FROM deps AS runner
WORKDIR /app
COPY main.py .

CMD ["python", "main.py"]