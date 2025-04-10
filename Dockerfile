FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Make sure the mock data is available
RUN if [ ! -f mock_nrl_data.json ]; then echo "[]" > mock_nrl_data.json; fi

# Environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PORT=5001
ENV ALLOWED_ORIGINS=http://localhost:3000

# Expose the port
EXPOSE $PORT

# Run the application
CMD gunicorn --bind 0.0.0.0:$PORT app:app 