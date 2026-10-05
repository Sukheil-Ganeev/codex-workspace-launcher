const axios = require("axios");
const send = async (phone, msg) => { console.log("Sending to", phone, ":", msg); };
module.exports = send;