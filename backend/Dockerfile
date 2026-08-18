# Portable container build for the Omni-Agent API — useful if you deploy
# somewhere other than Render's native Python runtime (Fly.io, Railway,
# AWS App Runner/ECS, etc). Render itself does not need this file (see
# ../render.yaml, which uses runtime: python directly).
FROM python:3.11-slim

WORKDIR /app

COPY requirements-deploy.txt .
# requirements-deploy.txt = requirements.txt minus emergentintegrations
# (Emergent-private package, not resolvable off-platform — see that file).
RUN pip install --no-cache-dir -r requirements-deploy.txt

COPY . .

EXPOSE 8000

# $PORT is respected when the platform sets it (Render, Railway, Fly);
# defaults to 8000 for `docker run` locally.
ENV PORT=8000
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT}"]
