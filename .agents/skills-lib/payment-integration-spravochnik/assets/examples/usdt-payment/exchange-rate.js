const axios = require("axios");
const getRate = async () => { const r = await axios.get("https://api.exchangerate-api.com/v4/latest/AED"); return r.data.rates.USD; };
module.exports = getRate;