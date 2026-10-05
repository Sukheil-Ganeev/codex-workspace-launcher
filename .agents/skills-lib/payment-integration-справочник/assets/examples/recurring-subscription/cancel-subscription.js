const stripe = require("stripe")(process.env.STRIPE_SECRET_KEY);
const cancel = async (id) => { await stripe.subscriptions.cancel(id); console.log("Cancelled:", id); };
module.exports = cancel;