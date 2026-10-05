const express = require("express");
const stripe = require("stripe")(process.env.STRIPE_SECRET_KEY);
const app = express();
app.use(express.json());
app.use(express.static("public"));
app.post("/api/create-group-payment", async (req, res) => { const { groupName, totalAmount, participants } = req.body; const amountPerPerson = Math.round(totalAmount / participants.length); res.json({ groupId: 1, amountPerPerson }); });
app.listen(3000);