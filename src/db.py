import os
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "lawyer_db")
DB_USER = os.getenv("POSTGRES_USER", "lawyer_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "lawyer_pass")

CONN_STRING = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Try importing psycopg for PostgreSQL connection
psycopg = None
try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:
    logger.info("psycopg module not found. Operating in local JSON fallback mode.")

def get_db_connection():
    if not psycopg:
        return None
    try:
        conn = psycopg.connect(CONN_STRING, row_factory=dict_row)
        return conn
    except Exception as e:
        logger.warning(f"Could not connect to PostgreSQL ({e}). Operating in JSON file fallback mode.")
        return None

def init_db():
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cur:
            schema_path = os.path.join(os.path.dirname(__file__), "..", "schema.sql")
            if os.path.exists(schema_path):
                with open(schema_path, "r", encoding="utf-8") as f:
                    cur.execute(f.read())
                conn.commit()
                logger.info("Successfully initialized PostgreSQL schema with pgvector & pg_trgm.")
                return True
    except Exception as e:
        logger.error(f"Failed to initialize PostgreSQL schema: {e}")
    finally:
        conn.close()
    return False

def upsert_section(act_id: int, act_name_en: str, act_name_bn: str, category: str, 
                   sec_num: str, title_en: str, title_bn: str, content_en: str, 
                   content_bn: str, easy_exp_bn: str, url: str):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO acts (act_id, act_name_en, act_name_bn, category, source_url)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (act_id) DO UPDATE SET
                    act_name_en = EXCLUDED.act_name_en,
                    act_name_bn = EXCLUDED.act_name_bn,
                    category = EXCLUDED.category;
            """, (act_id, act_name_en, act_name_bn, category, url))

            cur.execute("""
                INSERT INTO sections (act_id, section_number, section_title_en, section_title_bn, content_en, content_bn, easy_explanation_bn, source_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (act_id, section_number) DO UPDATE SET
                    section_title_en = EXCLUDED.section_title_en,
                    section_title_bn = EXCLUDED.section_title_bn,
                    content_en = EXCLUDED.content_en,
                    content_bn = EXCLUDED.content_bn,
                    easy_explanation_bn = EXCLUDED.easy_explanation_bn;
            """, (act_id, sec_num, title_en, title_bn, content_en, content_bn, easy_exp_bn, url))
            
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"Error upserting section {sec_num} of Act {act_id}: {e}")
    finally:
        conn.close()
    return False

if __name__ == "__main__":
    init_db()
