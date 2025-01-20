#Base Image
FROM python:3.10-slim

#Working Directory
WORKDIR /app

#Install Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#Copy Code File
COPY main.py .

#Run Fast Api Without Worker and Threads
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

#Run Fast Api With Worker and Threads
CMD ["gunicorn", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--threads", "2", "--bind", "0.0.0.0:8000", "--log-level", "info", "main:app"]

