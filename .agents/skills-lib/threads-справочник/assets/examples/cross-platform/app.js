// Cross-Platform Publishing API
// Instagram + Threads одновременно
// Автор: Claude Code Agent

require('dotenv').config();
const express = require('express');
const CrossPoster = require('../../templates/cross-poster');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());

// Logger middleware
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
  next();
});

// Initialize CrossPoster
const poster = new CrossPoster(
  process.env.ACCESS_TOKEN,
  process.env.IG_USER_ID
);

// ============================================
// Routes
// ============================================

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Cross-post to both platforms
app.post('/api/cross-post', async (req, res) => {
  try {
    const { title, description, imageUrl, hashtags } = req.body;

    // Validation
    if (!title) {
      return res.status(400).json({ error: 'Title is required' });
    }

    if (!imageUrl) {
      return res.status(400).json({ error: 'Image URL is required' });
    }

    const content = { title, description, imageUrl, hashtags };
    const results = await poster.crossPost(content);

    const successCount = [results.instagram.success, results.threads.success]
      .filter(Boolean).length;

    res.json({
      success: successCount > 0,
      results: results,
      successCount: successCount,
      totalPlatforms: 2
    });

  } catch (error) {
    console.error('Cross-post error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Publish to Instagram only
app.post('/api/publish/instagram', async (req, res) => {
  try {
    const { imageUrl, caption, hashtags } = req.body;

    if (!imageUrl || !caption) {
      return res.status(400).json({ error: 'Image URL and caption are required' });
    }

    const formattedCaption = poster.formatCaptionForInstagram(caption, hashtags);
    const result = await poster.publishToInstagram(imageUrl, formattedCaption);

    res.json(result);

  } catch (error) {
    console.error('Instagram publish error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Publish to Threads only
app.post('/api/publish/threads', async (req, res) => {
  try {
    const { title, description, imageUrl, hashtags } = req.body;

    if (!title) {
      return res.status(400).json({ error: 'Title is required' });
    }

    const formattedText = poster.formatTextForThreads(title, description, hashtags);
    const result = await poster.publishToThreads(formattedText, imageUrl);

    res.json(result);

  } catch (error) {
    console.error('Threads publish error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Webhook endpoint для Make.com / Zapier
app.post('/webhook', async (req, res) => {
  try {
    // Проверка webhook secret
    const webhookSecret = req.headers['x-webhook-secret'];

    if (webhookSecret !== process.env.WEBHOOK_SECRET) {
      return res.status(401).json({ error: 'Unauthorized' });
    }

    const { event, data } = req.body;

    console.log('Webhook received:', event);

    // Обработка разных событий
    switch (event) {
      case 'booking_confirmed':
        await handleBookingConfirmed(data);
        break;

      case 'new_review':
        await handleNewReview(data);
        break;

      case 'custom_post':
        await handleCustomPost(data);
        break;

      default:
        console.log('Unknown event:', event);
    }

    res.json({ success: true, event: event });

  } catch (error) {
    console.error('Webhook error:', error);
    res.status(500).json({ error: error.message });
  }
});

// ============================================
// Webhook Handlers
// ============================================

async function handleBookingConfirmed(data) {
  const content = {
    title: '🎉 New booking just confirmed!',
    description: `Tour: ${data.tour}
Customer: ${data.customer}
Date: ${data.date}

We're excited to host you!`,
    imageUrl: data.imageUrl || null,
    hashtags: ['DubaiTours', 'BookingConfirmed', 'ThankYou']
  };

  if (content.imageUrl) {
    return await poster.crossPost(content);
  } else {
    return await poster.postTextOnly(content);
  }
}

async function handleNewReview(data) {
  const stars = '⭐'.repeat(data.rating || 5);

  const content = {
    title: `${stars} Amazing review from ${data.customerName}!`,
    description: `"${data.reviewText}"

Thank you for choosing us!`,
    imageUrl: data.photoUrl || null,
    hashtags: ['CustomerReview', 'DubaiTours', 'HappyCustomers']
  };

  if (content.imageUrl) {
    return await poster.crossPost(content);
  } else {
    return await poster.postTextOnly(content);
  }
}

async function handleCustomPost(data) {
  const content = {
    title: data.title,
    description: data.description,
    imageUrl: data.imageUrl,
    hashtags: data.hashtags || []
  };

  if (content.imageUrl) {
    return await poster.crossPost(content);
  } else {
    return await poster.postTextOnly(content);
  }
}

// ============================================
// Error Handling
// ============================================

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Endpoint not found' });
});

// Global error handler
app.use((err, req, res, next) => {
  console.error('Server error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

// ============================================
// Server Start
// ============================================

app.listen(PORT, () => {
  console.log(`\n🚀 Cross-Platform API running on port ${PORT}`);
  console.log(`Health check: http://localhost:${PORT}/health`);
  console.log(`\nEndpoints:`);
  console.log(`  POST /api/cross-post`);
  console.log(`  POST /api/publish/instagram`);
  console.log(`  POST /api/publish/threads`);
  console.log(`  POST /webhook`);
  console.log(`\nPress Ctrl+C to stop\n`);
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\nShutting down gracefully...');
  process.exit(0);
});
