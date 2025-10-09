# Dockerfile for PyVault Dev Container
# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /workspace

# Install system dependencies required for PySide6 (Qt)
# libxcb-cursor0 is needed for cursor support in some environments
RUN apt-get update && apt-get install -y \
  libgl1-mesa-glx \
  libglib2.0-0 \
  libxkbcommon-x11-0 \
  libxcb-icccm4 \
  libxcb-image0 \
  libxcb-keysyms1 \
  libxcb-randr0 \
  libxcb-render-util0 \
  libxcb-shape0 \
  libxcb-xinerama0 \
  libxcb-xfixes0 \
  libxcb-cursor0 \
  && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# The container will run as a non-root user for better security
# Create a non-root user and switch to it
RUN useradd -ms /bin/bash vscode
USER vscode

# Keep the container running
CMD ["sleep", "infinity"]
