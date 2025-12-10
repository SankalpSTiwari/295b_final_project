const express = require('express');
const md5 = require('md5');
const jwt = require('jsonwebtoken');

const router = express.Router();
const HttpCodes = require('../enums/http-codes');
require('dotenv/config');
const pool = require('../mysql_db');

//User Login for Stress Mang App:
router.post('/', async (req, res) => {
  console.log('inside login');
  const { email, password } = req.body;
  if (email == '' || password == '') {
    res
      .status(HttpCodes.BadRequest)
      .send({ errmessage: 'Please enter all the credential details' });
    return;
  }

  const sql = 'SELECT * from user_data where email=? and password=?';
  let connection;
  try {
    connection = await pool.getConnection();
    const [results] = await connection.query(sql, [
      req.body.email,
      md5(req.body.password),
    ]);
    if (!results || results.length === 0) {
      throw new Error('Invalid credentials');
    }
    const payload = { user_id: results[0].id };
    console.log('PAYLOAD+++', payload);
    const token = jwt.sign(payload, process.env.Secret, {
      expiresIn: 60 * 60,
    });
    res.status(HttpCodes.OK).send({ jwt: `JWT ${token}` });
  } catch (err) {
    res.status(HttpCodes.InternalServerError).json({ errmessage: err.message || 'Login failed' });
  } finally {
    if (connection && connection.release) connection.release();
  }
});

// User Login
router.post('/testlogin', async (req, res) => {
  console.log('inside login');
  const { email, password } = req.body;
  if (email == '' || password == '') {
    res
      .status(HttpCodes.BadRequest)
      .send({ errmessage: 'Please enter all the credential details' });
    return;
  }

  const sql = 'SELECT * from users where email=? and password=?';
  let connection;
  try {
    connection = await pool.getConnection();
    const [results] = await connection.query(sql, [
      req.body.email,
      md5(req.body.password),
    ]);
    if (!results || results.length === 0) {
      throw new Error('Invalid credentials');
    }
    const payload = { user_id: results[0].id };
    console.log('PAYLOAD+++', payload);
    const token = jwt.sign(payload, process.env.Secret, {
      expiresIn: 60 * 60,
    });
    res.status(HttpCodes.OK).send({ jwt: `JWT ${token}` });
  } catch (err) {
    res.status(HttpCodes.InternalServerError).json({ errmessage: err.message || 'Login failed' });
  } finally {
    if (connection && connection.release) connection.release();
  }
});

// Admin Login
router.post('/adminlogin', async (req, res) => {
  console.log('inside adminlogin');
  const { email, password } = req.body;
  if (email == '' || password == '') {
    res
      .status(HttpCodes.BadRequest)
      .send({ errmessage: 'Please enter all the credential details' });
    return;
  }

  const adminloginsql = 'SELECT * from admin where email=? and password=?';
  let connection;
  try {
    connection = await pool.getConnection();
    const [results] = await connection.query(adminloginsql, [
      req.body.email,
      req.body.password,
    ]);
    if (!results || results.length === 0) {
      throw new Error('Invalid credentials');
    }
    const payload = { admin_id: results[0].admin_id };
    console.log('PAYLOAD+++', payload);
    const token = jwt.sign(payload, process.env.Secret, {
      expiresIn: 60 * 60,
    });
    res.status(HttpCodes.OK).send({ jwt: `JWT ${token}` });
  } catch (err) {
    res.status(HttpCodes.InternalServerError).json({ errmessage: err.message || 'Login failed' });
  } finally {
    if (connection && connection.release) connection.release();
  }
});

module.exports = router;
