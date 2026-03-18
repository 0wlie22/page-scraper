FROM python:3.12-slim AS builder

ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

RUN pip install playwright \
    && playwright install chromium \
    && chmod -R 755 /ms-playwright \
    && ls -la /ms-playwright

FROM python:3.12-slim

COPY --from=builder /ms-playwright /ms-playwright

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    pip install -r requirements.txt

ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

COPY src/ /app
WORKDIR /app

CMD ["python", "main.py"]
