const express = require("express");
const stripe = require("stripe")(process.env.STRIPE_SECRET_KEY);
const app = express();
app.use(express.json());
app.use(express.static("public"));
app.post("/api/create-subscription", async (req, res) => { const { email, priceId } = req.body; const customer = await stripe.customers.create({ email }); const subscription = await stripe.subscriptions.create({ customer: customer.id, items: [{ price: priceId }] }); res.json({ subscriptionId: subscription.id }); });
app.listen(3000);