# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set up the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy the script into the container
COPY main.py .

# Run the script
CMD ["python", "main.py"]