"""
OSE Platform - PostgreSQL to MongoDB Incremental Sync
Sincroniza solo los registros nuevos desde PostgreSQL a MongoDB

Usage:
    python scripts/sync_postgresql_incremental.py
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

# Configuración de tablas y sus campos únicos
# Solo incluimos tablas con identificadores únicos numéricos que permiten sincronización incremental
TABLE_CONFIG = {
    # Tablas principales con campo 'nro' (las 3 más importantes con más de 230k registros)
    'registros_2025': {'unique_field': 'nro'},
    'registros_2025_puesto2': {'unique_field': 'nro'},
    'oem_registros': {'unique_field': 'nro'},
    # Tabla de administración
    'personal_admin': {'unique_field': 'nro'},
}


def get_max_value_in_mongodb(collection, field_name):
    """Obtiene el valor máximo de un campo en MongoDB"""
    try:
        result = collection.find_one(
            sort=[(field_name, -1)],
            projection={field_name: 1, '_id': 0}
        )
        if result and field_name in result:
            return result[field_name]
        return 0
    except Exception as e:
        print(f'    [WARNING] Could not get max value: {e}')
        return 0


def sync_table_incremental(pg_cursor, mongo_db, table_name, config):
    """Sincroniza una tabla de forma incremental"""
    unique_field = config['unique_field']
    collection_name = f'pg_{table_name}'
    collection = mongo_db[collection_name]

    print(f'Processing table: {table_name}')

    # Obtener el valor máximo en MongoDB
    max_value_in_mongo = get_max_value_in_mongodb(collection, unique_field)
    print(f'  Max {unique_field} in MongoDB: {max_value_in_mongo}')

    # Contar registros nuevos en PostgreSQL
    pg_cursor.execute(f'''
        SELECT COUNT(*)
        FROM {POSTGRESQL_CONFIG["schema"]}.{table_name}
        WHERE {unique_field} > {max_value_in_mongo}
    ''')
    new_records_count = pg_cursor.fetchone()[0]

    print(f'  New records in PostgreSQL: {new_records_count:,}')

    if new_records_count == 0:
        print(f'  Status: UP TO DATE (no new records)')
        print()
        return 0

    # Obtener nombres de columnas
    pg_cursor.execute(f'SELECT * FROM {POSTGRESQL_CONFIG["schema"]}.{table_name} LIMIT 0')
    columns = [desc[0] for desc in pg_cursor.description]

    # Crear índice en MongoDB si no existe
    try:
        collection.create_index([(unique_field, 1)], unique=True)
    except:
        pass  # El índice ya existe

    # Fetch nuevos registros en lotes
    offset = 0
    total_inserted = 0

    while True:
        pg_cursor.execute(f'''
            SELECT *
            FROM {POSTGRESQL_CONFIG["schema"]}.{table_name}
            WHERE {unique_field} > {max_value_in_mongo}
            ORDER BY {unique_field} ASC
            LIMIT {BATCH_SIZE} OFFSET {offset}
        ''')
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

        # Insert batch into MongoDB (usando insert_many con ordered=False para continuar si hay duplicados)
        if documents:
            try:
                result = collection.insert_many(documents, ordered=False)
                total_inserted += len(result.inserted_ids)
            except Exception as e:
                # Algunos documentos pueden fallar por duplicados, contar los exitosos
                if hasattr(e, 'details') and 'writeErrors' in e.details:
                    errors = len(e.details['writeErrors'])
                    successful = len(documents) - errors
                    total_inserted += successful
                    print(f'    [INFO] Batch: {successful} inserted, {errors} duplicates skipped')
                else:
                    raise e

        offset += BATCH_SIZE

        # Progress indicator for large tables
        if new_records_count > BATCH_SIZE:
            progress = min(100, (total_inserted * 100) // new_records_count)
            print(f'  Progress: {total_inserted:,}/{new_records_count:,} ({progress}%)')

    print(f'  Inserted {total_inserted:,} new records into collection: {collection_name}')
    print(f'  Status: SUCCESS')
    print()

    return total_inserted


def main():
    """Main sync function"""
    print('=' * 80)
    print('PostgreSQL to MongoDB - INCREMENTAL SYNC')
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
    print(f'Mode: INCREMENTAL (only new records)')
    print('=' * 80)
    print()

    pg_cursor = pg_conn.cursor()

    sync_stats = {
        'total_tables': len(TABLE_CONFIG),
        'synced_tables': 0,
        'total_new_records': 0,
        'up_to_date_tables': 0,
        'failed_tables': []
    }

    for table_name, config in TABLE_CONFIG.items():
        try:
            new_records = sync_table_incremental(pg_cursor, mongo_db, table_name, config)

            if new_records > 0:
                sync_stats['synced_tables'] += 1
                sync_stats['total_new_records'] += new_records
            else:
                sync_stats['up_to_date_tables'] += 1

        except Exception as e:
            print(f'  Status: FAILED - {str(e)}')
            sync_stats['failed_tables'].append({'table': table_name, 'error': str(e)})
            print()
            continue

    # Close connections
    pg_cursor.close()
    pg_conn.close()
    mongo_client.close()

    # Print summary
    print('=' * 80)
    print('Sync Summary')
    print('=' * 80)
    print(f'Total tables: {sync_stats["total_tables"]}')
    print(f'Tables with new data: {sync_stats["synced_tables"]}')
    print(f'Tables up to date: {sync_stats["up_to_date_tables"]}')
    print(f'Failed: {len(sync_stats["failed_tables"])}')
    print(f'Total new records synced: {sync_stats["total_new_records"]:,}')
    print('=' * 80)

    if sync_stats['failed_tables']:
        print()
        print('Failed Tables:')
        for failure in sync_stats['failed_tables']:
            print(f'  - {failure["table"]}: {failure["error"]}')

    print()
    if len(sync_stats['failed_tables']) == 0:
        if sync_stats['total_new_records'] > 0:
            print(f'[SUCCESS] Sync completed! {sync_stats["total_new_records"]:,} new records added.')
        else:
            print('[SUCCESS] Sync completed! All tables are up to date.')
        return True
    else:
        print('[WARNING] Sync completed with errors')
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
