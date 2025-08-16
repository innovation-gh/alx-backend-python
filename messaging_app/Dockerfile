# Use Python 3.10 as base image
FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        default-mysql-client \
        pkg-config \
        default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . /app/

# Expose port 8000 (equivalent to docker run -p 8000:8000)
EXPOSE 8000

# Note: Port mapping with -p is done at runtime: docker run -p 8000:8000
# Default command to run Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
