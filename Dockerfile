FROM python:3.13-slim
WORKDIR /app
COPY requirements.lock pyproject.toml LICENSE ./
COPY rag ./rag
RUN pip install --no-cache-dir -r requirements.lock && pip install --no-deps . && useradd --uid 10001 --create-home app && mkdir data && chown app:app data
USER app
EXPOSE 8084
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8084/health', timeout=2)"
CMD ["uvicorn", "rag.api:app", "--host", "0.0.0.0", "--port", "8084"]
