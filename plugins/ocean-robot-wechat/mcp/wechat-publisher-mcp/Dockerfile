ARG PYTHON_IMAGE=m.daocloud.io/docker.io/library/python:3.13-slim
FROM ${PYTHON_IMAGE}

ARG UV_VERSION=0.11.7

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_DEFAULT_INDEX=https://mirrors.aliyun.com/pypi/simple \
    PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple

RUN pip install --no-cache-dir "uv==${UV_VERSION}"

WORKDIR /app
COPY pyproject.toml README.md ./
RUN uv sync --no-dev --no-install-project

COPY src ./src
RUN uv sync --frozen --no-dev

RUN useradd --create-home --uid 10001 app \
    && mkdir -p /data \
    && chown -R app:app /data /app

USER app
EXPOSE 8000
VOLUME ["/data"]

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=2)"]

CMD ["uv", "run", "--frozen", "--no-dev", "wechat-publisher-mcp"]
