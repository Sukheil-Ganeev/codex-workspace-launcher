const express = require("express");
const axios = require("axios");
const app = express();
app.use(express.json());
app.use(express.static("public"));
app.post("/api/convert", async (req, res) => { const { from, to, amount } = req.body; res.json({ result: amount * 0.27 }); });
app.listen(3000);