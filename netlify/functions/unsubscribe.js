const { AybClient } = require("@aybdb/client");
const { BLOG_URL, getAybClient, html } = require("./_shared");

async function doUnsubscribe(token) {
  const db = getAybClient();
  const escaped = AybClient.escapeSQL(token);
  const rows = await db.queryObjects(
    `SELECT id FROM subscribers WHERE secret_token = '${escaped}' AND unsubscribed_at IS NULL`
  );
  if (rows.length === 0) {
    return { found: false };
  }
  await db.query(
    `UPDATE subscribers SET unsubscribed_at = CURRENT_TIMESTAMP WHERE id = ${parseInt(rows[0].id, 10)}`
  );
  return { found: true };
}

exports.handler = async (event) => {
  const token = (event.queryStringParameters || {}).token || "";
  if (!token.trim()) {
    return html("<p>Invalid or missing unsubscribe link.</p>");
  }

  try {
    if (event.httpMethod === "GET") {
      return html(
        `<p>Unsubscribe from future emails?</p>` +
        `<form method="POST" action="/.netlify/functions/unsubscribe?token=${encodeURIComponent(token.trim())}">` +
        `<button type="submit" style="padding:0.5em 1.5em;font-size:1em;cursor:pointer;">Yes, unsubscribe me</button>` +
        `</form>`
      );
    }

    if (event.httpMethod === "POST") {
      const result = await doUnsubscribe(token.trim());
      if (!result.found) {
        return html("<p>This unsubscribe link is not valid or you are already unsubscribed.</p>");
      }
      return html(
        `<p>You've been unsubscribed. You won't receive any more emails.</p>` +
        `<p><a href="${BLOG_URL}">Back to blog</a></p>`
      );
    }

    return { statusCode: 405, body: "Method not allowed" };
  } catch {
    return html("<p>Something went wrong. Please try again later.</p>");
  }
};
