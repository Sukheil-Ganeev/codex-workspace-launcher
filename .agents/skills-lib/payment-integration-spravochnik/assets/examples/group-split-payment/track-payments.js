const track = (groupId) => { console.log("Tracking group", groupId); };
if (require.main === module) track(process.argv[2]);
module.exports = track;