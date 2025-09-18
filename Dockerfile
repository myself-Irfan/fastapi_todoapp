# use python slim version
FROM python:3.11-slim

LABEL authors='irfan-ahmed'

# set work dir
WORKDIR /app

# install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc libpq-dev curl && rm -rf /var/lib/apt/lists/*

# install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy project files
COPY . .

# expose port
EXPOSE 8080

# run app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]