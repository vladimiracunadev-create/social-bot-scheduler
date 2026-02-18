FROM python:3.9-alpine

WORKDIR /app

# Instalar dependencias de sistema para pyodbc y el driver de SQL Server
RUN apk add --no-cache \
    curl \
    gnupg \
    unixodbc-dev \
    g++ \
    make \
    unixodbc \
    && curl -O https://download.microsoft.com/download/e/4/e/e4e67866-d358-4cd7-82ad-6033d64a1d9a/msodbcsql18_18.3.2.1-1_amd64.apk \
    && apk add --allow-untrusted msodbcsql18_18.3.2.1-1_amd64.apk \
    && rm msodbcsql18_18.3.2.1-1_amd64.apk

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
