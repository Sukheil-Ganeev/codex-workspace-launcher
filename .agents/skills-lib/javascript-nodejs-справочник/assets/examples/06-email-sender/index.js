const express = require('express');
const nodemailer = require('nodemailer');
require('dotenv').config();

const transporter = nodemailer.createTransport({
  host: process.env.SMTP_HOST,
  port: parseInt(process.env.SMTP_PORT),
  secure: true,
  auth: {
    user: process.env.SMTP_USER,
    pass: process.env.SMTP_PASSWORD
  }
});

const app = express();
app.use(express.json());

app.post('/send-email', async (req, res) => {
  try {
    const { to, subject, template } = req.body;

    await transporter.sendMail({
      from: process.env.FROM_EMAIL,
      to,
      subject,
      html: template
    });

    res.json({ status: 'sent' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(3000, () => console.log('Email service running'));
module.exports = app;
