"""
OSE Platform - PostgreSQL to MongoDB Migration Script
Migrates all tables from PostgreSQL (algepser schema) to MongoDB

Usage:
    python scripts/migrate_postgresql.py
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
from pymongo import MongoClient
from app.config import get_settings

# Configuration
POSTGRESQL_CONFIG = {
    'host': '192.168.100.118',
    'port': 5432,
    'database': 'postgres',
    'user': 'panda',
    'password': 'f2e2l1i9x6',
    'schema': 'algepser'
}

BATCH_SIZE = 10000  # Number of records to process per batch


def main():
    """Main migration function"""
    print('=' * 80)
    print('PostgreSQL to MongoDB Migration')
    print('=' * 80)
    print()

    # Get MongoDB configuration from settings
    settings = get_settings()

    # PostgreSQL connection
    try:
        pg_conn = psycopg2.connect(
            host=POSTGRESQL_CONFIG['host'],
            port=POSTGRESQL_CONFIG['port'],
            database=POSTGRESQL_CONFIG['database'],
            user=POSTGRESQL_CONFIG['user'],
            password=POSTGRESQL_CONFIG['password'],
            connect_timeout=10
        )
        print(f'[OK] PostgreSQL connection: {POSTGRESQL_CONFIG["host"]}:{POSTGRESQL_CONFIG["port"]}')
    except Exception as e:
        print(f'[ERROR] PostgreSQL connection failed: {e}')
        return False

    # MongoDB connection
    try:
        mongo_client = MongoClient(settings.MONGODB_URI)
        mongo_db = mongo_client[settings.MONGODB_DB_NAME]
        print(f'[OK] MongoDB connection: {settings.MONGODB_URI}')
    except Exception as e:
        print(f'[ERROR] MongoDB connection failed: {e}')
        pg_conn.close()
        return False

    print()
    print('=' * 80)
    print(f'Source: PostgreSQL at {POSTGRESQL_CONFIG["host"]}, schema {POSTGRESQL_CONFIG["schema"]}')
    print(f'Target: MongoDB at {settings.MONGODB_URI}, database {settings.MONGODB_DB_NAME}')
    print('=' * 80)
    print()

    pg_cursor = pg_conn.cursor()

    # Get all tables from algepser schema
    pg_cursor.execute(f"""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = '{POSTGRESQL_CONFIG["schema"]}'
        ORDER BY table_name
    """)

    tables = [row[0] for row in pg_cursor.fetchall()]
    print(f'Tables to migrate: {len(tables)}')
    print()

    migration_stats = {
        'total_tables': len(tables),
        'migrated_tables': 0,
        'total_records': 0,
        'skipped_tables': 0,
        'failed_tables': []
    }

    for table_name in tables:
        try:
            print(f'Processing table: {table_name}')

            # Get row count
            pg_cursor.execute(f'SELECT COUNT(*) FROM {POSTGRESQL_CONFIG["schema"]}.{table_name}')
            row_count = pg_cursor.fetchone()[0]
            print(f'  Records to migrate: {row_count:,}')

            if row_count == 0:
                print(f'  Skipped (empty table)')
                migration_stats['skipped_tables'] += 1
                print()
                continue

            # Get column names
            pg_cursor.execute(f'SELECT * FROM {POSTGRESQL_CONFIG["schema"]}.{table_name} LIMIT 0')
            columns = [desc[0] for desc in pg_cursor.description]

            # Fetch all data in batches for large tables
            offset = 0
            total_inserted = 0

            collection_name = f'pg_{table_name}'
            collection = mongo_db[collection_name]

            # Delete existing documents if collection exists (without drop)
            try:
                deleted = collection.delete_many({})
                if deleted.deleted_count > 0:
                    print(f'  Cleared {deleted.deleted_count} existing documents')
            except:
                pass  # Collection may not exist yet

            while True:
                pg_cursor.execute(
                    f'SELECT * FROM {POSTGRESQL_CONFIG["schema"]}.{table_name} '
                    f'LIMIT {BATCH_SIZE} OFFSET {offset}'
                )
                rows = pg_cursor.fetchall()

                if not rows:
                    break

                # Prepare MongoDB documents
                documents = []
                for row in rows:
                    doc = {}
                    for i, col in enumerate(columns):
                        value = row[i]
                        # Convert datetime objects to ISO format
                        if isinstance(value, datetime):
                            doc[col] = value.isoformat()
                        else:
                            doc[col] = value

                    # Add migration metadata
                    doc['_migrated_from'] = 'postgresql'
                    doc['_migrated_at'] = datetime.now().isoformat()
                    doc['_original_table'] = table_name

                    documents.append(doc)

                # Insert batch into MongoDB
                if documents:
                    result = collection.insert_many(documents)
                    total_inserted += len(result.inserted_ids)

                offset += BATCH_SIZE

                # Progress indicator for large tables
                if row_count > BATCH_SIZE:
                    progress = min(100, (total_inserted * 100) // row_count)
                    print(f'  Progress: {total_inserted:,}/{row_count:,} ({progress}%)')

            print(f'  Migrated {total_inserted:,} records to collection: {collection_name}')

            migration_stats['migrated_tables'] += 1
            migration_stats['total_records'] += total_inserted

            print(f'  Status: SUCCESS')
            print()

        except Exception as e:
            print(f'  Status: FAILED - {str(e)}')
            migration_stats['failed_tables'].append({'table': table_name, 'error': str(e)})
            print()
            continue

    # Close connections
    pg_cursor.close()
    pg_conn.close()
    mongo_client.close()

    # Print summary
    print('=' * 80)
    print('Migration Summary')
    print('=' * 80)
    print(f'Total tables: {migration_stats["total_tables"]}')
    print(f'Successfully migrated: {migration_stats["migrated_tables"]}')
    print(f'Skipped (empty): {migration_stats["skipped_tables"]}')
    print(f'Failed: {len(migration_stats["failed_tables"])}')
    print(f'Total records migrated: {migration_stats["total_records"]:,}')
    print('=' * 80)

    if migration_stats['failed_tables']:
        print()
        print('Failed Tables:')
        for failure in migration_stats['failed_tables']:
            print(f'  - {failure["table"]}: {failure["error"]}')

    print()
    if len(migration_stats['failed_tables']) == 0:
        print('[SUCCESS] Migration completed successfully!')
        return True
    else:
        print('[WARNING] Migration completed with errors')
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
