FROM python:3.13-slim

WORKDIR /app

RUN pip install --upgrade --no-cache-dir "pip>=25" && \
    pip install --root-user-action=ignore --no-cache-dir "poetry>=2,<3"

COPY pyproject.toml poetry.lock* /app/

RUN poetry config virtualenvs.create false \
    && poetry install -vv --without dev \
       --no-root --no-interaction --no-ansi --no-cache

COPY ./app /app/

EXPOSE 7086

CMD ["uvicorn", "main:http_api_app", "--host", "0.0.0.0", "--port", "7086"]
