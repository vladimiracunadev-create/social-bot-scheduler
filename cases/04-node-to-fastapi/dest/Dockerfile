FROM python:3.13-alpine
WORKDIR /app
RUN apk add --no-cache gcc musl-dev
# requirements.txt viene con hashes SHA256: pip entra solo en modo
# --require-hashes, sin resolución de versiones en tiempo de build.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "main.py"]
