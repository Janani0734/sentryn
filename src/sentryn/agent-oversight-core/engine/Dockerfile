FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install fastapi uvicorn numpy redis qdrant-client pydantic sentence-transformers requests --extra-index-url https://download.pytorch.org/whl/cpu

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
