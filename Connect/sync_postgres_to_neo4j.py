from neo4j import GraphDatabase
import psycopg2

# Neo4
NEO4J_URI = "bolt://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "12345678"

# PostgreSQL
PG_HOST = "localhost"
PG_PORT = 5432
PG_DBNAME = "data"
PG_USER = "postgres"
PG_PASS = "12345678"

# --- Connect ---
neo = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS)) # Connect to Neo4j
pg = psycopg2.connect(
    host=PG_HOST, port=PG_PORT, dbname=PG_DBNAME,
    user=PG_USER, password=PG_PASS
)
pg.autocommit = True
cur = pg.cursor() # Connect to PostgreSQL

# get data from Neo4j
def export_simple_nodes(tx, label, fields):
    query = f"""
    // get node
    MATCH (n:{label}) 
    // lấy các trường có trong node
    RETURN {', '.join([f"n.{f}" for f in fields])}
    """
    return [tuple(r.values()) for r in tx.run(query)]

# lấy dữ liệu bài học kèm theo topic_id thông qua quan hệ HAS_LESSON
def export_lessons_with_topic(tx):
    query = """
    MATCH (t:Topic)-[:HAS_LESSON]->(l:Lesson)
    RETURN 
        l.lesson_id AS lesson_id,
        l.lesson_name AS lesson_name,
        COALESCE(l.lesson_url, '') AS lesson_url,
        t.topic_id AS topic_id
    ORDER BY lesson_id
    """
    return [tuple(r.values()) for r in tx.run(query)]


# --------------------- INSERT INTO POSTGRES ---------------------
def insert_rows(table, fields, rows):
    """Insert or update rows into PostgreSQL"""
    placeholders = ", ".join(["%s"] * len(fields))
    field_names = ", ".join(fields)

    # Nếu trùng khóa chính → UPDATE các cột khác
    sql = f"""
        INSERT INTO {table} ({field_names})
        VALUES ({placeholders})
        ON CONFLICT ({fields[0]})
        DO UPDATE SET {', '.join([f"{f}=EXCLUDED.{f}" for f in fields[1:]])};
    """

    for row in rows:
        cur.execute(sql, row)


# main
with neo.session() as session:
    print("Exporting from Neo4j")

    subjects = export_simple_nodes(session, "Subject", ["subject_id", "subject_name"])
    classes = export_simple_nodes(session, "Class", ["class_id", "class_name", "class_url"])
    topics = export_simple_nodes(session, "Topic", ["topic_id", "topic_name", "topic_url"])
    lessons = export_lessons_with_topic(session)

    print(f"Subjects: {len(subjects)} | Classes: {len(classes)} | Topics: {len(topics)} | Lessons: {len(lessons)}")

    print("Insert into PostgreSQL...")
    insert_rows("subjects", ["subject_id", "subject_name"], subjects)
    insert_rows("classes", ["class_id", "class_name", "class_url"], classes)
    insert_rows("topics", ["topic_id", "topic_name", "topic_url"], topics)
    insert_rows("lessons", ["lesson_id", "lesson_name", "lesson_url", "topic_id"], lessons)

pg.close()
neo.close()
print("Export completed successfully!")
