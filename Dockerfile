FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend backend
COPY frontend frontend
RUN useradd --create-home app && mkdir /data && chown app /data
USER app
ENV DATABASE_PATH=/data/advising.db
EXPOSE 8001
CMD ["python","-m","uvicorn","backend.app:app","--host","0.0.0.0","--port","8001"]
