/**
 * Subscription Template
 *
 * Handle recurring payments using Stripe Subscriptions API.
 * Perfect for monthly yacht packages, VIP memberships, or recurring services.
 *
 * Features:
 * - Create subscriptions with multiple pricing tiers
 * - Handle trial periods
 * - Manage upgrades/downgrades
 * - Cancel subscriptions
 * - Webhook handling for subscription events
 * - Usage-based billing (optional)
 *
 * Usage:
 *   const subscription = await createSubscription({
 *     customerId: 'cus_xxx',
 *     priceId: 'price_xxx',
 *     trialDays: 14
 *   });
 */

require('dotenv').config();
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
// const db = require('./database');
// const emailService = require('./email');

/**
 * Create a new subscription
 */
async function createSubscription(options) {
  const {
    customerId, // Existing Stripe customer ID
    customerEmail, // Or create new customer from email
    priceId, // Stripe Price ID (e.g., price_xxx)
    trialDays = 0,
    coupon = null,
    metadata = {},
  } = options;

  try {
    // Get or create customer
    let customer = customerId;

    if (!customer && customerEmail) {
      const newCustomer = await stripe.customers.create({
        email: customerEmail,
        metadata: metadata,
      });
      customer = newCustomer.id;
    }

    if (!customer) {
      throw new Error('Customer ID or email is required');
    }

    // Create subscription
    const subscription = await stripe.subscriptions.create({
      customer: customer,
      items: [{ price: priceId }],
      trial_period_days: trialDays > 0 ? trialDays : undefined,
      coupon: coupon,
      metadata: {
        ...metadata,
        created_via: 'api',
      },
      // Automatically charge the customer
      payment_behavior: 'default_incomplete',
      payment_settings: {
        save_default_payment_method: 'on_subscription',
      },
      expand: ['latest_invoice.payment_intent'],
    });

    // Save to database
    // await db.query(
    //   'INSERT INTO subscriptions (stripe_subscription_id, customer_id, price_id, status, trial_end, next_billing_date, created_at) VALUES (?, ?, ?, ?, ?, ?, NOW())',
    //   [
    //     subscription.id,
    //     customer,
    //     priceId,
    //     subscription.status,
    //     subscription.trial_end ? new Date(subscription.trial_end * 1000) : null,
    //     new Date(subscription.current_period_end * 1000),
    //   ]
    // );

    console.log('Subscription created:', subscription.id);

    return {
      subscriptionId: subscription.id,
      customerId: customer,
      status: subscription.status,
      trialEnd: subscription.trial_end
        ? new Date(subscription.trial_end * 1000)
        : null,
      nextBilling: new Date(subscription.current_period_end * 1000),
      clientSecret:
        subscription.latest_invoice?.payment_intent?.client_secret,
    };
  } catch (err) {
    console.error('Failed to create subscription:', err.message);
    throw err;
  }
}

/**
 * Cancel subscription
 */
async function cancelSubscription(subscriptionId, immediately = false) {
  try {
    const subscription = immediately
      ? await stripe.subscriptions.cancel(subscriptionId)
      : await stripe.subscriptions.update(subscriptionId, {
          cancel_at_period_end: true,
        });

    // Update database
    // await db.query(
    //   'UPDATE subscriptions SET status = ?, cancelled_at = NOW(), cancel_at = ? WHERE stripe_subscription_id = ?',
    //   [
    //     subscription.status,
    //     subscription.cancel_at ? new Date(subscription.cancel_at * 1000) : null,
    //     subscriptionId,
    //   ]
    // );

    console.log(
      immediately
        ? 'Subscription cancelled immediately'
        : 'Subscription will cancel at period end'
    );

    return {
      subscriptionId: subscription.id,
      status: subscription.status,
      cancelAt: subscription.cancel_at
        ? new Date(subscription.cancel_at * 1000)
        : new Date(),
    };
  } catch (err) {
    console.error('Failed to cancel subscription:', err.message);
    throw err;
  }
}

/**
 * Update subscription (upgrade/downgrade)
 */
async function updateSubscription(subscriptionId, newPriceId, prorationBehavior = 'always_invoice') {
  try {
    const subscription = await stripe.subscriptions.retrieve(subscriptionId);

    const updatedSubscription = await stripe.subscriptions.update(
      subscriptionId,
      {
        items: [
          {
            id: subscription.items.data[0].id,
            price: newPriceId,
          },
        ],
        proration_behavior: prorationBehavior, // 'always_invoice', 'create_prorations', 'none'
      }
    );

    // Update database
    // await db.query(
    //   'UPDATE subscriptions SET price_id = ?, updated_at = NOW() WHERE stripe_subscription_id = ?',
    //   [newPriceId, subscriptionId]
    // );

    console.log('Subscription updated:', subscriptionId);

    return {
      subscriptionId: updatedSubscription.id,
      newPriceId: newPriceId,
      status: updatedSubscription.status,
    };
  } catch (err) {
    console.error('Failed to update subscription:', err.message);
    throw err;
  }
}

/**
 * Pause subscription (only available for certain billing intervals)
 */
async function pauseSubscription(subscriptionId) {
  try {
    const subscription = await stripe.subscriptions.update(subscriptionId, {
      pause_collection: {
        behavior: 'void', // Don't invoice during pause
      },
    });

    console.log('Subscription paused:', subscriptionId);

    return {
      subscriptionId: subscription.id,
      status: subscription.status,
      pausedAt: new Date(),
    };
  } catch (err) {
    console.error('Failed to pause subscription:', err.message);
    throw err;
  }
}

/**
 * Resume paused subscription
 */
async function resumeSubscription(subscriptionId) {
  try {
    const subscription = await stripe.subscriptions.update(subscriptionId, {
      pause_collection: '', // Remove pause
    });

    console.log('Subscription resumed:', subscriptionId);

    return {
      subscriptionId: subscription.id,
      status: subscription.status,
      resumedAt: new Date(),
    };
  } catch (err) {
    console.error('Failed to resume subscription:', err.message);
    throw err;
  }
}

/**
 * Get subscription details
 */
async function getSubscription(subscriptionId) {
  try {
    const subscription = await stripe.subscriptions.retrieve(subscriptionId, {
      expand: ['customer', 'latest_invoice'],
    });

    return {
      id: subscription.id,
      status: subscription.status,
      customer: subscription.customer,
      currentPeriodStart: new Date(subscription.current_period_start * 1000),
      currentPeriodEnd: new Date(subscription.current_period_end * 1000),
      cancelAtPeriodEnd: subscription.cancel_at_period_end,
      cancelAt: subscription.cancel_at
        ? new Date(subscription.cancel_at * 1000)
        : null,
      trialEnd: subscription.trial_end
        ? new Date(subscription.trial_end * 1000)
        : null,
      items: subscription.items.data,
      latestInvoice: subscription.latest_invoice,
    };
  } catch (err) {
    console.error('Failed to get subscription:', err.message);
    throw err;
  }
}

/**
 * List customer subscriptions
 */
async function listCustomerSubscriptions(customerId) {
  try {
    const subscriptions = await stripe.subscriptions.list({
      customer: customerId,
      status: 'all',
      expand: ['data.latest_invoice'],
    });

    return subscriptions.data.map((sub) => ({
      id: sub.id,
      status: sub.status,
      currentPeriodEnd: new Date(sub.current_period_end * 1000),
      cancelAtPeriodEnd: sub.cancel_at_period_end,
      priceId: sub.items.data[0]?.price?.id,
      amount: sub.items.data[0]?.price?.unit_amount / 100,
      currency: sub.items.data[0]?.price?.currency,
    }));
  } catch (err) {
    console.error('Failed to list subscriptions:', err.message);
    throw err;
  }
}

/**
 * Handle subscription webhook events
 */
async function handleSubscriptionWebhook(event) {
  const subscription = event.data.object;

  switch (event.type) {
    case 'customer.subscription.created':
      console.log('Subscription created:', subscription.id);
      // Send welcome email
      break;

    case 'customer.subscription.updated':
      console.log('Subscription updated:', subscription.id);
      break;

    case 'customer.subscription.deleted':
      console.log('Subscription deleted:', subscription.id);
      // Send cancellation email
      break;

    case 'customer.subscription.trial_will_end':
      console.log('Trial ending soon:', subscription.id);
      // Send reminder email
      break;

    case 'invoice.payment_succeeded':
      console.log('Subscription payment succeeded:', subscription.id);
      // Send receipt
      break;

    case 'invoice.payment_failed':
      console.log('Subscription payment failed:', subscription.id);
      // Send payment failure notice
      break;

    default:
      console.log('Unhandled subscription event:', event.type);
  }
}

// CLI usage example
if (require.main === module) {
  const args = process.argv.slice(2);
  const command = args[0];

  if (!command) {
    console.log(`
Usage:
  node subscription-template.js create <email> <price-id> [trial-days]
  node subscription-template.js cancel <subscription-id> [immediately]
  node subscription-template.js get <subscription-id>

Examples:
  node subscription-template.js create john@example.com price_xxx 14
  node subscription-template.js cancel sub_xxx
  node subscription-template.js get sub_xxx
    `);
    process.exit(0);
  }

  switch (command) {
    case 'create':
      createSubscription({
        customerEmail: args[1],
        priceId: args[2],
        trialDays: parseInt(args[3]) || 0,
      })
        .then((result) => {
          console.log('\n✅ Subscription created successfully!');
          console.log('Subscription ID:', result.subscriptionId);
          console.log('Status:', result.status);
          console.log('Next billing:', result.nextBilling);
        })
        .catch((err) => console.error('Error:', err.message));
      break;

    case 'cancel':
      cancelSubscription(args[1], args[2] === 'immediately')
        .then((result) => {
          console.log('\n✅ Subscription cancelled');
          console.log('Cancel at:', result.cancelAt);
        })
        .catch((err) => console.error('Error:', err.message));
      break;

    case 'get':
      getSubscription(args[1])
        .then((result) => {
          console.log('\n📊 Subscription Details:');
          console.log(JSON.stringify(result, null, 2));
        })
        .catch((err) => console.error('Error:', err.message));
      break;

    default:
      console.error('Unknown command:', command);
      process.exit(1);
  }
}

module.exports = {
  createSubscription,
  cancelSubscription,
  updateSubscription,
  pauseSubscription,
  resumeSubscription,
  getSubscription,
  listCustomerSubscriptions,
  handleSubscriptionWebhook,
};
