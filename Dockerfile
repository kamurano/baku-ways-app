# Use the official Python image
FROM python:3.12-slim

# Set work directory
WORKDIR /app

# Install Poetry and pip-tools
RUN pip install pip-tools

# Create virtual environment
RUN python3 -m venv venv

# Ensure bash is used to activate the virtual environment
SHELL ["/bin/bash", "-c"]

# Copy the project files
COPY . .

# Install dependencies
RUN ./venv/bin/pip install pip-tools
RUN ./venv/bin/pip-compile pyproject.toml
RUN ./venv/bin/pip install -r requirements.txt

# Make sure that the venv's bin is added to the PATH
ENV PATH="/app/venv/bin:$PATH"

# Expose the port FastAPI is running on
EXPOSE 8000

# Command to run the app with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
