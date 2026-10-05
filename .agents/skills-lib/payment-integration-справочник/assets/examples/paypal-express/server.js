const express = require("express");
const paypal = require("@paypal/checkout-server-sdk");
const app = express();
app.use(express.json());
app.use(express.static("public"));
app.post("/api/create-order", async (req, res) => { res.json({ orderID: "ORDER123" }); });
app.listen(3000);