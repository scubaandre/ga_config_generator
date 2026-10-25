FROM python:3.11-slim-bullseye

# Install core utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python requirements
RUN pip install --no-cache-dir streamlit requests pyyaml

# Copy app files
WORKDIR /app
COPY app.py run.sh /app/

# Make the startup script executable
RUN chmod a+x /app/run.sh

CMD [ "/app/run.sh" ]
