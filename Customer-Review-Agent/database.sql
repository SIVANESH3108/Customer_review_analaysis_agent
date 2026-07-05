CREATE DATABASE IF NOT EXISTS customer_review_db;
USE customer_review_db;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS analysis_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    customer_review TEXT NOT NULL,
    summary TEXT,
    sentiment VARCHAR(50),
    positive_percentage VARCHAR(10),
    negative_percentage VARCHAR(10),
    neutral_percentage VARCHAR(10),
    positive_points JSON,
    negative_points JSON,
    top_complaints JSON,
    keywords JSON,
    recommendations JSON,
    rating VARCHAR(10),
    business_recommendation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
