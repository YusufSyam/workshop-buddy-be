# Use Python 3.10 slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all other files
COPY . .

# Create uploads directories and set permissions for database and uploads
RUN mkdir -p uploads/mechanics uploads/inventory && \
    chmod -R 755 uploads && \
    touch workshop.db bengkel.db && \
    chmod 666 workshop.db bengkel.db || true

# Expose port 7860 (Hugging Face default port)
EXPOSE 7860

# Run uvicorn on host 0.0.0.0 and port 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]

