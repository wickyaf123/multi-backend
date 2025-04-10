# NRL Multi-Builder Backend

A Flask-based backend API for the NRL Multi-Builder application, which helps users build multi-bets for NRL (National Rugby League) games based on their desired stake and win amount.

## Features

- Generates optimal multi-bet combinations based on user's stake and desired win amount
- Provides alternative player suggestions for each position in the multi
- Uses a backtracking algorithm with pruning for efficient combination finding
- Handles various constraints like one bet per game, minimum/maximum legs, etc.
- Calculates potential win amounts and achieved odds

## API Endpoints

- `POST /api/generate-multi`: Generates a multi-bet combination with player alternatives
- `GET /health`: Health check endpoint

## Technology Stack

- Python 3.9
- Flask
- Docker
- Railway (for deployment)

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Docker (optional)

### Running Locally with Python

1. Clone the repository:
   ```bash
   git clone https://github.com/wickyaf123/multi-backend.git
   cd multi-backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python app.py
   ```

The API will be available at http://localhost:5001.

### Running with Docker

1. Build and run using Docker Compose:
   ```bash
   docker-compose up --build
   ```

The API will be available at http://localhost:5001.

## Environment Variables

- `PORT`: Port to run the application on (default: 5001)
- `ALLOWED_ORIGINS`: Comma-separated list of allowed CORS origins (default: http://localhost:3000)
- `FLASK_ENV`: Application environment (development/production)

## Deployment

This application is designed to be deployed on Railway. Railway will automatically detect the Dockerfile and deploy the application.

### Deploy on Railway

1. Push the code to GitHub:
   ```bash
   git push origin main
   ```

2. Connect your GitHub repository to Railway
3. Railway will automatically build and deploy the application

## License

MIT 