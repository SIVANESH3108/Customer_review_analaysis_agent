# Customer Review Analysis Agent

An AI-powered web application that analyzes customer reviews using Google's Gemini API. The system summarizes reviews, identifies sentiment, extracts common issues, highlights positive aspects, recommends business improvements, and stores all analysis in a MySQL database.

## Features
- **Modern Landing Page**: Dashboard layout with glassmorphism aesthetics.
- **Customer Review Input**: Paste reviews or upload text files for analysis.
- **AI Analysis**: Uses `gemini-2.5-flash` to extract summary, sentiment, keywords, ratings, and business recommendations.
- **Analysis History**: Stores all analysis results in a MySQL database for future reference.
- **Statistics Dashboard**: Visualizes overall sentiment distribution and volumes using Chart.js.
- **Management**: Search through history or delete records.

## Folder Structure
```
Customer-Review-Agent/
│
├── client/                 # Frontend
│   ├── index.html          # HTML Layout
│   ├── style.css           # Vanilla CSS (Glassmorphism & Responsive)
│   └── script.js           # Vanilla JavaScript for API interaction & UI logic
│
├── server/                 # Backend
│   ├── app.py              # Flask Application Entry Point
│   ├── config.py           # Configuration (loads env vars)
│   ├── database.py         # MySQL Database connection pool & queries
│   ├── gemini_service.py   # Google Generative AI integration
│   ├── routes.py           # RESTful API endpoints
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Example environment variables
│
├── database.sql            # MySQL schema
└── README.md               # Documentation
```

## Installation

### Prerequisites
- Python 3.8+
- MySQL Server
- Node.js (Optional, if you wish to use a local static server like `http-server`)

### Backend Setup
1. Navigate to the `server` directory:
   ```bash
   cd Customer-Review-Agent/server
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file by copying the template:
   ```bash
   cp .env.example .env
   ```
4. Fill in your variables in the `.env` file:
   ```env
   GEMINI_API_KEY=your_actual_gemini_api_key
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_db_password
   DB_NAME=customer_review_db
   ```

### MySQL Setup
1. Ensure your MySQL server is running.
2. The application will attempt to auto-initialize the database `customer_review_db` and create the `analysis_history` table on the first request if they don't exist.
3. Alternatively, you can run the `database.sql` script manually in your MySQL workbench/CLI.

## Running Locally

1. Start the Flask server:
   ```bash
   cd server
   python app.py
   ```
   The backend will start at `http://localhost:5000`.

2. Serve the frontend:
   Open `client/index.html` in your browser directly, OR serve it using a local static server:
   ```bash
   # using python
   cd client
   python -m http.server 8000
   ```
   Then visit `http://localhost:8000` in your browser.

## Deployment

### Deploy Backend on Render
1. Push your code to a GitHub repository.
2. Log into Render and create a new **Web Service**.
3. Connect your repository.
4. Set the Root Directory to `server`.
5. Set the Build Command to `pip install -r requirements.txt`.
6. Set the Start Command to `gunicorn app:app`.
7. Add Environment Variables from your `.env` file. (Note: You will need a remote MySQL database like Aiven or PlanetScale to connect to, as Render doesn't host MySQL natively).

### Deploy Frontend on Netlify
1. Log into Netlify and click "Add new site" -> "Import an existing project".
2. Connect your GitHub repository.
3. Set the Publish directory to `client`.
4. (Optional) Update `API_URL` in `client/script.js` to point to your live Render backend URL before deploying.

## Screenshots placeholder
*(Add screenshots of your UI here)*

## Future Improvements
- Implement user authentication to separate analysis history by user.
- Export analysis history as CSV/PDF.
- Add real-time websocket support for long-running batch analysis.
- Support uploading CSV/Excel files containing multiple individual reviews for batch processing.
