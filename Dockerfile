# Stage 1: Build the application
FROM python:3.10-slim AS builder

# Set working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN python -m nltk.downloader punkt
RUN git clone https://github.com/HKUDS/LightRAG.git
RUN pip install -e ./LightRAG

RUN apt-get update && \
DEBIAN_FRONTEND=noninteractive apt-get install -y \
cmake \
protobuf-compiler \
libprotobuf-dev \
poppler-utils \
libgl1 \
libgl1-mesa-glx \
libglib2.0-0 \
libgtk2.0-dev \
libsm6 \
libxrender1 \
libxext6 \
tesseract-ocr \
tesseract-ocr-eng \
python3-nltk

# # Stage 2: Create the production image
# FROM python:3.12-slim

# # Set working directory
# WORKDIR /app

# # Copy only necessary files from the builder stage
# COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/

# Copy the entire current directory (.) to /app in the container
COPY . /app
# Expose port
EXPOSE 8080

# Command to run the FastAPI application
CMD ["fastapi", "run", "app/main.py", "--port", "8000"]
# CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8080"]

