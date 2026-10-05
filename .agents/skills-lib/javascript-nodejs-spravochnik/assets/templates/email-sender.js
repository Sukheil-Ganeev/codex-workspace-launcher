/**
 * Email Sender Template (SendGrid)
 *
 * Production-ready отправка писем через SendGrid с:
 * - HTML и plain-text версиями
 * - Шаблонами
 * - Вложениями
 * - Отслеживанием открытий/кликов
 * - Error handling и retry logic
 *
 * @example
 * npm install @sendgrid/mail dotenv
 */

const sgMail = require('@sendgrid/mail');

sgMail.setApiKey(process.env.SENDGRID_API_KEY);

// ==================== EMAIL CONFIG ====================

const EMAIL_CONFIG = {
  fromEmail: process.env.FROM_EMAIL || 'noreply@example.com',
  fromName: process.env.FROM_NAME || 'My Company',
  replyToEmail: process.env.REPLY_TO_EMAIL || 'support@example.com',
};

// ==================== BASIC EMAIL ====================

/**
 * Отправить простое письмо
 *
 * @param {Object} options - { to, subject, html, text }
 * @returns {Promise<Object>} SendGrid response
 *
 * @example
 * await sendEmail({
 *   to: 'user@example.com',
 *   subject: 'Welcome',
 *   html: '<h1>Welcome!</h1>',
 *   text: 'Welcome!'
 * });
 */
async function sendEmail(options) {
  try {
    const { to, cc, bcc, subject, html, text, attachments = [] } = options;

    // Валидация
    if (!to || !subject) {
      throw new Error('to and subject are required');
    }

    if (!html && !text) {
      throw new Error('html or text content is required');
    }

    const msg = {
      to,
      cc,
      bcc,
      from: `${EMAIL_CONFIG.fromName} <${EMAIL_CONFIG.fromEmail}>`,
      replyTo: EMAIL_CONFIG.replyToEmail,
      subject,
      text: text || undefined,
      html: html || undefined,
      attachments: attachments.length > 0 ? attachments : undefined,
      trackingSettings: {
        openTracking: {
          enable: true,
        },
        clickTracking: {
          enable: true,
        },
      },
    };

    const response = await sgMail.send(msg);

    console.log(`[Email] Sent to ${to} (${subject})`);
    return {
      success: true,
      messageId: response[0].headers['x-message-id'],
    };
  } catch (error) {
    console.error('[Email] Error:', error.message);
    throw error;
  }
}

// ==================== TEMPLATE EMAIL ====================

/**
 * Отправить письмо с использованием SendGrid template
 *
 * @param {Object} options - { to, templateId, dynamicTemplateData }
 * @returns {Promise<Object>}
 *
 * @example
 * await sendTemplateEmail({
 *   to: 'user@example.com',
 *   templateId: 'd-1234567890abcdef',
 *   dynamicTemplateData: {
 *     firstName: 'John',
 *     bookingId: 'BOOK123'
 *   }
 * });
 */
async function sendTemplateEmail(options) {
  try {
    const { to, cc, bcc, templateId, dynamicTemplateData = {} } = options;

    if (!to || !templateId) {
      throw new Error('to and templateId are required');
    }

    const msg = {
      to,
      cc,
      bcc,
      from: `${EMAIL_CONFIG.fromName} <${EMAIL_CONFIG.fromEmail}>`,
      replyTo: EMAIL_CONFIG.replyToEmail,
      templateId,
      dynamicTemplateData,
    };

    const response = await sgMail.send(msg);

    console.log(`[Email] Template sent to ${to}`);
    return {
      success: true,
      messageId: response[0].headers['x-message-id'],
    };
  } catch (error) {
    console.error('[Email] Template error:', error.message);
    throw error;
  }
}

// ==================== BUSINESS EMAIL TEMPLATES ====================

/**
 * Письмо подтверждения бронирования
 *
 * @param {Object} booking - { id, email, tourName, date, numberOfPeople, totalPrice }
 */
async function sendBookingConfirmation(booking) {
  const html = `
    <h2>Подтверждение бронирования</h2>
    <p>Спасибо за ваше бронирование!</p>
    <ul>
      <li><strong>ID:</strong> ${booking.id}</li>
      <li><strong>Тур:</strong> ${booking.tourName}</li>
      <li><strong>Дата:</strong> ${new Date(booking.date).toLocaleDateString('ru-RU')}</li>
      <li><strong>Участников:</strong> ${booking.numberOfPeople}</li>
      <li><strong>Сумма:</strong> ${booking.totalPrice} AED</li>
    </ul>
    <p>Мы отправим вам дополнительные инструкции на email.</p>
  `;

  return sendEmail({
    to: booking.email,
    subject: `Подтверждение бронирования #${booking.id}`,
    html,
    text: `Подтверждение бронирования #${booking.id}`,
  });
}

/**
 * Письмо о платеже
 */
async function sendPaymentReceipt(payment) {
  const html = `
    <h2>Квитанция об оплате</h2>
    <p>Платеж успешно получен.</p>
    <ul>
      <li><strong>ID платежа:</strong> ${payment.id}</li>
      <li><strong>Сумма:</strong> ${payment.amount} ${payment.currency}</li>
      <li><strong>Дата:</strong> ${new Date().toLocaleDateString('ru-RU')}</li>
      <li><strong>Статус:</strong> ${payment.status}</li>
    </ul>
  `;

  return sendEmail({
    to: payment.email,
    subject: `Квитанция об оплате #${payment.id}`,
    html,
  });
}

/**
 * Письмо об отмене
 */
async function sendCancellationNotice(booking) {
  const html = `
    <h2>Отмена бронирования</h2>
    <p>Ваше бронирование #${booking.id} было отменено.</p>
    <p>Если у вас есть вопросы, свяжитесь с нашей поддержкой.</p>
  `;

  return sendEmail({
    to: booking.email,
    subject: `Отмена бронирования #${booking.id}`,
    html,
  });
}

// ==================== BATCH SENDING ====================

/**
 * Отправить письма нескольким получателям
 * TODO: Использовать SendGrid batch API для больших объемов
 *
 * @param {Object} options - { recipients, subject, html }
 * @returns {Promise<Object>} { sent, failed }
 */
async function sendBatch(options) {
  const { recipients, subject, html, text } = options;

  if (!recipients || recipients.length === 0) {
    throw new Error('recipients is required');
  }

  const results = {
    sent: 0,
    failed: 0,
    errors: [],
  };

  // TODO: Использовать Promise.allSettled для параллельной отправки
  for (const email of recipients) {
    try {
      await sendEmail({
        to: email,
        subject,
        html,
        text,
      });
      results.sent++;
    } catch (error) {
      results.failed++;
      results.errors.push({
        email,
        error: error.message,
      });
    }
  }

  console.log(`[Email] Batch complete: ${results.sent} sent, ${results.failed} failed`);
  return results;
}

// ==================== RETRY LOGIC ====================

/**
 * Отправить с автоматическим retry
 *
 * @param {Object} options - Email options
 * @param {number} maxRetries - Максимум попыток (default: 3)
 * @param {number} delayMs - Задержка между попытками (default: 1000)
 */
async function sendWithRetry(options, maxRetries = 3, delayMs = 1000) {
  let lastError;

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      console.log(`[Email] Attempt ${attempt}/${maxRetries}`);
      return await sendEmail(options);
    } catch (error) {
      lastError = error;
      console.error(`[Email] Attempt ${attempt} failed:`, error.message);

      if (attempt < maxRetries) {
        await new Promise((resolve) => setTimeout(resolve, delayMs * attempt));
      }
    }
  }

  throw lastError;
}

// ==================== EMAIL WITH ATTACHMENT ====================

/**
 * Отправить письмо с вложением
 *
 * @param {Object} options - { to, subject, html, attachmentPath }
 */
async function sendWithAttachment(options) {
  const { to, subject, html, attachmentPath } = options;

  const fs = require('fs');
  const path = require('path');

  try {
    const fileContent = fs.readFileSync(attachmentPath);
    const filename = path.basename(attachmentPath);

    return sendEmail({
      to,
      subject,
      html,
      attachments: [
        {
          content: fileContent.toString('base64'),
          filename,
          type: 'application/pdf',
          disposition: 'attachment',
        },
      ],
    });
  } catch (error) {
    console.error('[Email] Attachment error:', error.message);
    throw error;
  }
}

// ==================== EXPORTS ====================

module.exports = {
  sendEmail,
  sendTemplateEmail,
  sendBookingConfirmation,
  sendPaymentReceipt,
  sendCancellationNotice,
  sendBatch,
  sendWithRetry,
  sendWithAttachment,
};

// Required environment variables:
// SENDGRID_API_KEY=SG.xxxxxxxxxx
// FROM_EMAIL=noreply@example.com
// FROM_NAME=My Company
// REPLY_TO_EMAIL=support@example.com
