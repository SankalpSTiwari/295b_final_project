// MySQL connection settings (env-driven so you can point to a new DB)
const dbConfig = {
  connectionLimit: 20, // default 10
  host: process.env.DB_HOST || 'dbfinalproject.cpcem4w6a78y.us-east-1.rds.amazonaws.com',
  port: process.env.DB_PORT || '3306',
  user: process.env.DB_USER || 'admin',
  password: process.env.DB_PASSWORD || '295bfinalproject',
  database: process.env.DB_NAME || 'finaldb',
};

module.exports = dbConfig;