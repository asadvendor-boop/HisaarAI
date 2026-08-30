FROM node:22-slim AS web-build

WORKDIR /web
COPY web/package.json web/package-lock.json ./
RUN npm ci
COPY web ./
RUN npm run build

FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv==0.8.22 \
    && uv export --frozen --no-dev --no-hashes --format requirements-txt > requirements.txt \
    && pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY fixtures ./fixtures
COPY --from=web-build /web/dist ./web-dist

ENV PYTHONPATH=/app/src \
    HISAAR_WEB_DIST=/app/web-dist
CMD ["sh", "-c", "uvicorn hisaarai.app:app --host 0.0.0.0 --port ${PORT}"]
