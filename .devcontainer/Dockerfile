# Use the official Python image from the Docker Hub
FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye

# Update the list of packages and install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
