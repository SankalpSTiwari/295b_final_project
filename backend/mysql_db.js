// MySQL connection pool (mysql2/promise) configured via env in routes/config.js
const mysql = require('mysql2/promise');
const dbConfig = require('./routes/config');

// Create a promise-based pool
const pool = mysql.createPool(dbConfig);

// Provide a thenable interface for legacy pool.then(...) usage
pool.then = (cb) => Promise.resolve(pool).then(cb);

module.exports = pool;
