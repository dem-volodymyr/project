# Use Python 3.13 as the base image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Run migrations and load initial data
RUN cd slot_machine_api && python manage.py migrate
RUN cd slot_machine_api && python manage.py loaddata symbols

# Expose port 8000
EXPOSE 8000

# Run the application
CMD ["python", "slot_machine_api/manage.py", "runserver", "0.0.0.0:8000"]