# Use official Python image (slim variant to keep image size small)
FROM python:3.10-slim

# Set environment variables to prevent Python from writing .pyc files and to buffer stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy the local project files to the container
COPY . /app

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set the default command to run the scraper script
ENTRYPOINT ["python", "email_scraper.py"]
