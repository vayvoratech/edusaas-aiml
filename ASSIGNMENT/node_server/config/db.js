const { Pool } = require("pg");

const pool = new Pool({
    host: process.env.DB_HOST || "localhost",
    port: process.env.DB_PORT || 5432,
    database: process.env.DB_NAME || "education_db",
    user: process.env.DB_USER || "postgres",
    password: process.env.DB_PASSWORD || "postgres"
});

pool.on("connect", (client) => {
    // Automatically default queries to the education schema
    client.query("SET search_path TO education, public");
});

pool.on("error", (err) => {
    console.error("PostgreSQL pool connection error:", err);
});

module.exports = pool;