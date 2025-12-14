FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY basket_bot_backend/ ./basket_bot_backend/
COPY basket_bot_frontend/ ./basket_bot_frontend/
EXPOSE 8000

CMD ["python", "-m", "uvicorn", "basket_bot_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
