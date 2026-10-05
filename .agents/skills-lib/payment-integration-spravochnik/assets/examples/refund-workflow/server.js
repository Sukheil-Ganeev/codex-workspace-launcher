#!/usr/bin/env node

/**
 * Refund Workflow - Full & Partial Refunds
 * Handles refund requests with approval process
 */

require('dotenv').config();
const express = require('express');
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

const app = express();
app.use(express.json());

// In-memory refund requests (use DB in production)
const refundRequests = new Map();

/**
 * Request refund
 */
app.post('/request-refund', async (req, res) => {
  const { paymentIntentId, amount, reason, customerEmail } = req.body;

  const requestId = 'REF-' + Date.now();

  refundRequests.set(requestId, {
    id: requestId,
    paymentIntentId,
    amount,
    reason,
    customerEmail,
    status: 'pending',
    createdAt: new Date(),
  });

  res.json({ requestId, status: 'pending', message: 'Refund request submitted' });
});

/**
 * Approve and process refund
 */
app.post('/approve-refund/:requestId', async (req, res) => {
  const { requestId } = req.params;
  const request = refundRequests.get(requestId);

  if (!request) return res.status(404).json({ error: 'Request not found' });
  if (request.status !== 'pending') return res.status(400).json({ error: 'Already processed' });

  try {
    const refund = await stripe.refunds.create({
      payment_intent: request.paymentIntentId,
      amount: request.amount,
      reason: 'requested_by_customer',
      metadata: { request_id: requestId },
    });

    request.status = 'approved';
    request.refundId = refund.id;

    res.json({ success: true, refund });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * Reject refund
 */
app.post('/reject-refund/:requestId', async (req, res) => {
  const { requestId } = req.params;
  const { rejectionReason } = req.body;
  const request = refundRequests.get(requestId);

  if (!request) return res.status(404).json({ error: 'Request not found' });

  request.status = 'rejected';
  request.rejectionReason = rejectionReason;

  res.json({ success: true });
});

/**
 * List pending refunds
 */
app.get('/pending-refunds', (req, res) => {
  const pending = Array.from(refundRequests.values()).filter(r => r.status === 'pending');
  res.json(pending);
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`💸 Refund system on port ${PORT}`));
