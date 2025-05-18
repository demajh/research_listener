### `backend/Dockerfile`
# Use official python image
FROM python:3.9-slim

# Set work directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

RUN apt-get update && apt-get install -y \
        build-essential libpango-1.0-0 libpangocairo-1.0-0 \
        libcairo2 libffi-dev shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . /app

# Expose port
EXPOSE 8000

# Run the API server
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
