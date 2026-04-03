FROM python:3.12-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update &amp;&amp; apt-get install -y \
    gcc \
    &amp;&amp; rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
COPY setup.py .
COPY config/ ./config/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip &amp;&amp; \
    pip install --no-cache-dir -r requirements.txt &amp;&amp; \
    pip install --no-cache-dir -e .

# Copy project
COPY . .

# Expose port for potential dashboard (Streamlit default 8501)
EXPOSE 8501

# Default entrypoint: CLI bot (can override with docker run ... python -m DEV.gui_bot or others)
ENTRYPOINT ["python", "-m", "bots.cli_bot"]

