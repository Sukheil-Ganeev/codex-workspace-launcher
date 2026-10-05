// Простой API endpoint
// Endpoint: https://your-domain.vercel.app/api/hello

export default function handler(req, res) {
  const { name = 'Гость' } = req.query;
  
  res.status(200).json({
    message: `Привет, ${name}!`,
    timestamp: new Date().toISOString(),
    method: req.method
  });
}
