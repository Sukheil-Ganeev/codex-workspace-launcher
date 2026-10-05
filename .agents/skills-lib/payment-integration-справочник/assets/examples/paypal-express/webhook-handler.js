const express = require("express");
const router = express.Router();
router.post("/webhook", (req, res) => { console.log("PayPal webhook"); res.sendStatus(200); });
module.exports = router;