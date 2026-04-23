# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /code

# Copy the requirements file and install dependencies first to leverage caching
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# --- CRITICAL: Copy your models and data into the image ---
# This ensures your application can find them inside the container.
COPY ./saved_models /code/saved_models
COPY ./app/data /code/app/data

# Copy the rest of the application's source code
COPY ./app /code/app

# Expose the port the app runs on (FastAPI default is 8000)
EXPOSE 8000

# Define the command to run the Uvicorn server
# --host 0.0.0.0 makes the server accessible from outside the container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]