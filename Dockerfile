FROM python:3.12-slim

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    pip install -r requirements.txt

RUN playwright install --with-deps

COPY . .

CMD ["python", "-m", "src.main"]
