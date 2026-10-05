/**
 * Обработчик Notion Webhooks (Express.js).
 * Получает события от Notion API Webhooks и обрабатывает их.
 * 
 * Требования:
 *   npm install express @notionhq/client
 *   Переменные окружения: NOTION_TOKEN, NOTION_WEBHOOK_SECRET, PORT
 * 
 * Notion Webhooks:
 *   - 23 типа событий (page, data_source, database, comment)
 *   - Payload НЕ содержит данные изменений -- только сигнал
 *   - Нужен follow-up запрос к API для получения данных
 *   - Верификация подписи: HMAC-SHA256 (x-notion-signature)
 *   - Доставка: at-most-once, до 8 retry за 24ч
 * 
 * Использование:
 *   NOTION_TOKEN=ntn_*** NOTION_WEBHOOK_SECRET=whsec_*** PORT=3000 node webhook-handler.js
 */

const express = require("express");
const crypto = require("crypto");
const { Client } = require("@notionhq/client");

const app = express();
const PORT = process.env.PORT || 3000;
const WEBHOOK_SECRET = process.env.NOTION_WEBHOOK_SECRET;
const notion = new Client({ auth: process.env.NOTION_TOKEN });

// Raw body для верификации подписи
app.use(express.json({
  verify: (req, _res, buf) => {
    req.rawBody = buf;
  },
}));

/**
 * Верифицирует подпись webhook запроса (HMAC-SHA256).
 */
function verifySignature(req) {
  const signature = req.headers["x-notion-signature"];
  if (!signature) return false;

  const hmac = crypto.createHmac("sha256", WEBHOOK_SECRET);
  hmac.update(req.rawBody);
  const expected = `sha256=${hmac.digest("hex")}`;

  try {
    return crypto.timingSafeEqual(
      Buffer.from(signature),
      Buffer.from(expected)
    );
  } catch {
    return false;
  }
}

/**
 * Обработчики событий по типам.
 */
const handlers = {
  // Страница создана
  "page.created": async (payload) => {
    const pageId = payload.data?.page?.id;
    if (!pageId) return;

    const page = await notion.pages.retrieve({ page_id: pageId });
    const title = page.properties?.["Booking Name"]?.title?.[0]?.plain_text || "Untitled";
    console.log(`[NEW PAGE] ${title} (${pageId})`);

    // Здесь: отправить уведомление в Telegram/Slack
  },

  // Свойства страницы обновлены (например, Status изменен)
  "page.properties_updated": async (payload) => {
    const pageId = payload.data?.page?.id;
    if (!pageId) return;

    const page = await notion.pages.retrieve({ page_id: pageId });
    const status = page.properties?.["Status"]?.select?.name;
    const title = page.properties?.["Booking Name"]?.title?.[0]?.plain_text || "Untitled";
    console.log(`[UPDATED] ${title} -> Status: ${status}`);

    // Реагировать на смену статуса
    if (status === "Paid") {
      console.log(`  -> Бронирование оплачено! Отправить подтверждение клиенту.`);
    } else if (status === "Cancelled") {
      console.log(`  -> Бронирование отменено. Уведомить поставщика.`);
    }
  },

  // Страница удалена (в корзину)
  "page.deleted": async (payload) => {
    const pageId = payload.data?.page?.id;
    console.log(`[DELETED] Page ${pageId} moved to trash`);
  },

  // Комментарий создан
  "comment.created": async (payload) => {
    const pageId = payload.data?.comment?.parent?.page_id;
    if (!pageId) return;

    const comments = await notion.comments.list({ block_id: pageId });
    const latest = comments.results[comments.results.length - 1];
    const text = latest?.rich_text?.[0]?.plain_text || "";
    console.log(`[COMMENT] on page ${pageId}: ${text}`);
  },
};

/**
 * Webhook endpoint.
 */
app.post("/webhook/notion", async (req, res) => {
  // 1. Верифицировать подпись
  if (!verifySignature(req)) {
    console.error("Invalid webhook signature");
    return res.status(401).json({ error: "Invalid signature" });
  }

  // 2. Обработать verification challenge (при регистрации webhook)
  if (req.body.type === "url_verification") {
    console.log("Webhook verification challenge received");
    return res.json({ challenge: req.body.challenge });
  }

  // 3. Обработать событие
  const eventType = req.body.type;
  console.log(`\nReceived event: ${eventType}`);

  const handler = handlers[eventType];
  if (handler) {
    try {
      await handler(req.body);
    } catch (error) {
      console.error(`Error handling ${eventType}:`, error.message);
    }
  } else {
    console.log(`  No handler for event type: ${eventType}`);
  }

  // 4. Ответить 200 (Notion ожидает быстрый ответ)
  res.status(200).json({ ok: true });
});

app.listen(PORT, () => {
  console.log(`Notion Webhook Handler listening on port ${PORT}`);
  console.log(`Endpoint: POST http://localhost:${PORT}/webhook/notion`);
  console.log(`\nSupported events: ${Object.keys(handlers).join(", ")}`);
});
