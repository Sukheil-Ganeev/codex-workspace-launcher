const axios = require("axios");
const updateRates = async () => { const r = await axios.get("https://api.exchangerate-api.com/v4/latest/AED"); console.log("Rates:", r.data.rates); };
if (require.main === module) updateRates();
module.exports = updateRates;