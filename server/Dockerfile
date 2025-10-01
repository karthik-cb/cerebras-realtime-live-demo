# ---- Base image ----
    FROM python:3.12-slim

    # Optional: system libs your stack might need (uncomment as required)
    # RUN apt-get update && apt-get install -y --no-install-recommends \
    #     ffmpeg libsndfile1 curl ca-certificates \
    #   && rm -rf /var/lib/apt/lists/*
    
    ENV PYTHONDONTWRITEBYTECODE=1 \
        PYTHONUNBUFFERED=1
    
    WORKDIR /app
    
    # Copy backend code (keep relative requirements includes working)
    COPY . /app/
    
    # (Optional) debug to confirm files are where you expect
    # RUN set -eux; pwd; ls -la; ls -la webapp || true; ls -la bots || true
    
    # Install Python deps
    # Your server/requirements.txt includes -r ./webapp/... etc, so this path is correct
    RUN pip install --no-cache-dir -r requirements.txt
    
    # (Optional) if you have a "webapp/healthz" route, you can add a container healthcheck:
    # HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD \
    #   curl -fsS http://127.0.0.1:${PORT:-7860}/healthz || exit 1
    
    # Railway injects $PORT at runtime. Use a shell so ${PORT} expands.
    EXPOSE ${PORT}
    CMD ["sh","-c","uvicorn webapp.main:app --host 0.0.0.0 --port ${PORT} --proxy-headers"]
    