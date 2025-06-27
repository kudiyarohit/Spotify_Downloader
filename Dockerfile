FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg git gcc libffi-dev libssl-dev && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy app files
COPY . .

# Copy your cookies.txt (must be in same dir as Dockerfile)
COPY cookies.txt /app/cookies.txt

COPY cookies.txt /root/.config/spotdl/cookies.txt

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Create yt-dlp config and include user-agent and cookie path
RUN mkdir -p /root/.config/yt-dlp && \
    echo '--user-agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"' > /root/.config/yt-dlp/config && \
    echo '--cookies /app/cookies.txt' >> /root/.config/yt-dlp/config

RUN mkdir -p /root/.config/spotdl && \
    echo '--cookies /root/.config/spotdl/cookies.txt' >> /root/.config/spotdl/config

# Expose port
EXPOSE 5000

# Start the app using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "300", "run:app"]
