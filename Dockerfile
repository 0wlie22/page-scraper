FROM python:3.11-slim AS builder

RUN pip install playwright
RUN playwright install chromium

FROM python:3.12-slim

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    pip install -r requirements.txt

ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

COPY src/ /app

WORKDIR /app

CMD ["python", "main.py"]
