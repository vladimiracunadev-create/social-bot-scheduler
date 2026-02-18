FROM python:3.11-alpine
WORKDIR /app
RUN apk add --no-cache gcc musl-dev
RUN pip install fastapi uvicorn pydantic
COPY . .
EXPOSE 8000
CMD ["python", "main.py"]
