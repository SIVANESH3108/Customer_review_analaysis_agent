import pymysql
import json
from dbutils.pooled_db import PooledDB
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    _pool = None

    @classmethod
    def get_pool(cls):
        if cls._pool is None:
            try:
                cls._pool = PooledDB(
                    creator=pymysql,
                    maxconnections=10,
                    mincached=2,
                    maxcached=5,
                    blocking=True,
                    host=Config.DB_HOST,
                    user=Config.DB_USER,
                    password=Config.DB_PASSWORD,
                    database=Config.DB_NAME,
                    cursorclass=pymysql.cursors.DictCursor
                )
                logger.info("Database connection pool created successfully.")
            except Exception as e:
                logger.error(f"Error creating connection pool: {e}")
                raise e
        return cls._pool

    @classmethod
    def get_connection(cls):
        return cls.get_pool().connection()

    @classmethod
    def initialize_db(cls):
        """Initializes the database and tables if they don't exist."""
        try:
            conn = pymysql.connect(
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                cursorclass=pymysql.cursors.DictCursor
            )
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.DB_NAME}")
            cursor.execute(f"USE {Config.DB_NAME}")
            
            create_users_table = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_users_table)
            
            create_table_query = """
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
            )
            """
            cursor.execute(create_table_query)
            
            # Add user_id column if it doesn't exist (for existing tables)
            try:
                cursor.execute("ALTER TABLE analysis_history ADD COLUMN user_id INT")
                cursor.execute("ALTER TABLE analysis_history ADD FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE")
            except Exception as e:
                # Column might already exist
                pass
                
            conn.commit()
            cursor.close()
            conn.close()
            logger.info("Database initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")

    @classmethod
    def create_user(cls, username, password_hash):
        try:
            conn = cls.get_connection()
            cursor = conn.cursor()
            query = "INSERT INTO users (username, password_hash) VALUES (%s, %s)"
            cursor.execute(query, (username, password_hash))
            conn.commit()
            last_id = cursor.lastrowid
            cursor.close()
            conn.close()
            return last_id
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise e

    @classmethod
    def get_user_by_username(cls, username):
        try:
            conn = cls.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            return user
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            raise e

    @classmethod
    def save_analysis(cls, review, analysis, user_id=None):
        try:
            conn = cls.get_connection()
            cursor = conn.cursor()
            
            query = """
            INSERT INTO analysis_history (
                user_id, customer_review, summary, sentiment, positive_percentage, 
                negative_percentage, neutral_percentage, positive_points, 
                negative_points, top_complaints, keywords, recommendations, 
                rating, business_recommendation
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                user_id,
                review,
                analysis.get('summary'),
                analysis.get('overall_sentiment'),
                analysis.get('positive_percentage'),
                analysis.get('negative_percentage'),
                analysis.get('neutral_percentage'),
                json.dumps(analysis.get('positive_points', [])),
                json.dumps(analysis.get('negative_points', [])),
                json.dumps(analysis.get('top_complaints', [])),
                json.dumps(analysis.get('keywords', [])),
                json.dumps(analysis.get('suggestions', [])),
                analysis.get('rating'),
                analysis.get('business_recommendation')
            )
            
            cursor.execute(query, values)
            conn.commit()
            last_id = cursor.lastrowid
            
            cursor.close()
            conn.close()
            return last_id
        except Exception as e:
            logger.error(f"Error saving analysis: {e}")
            raise e

    @classmethod
    def get_history(cls, user_id=None):
        try:
            conn = cls.get_connection()
            cursor = conn.cursor()
            if user_id:
                cursor.execute("SELECT * FROM analysis_history WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
            else:
                cursor.execute("SELECT * FROM analysis_history WHERE user_id IS NULL ORDER BY created_at DESC")
            results = cursor.fetchall()
            
            # Parse JSON fields back to python lists
            for row in results:
                for field in ['positive_points', 'negative_points', 'top_complaints', 'keywords', 'recommendations']:
                    if row.get(field):
                        try:
                            row[field] = json.loads(row[field])
                        except Exception:
                            pass
            
            cursor.close()
            conn.close()
            return results
        except Exception as e:
            logger.error(f"Error getting history: {e}")
            raise e

    @classmethod
    def delete_analysis(cls, analysis_id, user_id=None):
        try:
            conn = cls.get_connection()
            cursor = conn.cursor()
            if user_id:
                cursor.execute("DELETE FROM analysis_history WHERE id = %s AND user_id = %s", (analysis_id, user_id))
            else:
                cursor.execute("DELETE FROM analysis_history WHERE id = %s AND user_id IS NULL", (analysis_id,))
            conn.commit()
            affected = cursor.rowcount
            cursor.close()
            conn.close()
            return affected > 0
        except Exception as e:
            logger.error(f"Error deleting analysis: {e}")
            raise e

    @classmethod
    def delete_all_analysis(cls, user_id=None):
        try:
            conn = cls.get_connection()
            cursor = conn.cursor()
            if user_id:
                cursor.execute("DELETE FROM analysis_history WHERE user_id = %s", (user_id,))
            else:
                cursor.execute("DELETE FROM analysis_history WHERE user_id IS NULL")
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error deleting all analysis: {e}")
            raise e

    @classmethod
    def get_stats(cls, user_id=None):
        try:
            conn = cls.get_connection()
            cursor = conn.cursor()
            
            if user_id:
                cursor.execute("SELECT COUNT(*) as total FROM analysis_history WHERE user_id = %s", (user_id,))
                total = cursor.fetchone()['total']
                
                cursor.execute("SELECT sentiment, COUNT(*) as count FROM analysis_history WHERE user_id = %s GROUP BY sentiment", (user_id,))
                sentiments = cursor.fetchall()
                
                cursor.execute("SELECT AVG(CAST(rating AS DECIMAL)) as avg_rating FROM analysis_history WHERE user_id = %s AND rating REGEXP '^[0-9]+$'", (user_id,))
                avg_rating_row = cursor.fetchone()
            else:
                cursor.execute("SELECT COUNT(*) as total FROM analysis_history WHERE user_id IS NULL")
                total = cursor.fetchone()['total']
                
                cursor.execute("SELECT sentiment, COUNT(*) as count FROM analysis_history WHERE user_id IS NULL GROUP BY sentiment")
                sentiments = cursor.fetchall()
                
                cursor.execute("SELECT AVG(CAST(rating AS DECIMAL)) as avg_rating FROM analysis_history WHERE user_id IS NULL AND rating REGEXP '^[0-9]+$'")
                avg_rating_row = cursor.fetchone()

            avg_rating = float(avg_rating_row['avg_rating']) if avg_rating_row and avg_rating_row['avg_rating'] else 0
            
            cursor.close()
            conn.close()
            
            positive = sum(s['count'] for s in sentiments if s.get('sentiment') and s['sentiment'].lower() == 'positive')
            negative = sum(s['count'] for s in sentiments if s.get('sentiment') and s['sentiment'].lower() == 'negative')
            
            return {
                "total_analyses": total,
                "average_rating": round(avg_rating, 2),
                "positive_reviews": positive,
                "negative_reviews": negative,
                "sentiment_distribution": sentiments
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            raise e
