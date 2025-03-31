FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

# Add NVIDIA drivers for GPU support
RUN curl -s -L https://nvidia.github.io/nvidia-container-runtime/gpgkey | apt-key add - \
    && curl -s -L https://nvidia.github.io/nvidia-container-runtime/$(. /etc/os-release;echo $ID$VERSION_ID)/nvidia-container-runtime.list > /etc/apt/sources.list.d/nvidia-container-runtime.list \
    && apt-get update

# Set up work directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create log and data directories with proper permissions
RUN mkdir -p /app/logs /app/data && \
    chmod -R 755 /app/logs /app/data

# Create a non-root user to run the application
RUN useradd -m appuser && \
    chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Expose API port
EXPOSE 8080

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set entry point script as executable
RUN chmod +x /app/scripts/docker-entrypoint.sh

# Use entry point script to initialize the application
ENTRYPOINT ["/app/scripts/docker-entrypoint.sh"]

# Default command to run when the container starts
CMD ["python", "-m", "src.api"]