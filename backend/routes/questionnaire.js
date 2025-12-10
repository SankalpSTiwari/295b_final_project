const express = require('express');
const md5 = require('md5');
const jwt = require('jsonwebtoken');

const router = express.Router();
const HttpCodes = require('../enums/http-codes');
require('dotenv/config');
const pool = require('../mysql_db');

// Sign In Questionairre
router.post('/submit_signin_ques', async (req, res) => {
  // Extract values from the request body
  const { user_id, mood, recommOption, chipGroup, chipTime } = req.body;

  // Check if any of the required fields are empty
  if (!user_id || !mood || !recommOption || !chipGroup || !chipTime) {
    return res
      .status(HttpCodes.BadRequest)
      .json({ errmessage: 'Please fill out all the fields.' });
  }

  try {
    // Prepare the SQL query with updated UPSERT logic using an alias
    const upsertSql = `
      INSERT INTO questionnaire_responses(user_id, mood, interest, with_whom, time_preference)
      VALUES (?, ?, ?, ?, ?) AS new_values(user_id, mood, interest, with_whom, time_preference)
      ON DUPLICATE KEY UPDATE
        mood = new_values.mood,
        interest = new_values.interest,
        with_whom = new_values.with_whom,
        time_preference = new_values.time_preference;
    `;
    const values = [user_id, mood, recommOption, chipGroup, chipTime];

    const connection = await pool.getConnection();
    try {
      await connection.beginTransaction();
      const [results] = await connection.query(upsertSql, values);
      if (!results || results.affectedRows === 0) {
        throw new Error('No changes were made to the questionnaire response.');
      }
      await connection.commit();
      res.status(HttpCodes.OK).json({
        message: 'Questionnaire responses updated successfully.',
      });
    } catch (err) {
      await connection.rollback();
      res
        .status(HttpCodes.InternalServerError)
        .json({ errmessage: err.message || 'Failed to save questionnaire' });
    } finally {
      connection.release();
    }
  } catch (err) {
    console.error(err);
    res.status(HttpCodes.InternalServerError).json({ errmessage: 'Error updating questionnaire responses.' });
  }
});


// POST API to handle signup questionnaire submission
// Signup
router.post('/submit_signup_ques', async (req, res) => {
  const { user_id, happy_movie, sad_movie, neutral_movie } = req.body;

  // Check for required fields
  if (!user_id || !happy_movie || !sad_movie || !neutral_movie) {
    return res
      .status(HttpCodes.BadRequest)
      .json({ errmessage: 'Please provide all required fields' });
  }

  try {
    // Prepare the SQL query with UPSERT logic
    const upsertSql = `
      INSERT INTO genre_preferences (user_id, happy_movie, sad_movie, neutral_movie)
      VALUES (?, ?, ?, ?) AS new_values(user_id, happy_movie, sad_movie, neutral_movie)
      ON DUPLICATE KEY UPDATE
        happy_movie = new_values.happy_movie,
        sad_movie = new_values.sad_movie,
        neutral_movie = new_values.neutral_movie;
    `;
    const values = [user_id, happy_movie, sad_movie, neutral_movie];

    const connection = await pool.getConnection();
    try {
      await connection.beginTransaction();
      const [results] = await connection.query(upsertSql, values);
      if (!results || results.affectedRows === 0) {
        throw new Error('No changes were made to your movie preferences.');
      }
      await connection.commit();
      res.status(HttpCodes.OK).json({
        message: 'Movie preferences updated successfully.',
      });
    } catch (err) {
      await connection.rollback();
      res.status(HttpCodes.InternalServerError).json({ errmessage: err.message || 'Failed to save preferences' });
    } finally {
      connection.release();
    }
  } catch (err) {
    console.error(err);
    res.status(HttpCodes.InternalServerError).json({ errmessage: 'Error updating movie preferences.' });
  }
});

module.exports = router;
