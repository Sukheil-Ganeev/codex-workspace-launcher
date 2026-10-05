/**
 * Split Payment Calculator Template
 *
 * Calculate and manage split payments for group bookings.
 * Perfect for yacht charters, group tours, or any multi-passenger bookings.
 *
 * Features:
 * - Equal or custom splits
 * - Per-person calculation with VAT
 * - Payment tracking (who paid, who's pending)
 * - Generate individual payment links
 * - Auto-confirm when all paid
 *
 * Usage:
 *   const split = new SplitPayment({
 *     totalAmount: 2500,
 *     participants: 5,
 *     description: 'Luxury Yacht Charter',
 *     bookingId: 'BOOK-12345'
 *   });
 *
 *   const links = await split.generatePaymentLinks();
 *   const status = split.getPaymentStatus();
 */

require('dotenv').config();
const crypto = require('crypto');
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
// const db = require('./database');

class SplitPayment {
  constructor(options) {
    const {
      totalAmount,
      participants, // Array of participant objects or number
      description,
      bookingId,
      includeVAT = true,
      customSplits = null, // Optional: custom amounts per person
      organizerEmail = null,
    } = options;

    this.totalAmount = totalAmount;
    this.participants = Array.isArray(participants)
      ? participants
      : this.createParticipantList(participants);
    this.description = description;
    this.bookingId = bookingId;
    this.includeVAT = includeVAT;
    this.customSplits = customSplits;
    this.organizerEmail = organizerEmail;

    // Calculate splits
    this.calculateSplits();
  }

  /**
   * Create participant list from number
   */
  createParticipantList(count) {
    return Array.from({ length: count }, (_, i) => ({
      id: crypto.randomBytes(8).toString('hex'),
      name: `Participant ${i + 1}`,
      email: null,
      phone: null,
      status: 'pending',
    }));
  }

  /**
   * Calculate split amounts
   */
  calculateSplits() {
    const count = this.participants.length;

    if (this.customSplits) {
      // Use custom split amounts
      this.participants = this.participants.map((p, i) => ({
        ...p,
        amount: this.customSplits[i],
      }));
    } else {
      // Equal split
      const amountPerPerson = this.totalAmount / count;

      // Round to avoid floating point issues
      const roundedAmount = Math.round(amountPerPerson * 100) / 100;

      // Calculate remainder to assign to first person
      const remainder =
        this.totalAmount - roundedAmount * count;

      this.participants = this.participants.map((p, i) => ({
        ...p,
        amount: i === 0 ? roundedAmount + remainder : roundedAmount,
      }));
    }

    // Add VAT if needed
    if (this.includeVAT) {
      this.participants = this.participants.map((p) => {
        const vat = Math.round(p.amount * 0.05 * 100) / 100; // 5% VAT
        return {
          ...p,
          subtotal: p.amount,
          vat: vat,
          amount: p.amount + vat,
        };
      });
    }

    // Verify total (should match original with VAT)
    const calculatedTotal = this.participants.reduce(
      (sum, p) => sum + p.amount,
      0
    );
    const expectedTotal = this.includeVAT
      ? this.totalAmount * 1.05
      : this.totalAmount;

    console.log('Split calculation:', {
      originalTotal: this.totalAmount,
      includeVAT: this.includeVAT,
      expectedTotal: expectedTotal.toFixed(2),
      calculatedTotal: calculatedTotal.toFixed(2),
      participants: this.participants.length,
    });
  }

  /**
   * Generate payment links for all participants
   */
  async generatePaymentLinks() {
    const links = [];

    for (const participant of this.participants) {
      try {
        const session = await stripe.checkout.sessions.create({
          mode: 'payment',
          line_items: [
            {
              price_data: {
                currency: 'aed',
                product_data: {
                  name: this.description,
                  description: `Split payment (${participant.name})`,
                },
                unit_amount: Math.round(participant.amount * 100), // Convert to fils
              },
              quantity: 1,
            },
          ],
          customer_email: participant.email,
          metadata: {
            booking_id: this.bookingId,
            participant_id: participant.id,
            participant_name: participant.name,
            split_payment: 'true',
          },
          success_url: `${process.env.BASE_URL}/payment-success?session_id={CHECKOUT_SESSION_ID}`,
          cancel_url: `${process.env.BASE_URL}/payment-cancelled`,
        });

        participant.paymentLink = session.url;
        participant.sessionId = session.id;

        links.push({
          participantId: participant.id,
          name: participant.name,
          amount: participant.amount,
          link: session.url,
        });
      } catch (err) {
        console.error(
          `Failed to create link for ${participant.name}:`,
          err.message
        );
      }
    }

    // Save to database
    // await db.query(
    //   'INSERT INTO split_payments (booking_id, participants, created_at) VALUES (?, ?, NOW())',
    //   [this.bookingId, JSON.stringify(this.participants)]
    // );

    return links;
  }

  /**
   * Mark participant as paid
   */
  async markPaid(participantId, paymentIntentId) {
    const participant = this.participants.find((p) => p.id === participantId);

    if (!participant) {
      throw new Error('Participant not found');
    }

    participant.status = 'paid';
    participant.paymentIntentId = paymentIntentId;
    participant.paidAt = new Date();

    // Update database
    // await db.query(
    //   'UPDATE split_payments SET participants = ? WHERE booking_id = ?',
    //   [JSON.stringify(this.participants), this.bookingId]
    // );

    // Check if all paid
    if (this.isFullyPaid()) {
      await this.confirmBooking();
    }

    return this.getPaymentStatus();
  }

  /**
   * Check if all participants paid
   */
  isFullyPaid() {
    return this.participants.every((p) => p.status === 'paid');
  }

  /**
   * Get payment status summary
   */
  getPaymentStatus() {
    const paid = this.participants.filter((p) => p.status === 'paid').length;
    const pending = this.participants.length - paid;
    const totalPaid = this.participants
      .filter((p) => p.status === 'paid')
      .reduce((sum, p) => sum + p.amount, 0);
    const totalPending = this.participants
      .filter((p) => p.status === 'pending')
      .reduce((sum, p) => sum + p.amount, 0);

    return {
      totalParticipants: this.participants.length,
      paid,
      pending,
      totalPaid: totalPaid.toFixed(2),
      totalPending: totalPending.toFixed(2),
      isFullyPaid: this.isFullyPaid(),
      participants: this.participants.map((p) => ({
        name: p.name,
        amount: p.amount,
        status: p.status,
        paidAt: p.paidAt,
      })),
    };
  }

  /**
   * Confirm booking when all paid
   */
  async confirmBooking() {
    console.log('All participants paid! Confirming booking:', this.bookingId);

    // Update booking status
    // await db.query(
    //   'UPDATE bookings SET payment_status = ?, confirmed_at = NOW() WHERE id = ?',
    //   ['fully_paid', this.bookingId]
    // );

    // Send confirmation to organizer
    // if (this.organizerEmail) {
    //   await emailService.sendBookingConfirmation({
    //     email: this.organizerEmail,
    //     bookingId: this.bookingId,
    //     participants: this.participants,
    //   });
    // }
  }

  /**
   * Generate WhatsApp message for a participant
   */
  generateWhatsAppMessage(participant) {
    return `
✨ *Split Payment Request*

Hello ${participant.name}! 👋

You're invited to join:
📋 *${this.description}*
💰 Your share: *${participant.amount.toFixed(2)} AED*
${
  this.includeVAT
    ? `   (Subtotal: ${participant.subtotal.toFixed(2)} AED + VAT: ${participant.vat.toFixed(2)} AED)`
    : ''
}

🔗 Pay your share here:
${participant.paymentLink}

━━━━━━━━━━━━━━━━
👥 Total participants: ${this.participants.length}
📦 Total booking: ${(this.totalAmount * (this.includeVAT ? 1.05 : 1)).toFixed(2)} AED

✅ Fast & secure payment
🔒 PCI DSS compliant

Questions? Just reply! 😊
    `.trim();
  }
}

// CLI usage example
if (require.main === module) {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log(`
Usage:
  node split-payment-calculator.js <total> <participants>

Example:
  node split-payment-calculator.js 2500 5
    `);
    process.exit(0);
  }

  const totalAmount = parseFloat(args[0]);
  const participants = parseInt(args[1]);

  const split = new SplitPayment({
    totalAmount,
    participants,
    description: 'Group Tour Booking',
    bookingId: 'TEST-' + Date.now(),
    includeVAT: true,
  });

  console.log('\n📊 Split Payment Calculation\n');
  console.log('Total Amount:', totalAmount, 'AED');
  console.log('Participants:', participants);
  console.log('Include VAT:', split.includeVAT);
  console.log('\n' + '='.repeat(50) + '\n');

  split.participants.forEach((p, i) => {
    console.log(`Participant ${i + 1}: ${p.name}`);
    if (split.includeVAT) {
      console.log(`  Subtotal: ${p.subtotal.toFixed(2)} AED`);
      console.log(`  VAT (5%): ${p.vat.toFixed(2)} AED`);
    }
    console.log(`  Total: ${p.amount.toFixed(2)} AED`);
    console.log('');
  });

  const status = split.getPaymentStatus();
  console.log('Grand Total:', status.totalPending, 'AED');
}

module.exports = SplitPayment;
