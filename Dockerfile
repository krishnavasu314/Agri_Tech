# Use an official Python base image
FROM python:3.11-slim

# Install system dependencies, including Tesseract OCR
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libtesseract-dev \
    build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy Python dependencies
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app/

COPY .env /app/.env

# Expose the port your application will run on
EXPOSE 8000

# Run the application
CMD ["gunicorn", "agritech.wsgi:application", "--bind", "0.0.0.0:8000"]