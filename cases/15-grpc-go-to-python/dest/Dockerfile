# ==================================================================================================
# Case 15 — Cliente gRPC Python + FastAPI. Contexto de build = raíz del caso (para proto/).
# ==================================================================================================
FROM python:3.11-slim
WORKDIR /app
COPY dest/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY proto/social.proto ./social.proto
# Genera los stubs Python (social_pb2.py + social_pb2_grpc.py).
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. social.proto
COPY dest/main.py dest/index.html ./
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
