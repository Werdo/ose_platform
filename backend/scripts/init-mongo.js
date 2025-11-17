// ════════════════════════════════════════════════════════════════════════════
// OSE PLATFORM - MongoDB Initialization Script
// ════════════════════════════════════════════════════════════════════════════
//
// Este script se ejecuta automáticamente la primera vez que se inicia MongoDB
// Crea la base de datos y usuarios
// Los índices y colecciones se crean automáticamente por Beanie
//
// ════════════════════════════════════════════════════════════════════════════

print("════════════════════════════════════════════════════════════════");
print("  OSE PLATFORM - Initializing MongoDB");
print("════════════════════════════════════════════════════════════════");

// Leer variables de entorno (inyectadas por Docker)
const dbName = process.env.MONGO_INITDB_DATABASE || 'oversun_production';
const rootUser = process.env.MONGO_INITDB_ROOT_USERNAME;
const rootPassword = process.env.MONGO_INITDB_ROOT_PASSWORD;

// Conectar a la base de datos
db = db.getSiblingDB(dbName);

print("\n[1/2] Creating database: " + dbName);

// ════════════════════════════════════════════════════════════════════════════
// USUARIOS
// ════════════════════════════════════════════════════════════════════════════

print("\n[2/2] Creating users...");

// Crear usuario de aplicación
const adminDb = db.getSiblingDB('admin');

try {
  adminDb.createUser({
    user: "ose_user",
    pwd: "ose_secure_pass_2025",
    roles: [
      { role: "readWrite", db: dbName },
      { role: "dbAdmin", db: dbName }
    ]
  });
  print("  ✓ Created application user: ose_user");
} catch (e) {
  print("  ⚠ User already exists or error: " + e);
}

// Crear usuario de solo lectura (opcional, para reportes)
try {
  adminDb.createUser({
    user: "ose_readonly",
    pwd: "ose_readonly_pass",
    roles: [
      { role: "read", db: dbName }
    ]
  });
  print("  ✓ Created readonly user: ose_readonly");
} catch (e) {
  print("  ⚠ User already exists or error: " + e);
}

// ════════════════════════════════════════════════════════════════════════════
// FINALIZACIÓN
// ════════════════════════════════════════════════════════════════════════════

print("\n════════════════════════════════════════════════════════════════");
print("  ✓ MongoDB initialization completed successfully!");
print("  Database: " + dbName);
print("  Users created:");
print("    - ose_user (readWrite, dbAdmin)");
print("    - ose_readonly (read)");
print("  Note: Collections and indexes will be created by Beanie");
print("════════════════════════════════════════════════════════════════\n");
