FROM python:3.13-slim

WORKDIR /app

# Copied and installed before the rest of the app so Docker can reuse this
# layer from cache when only app code changes, not dependencies.
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "apps.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
