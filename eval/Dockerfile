# Eval app image: builds chainlit from this fork (frontend included) and runs eval/app.py.
# Build from the repo root: docker build -f eval/Dockerfile .

FROM node:24-slim AS build
# pnpm version comes from package.json "packageManager"; Cypress binary is only needed for E2E tests.
ENV COREPACK_ENABLE_DOWNLOAD_PROMPT=0 CYPRESS_INSTALL_BINARY=0 HUSKY=0
RUN corepack enable
COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /bin/uv
WORKDIR /src
COPY . .
# backend/build.py runs pnpm install + build and bundles frontend/copilot dist into the wheel.
RUN cd backend && uv build --wheel --python 3.12 --out-dir /dist

# Wheel only, for `--target wheel --output type=local`.
FROM scratch AS wheel
COPY --from=build /dist/ /

FROM python:3.12-slim
COPY --from=build /dist/ /tmp/dist/
RUN pip install --no-cache-dir /tmp/dist/chainlit-*.whl "openai>=2,<3" && rm -rf /tmp/dist
WORKDIR /app
COPY eval/app.py .
EXPOSE 8000
CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "8000", "--headless"]
