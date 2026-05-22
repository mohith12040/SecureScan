# Production-Grade Cybersecurity Docker Container
FROM python:3.13-slim

# Install system dependencies (specifically the Nmap native binary)
RUN apt-get update && apt-get install -y \
    nmap \
    && rm -rf /var/lib/apt/lists/*

# Set up execution environment
WORKDIR /app

# Copy dependency configs
COPY requirements.txt .

# Install dependencies using preferred wheels
RUN pip install --no-cache-dir -r requirements.txt

# Copy source assets
COPY . .

# Pre-train the severity model during the container build phase
# to optimize startup latency in serverless environments like Render
RUN python3 -m app.ml.train_model

# Expose server port
EXPOSE 5000

# Start server using Gunicorn WSGI
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
