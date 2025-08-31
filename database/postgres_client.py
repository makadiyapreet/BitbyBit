import os
import psycopg2
import psycopg2.extras

class PostgresClient:
    def __init__(self):
        self.host = os.getenv('POSTGRES_HOST', 'localhost')
        self.dbname = os.getenv('POSTGRES_DB', 'coastal_threats')
        self.user = os.getenv('POSTGRES_USER', 'postgres')
        self.password = os.getenv('POSTGRES_PASSWORD', 'postgres')
        self.port = os.getenv('POSTGRES_PORT', 5432)
        self.conn = None

    def connect(self):
        if self.conn is None or self.conn.closed:
            self.conn = psycopg2.connect(
                host=self.host,
                database=self.dbname,
                user=self.user,
                password=self.password,
                port=self.port
            )

    def execute(self, query, params=None):
        self.connect()
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, params)
            self.conn.commit()

    def query(self, query, params=None):
        self.connect()
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, params)
            results = cur.fetchall()
        return results

    def insert_alert(self, alert_data):
        # Expects: dict with keys (id, timestamp, location, threat_type, severity_score, recommendations, data)
        self.execute(
            """
            INSERT INTO threat_alerts
            (id, timestamp, location, threat_type, severity_score, recommendations, raw_data)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
            """,
            (
                alert_data['id'],
                alert_data['timestamp'],
                alert_data['location'],
                alert_data['threat_type'],
                alert_data['severity_score'],
                alert_data.get('recommendations', []),
                str(alert_data.get('data', {}))
            )
        )

    def get_alerts(self, limit=100):
        return self.query(
            "SELECT * FROM threat_alerts ORDER BY timestamp DESC LIMIT %s", (limit,)
        )

    def close(self):
        if self.conn and not self.conn.closed:
            self.conn.close()

# Singleton instance
postgres_client = PostgresClient()

# Example Table schema (run in psql):
# CREATE TABLE IF NOT EXISTS threat_alerts (
#     id TEXT PRIMARY KEY,
#     timestamp TIMESTAMP,
#     location TEXT,
#     threat_type TEXT,
#     severity_score REAL,
#     recommendations TEXT[],
#     raw_data TEXT
# );
