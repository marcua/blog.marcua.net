const { AybClient } = require("@aybdb/client");
const { BLOG_URL, BLOG_NAME, getAybClient, html } = require("./_shared");

exports.handler = async (event) => {
  const token = (event.queryStringParameters || {}).token || "";
  if (!token.trim()) {
    return html("<p>Invalid or missing confirmation link.</p>");
  }

  try {
    const db = getAybClient();
    const escaped = AybClient.escapeSQL(token.trim());

    if (event.httpMethod === "GET") {
      const rows = await db.queryObjects(
        `SELECT id, confirmed_at FROM subscribers WHERE secret_token = '${escaped}' AND unsubscribed_at IS NULL`
      );
      if (rows.length === 0) {
        return html("<p>This confirmation link is not valid.</p>");
      }
      if (rows[0].confirmed_at) {
        return html(`<p>You're already subscribed!</p><p><a href="${BLOG_URL}">Back to blog</a></p>`);
      }
      return html(
        `<p>Confirm your subscription to ${BLOG_NAME}?</p>` +
        `<form method="POST" action="/.netlify/functions/confirm?token=${encodeURIComponent(token.trim())}">` +
        `<button type="submit" style="padding:0.5em 1.5em;font-size:1em;cursor:pointer;">Yes, subscribe me</button>` +
        `</form>`
      );
    }

    if (event.httpMethod === "POST") {
      const rows = await db.queryObjects(
        `SELECT id, confirmed_at FROM subscribers WHERE secret_token = '${escaped}' AND unsubscribed_at IS NULL`
      );
      if (rows.length === 0) {
        return html("<p>This confirmation link is not valid.</p>");
      }
      if (rows[0].confirmed_at) {
        return html(`<p>You're already subscribed!</p><p><a href="${BLOG_URL}">Back to blog</a></p>`);
      }
      await db.query(
        `UPDATE subscribers SET confirmed_at = CURRENT_TIMESTAMP WHERE id = ${parseInt(rows[0].id, 10)}`
      );
      return html(
        `<p>You're subscribed! You'll get an email whenever a new post is published.</p>` +
        `<p><a href="${BLOG_URL}">Back to blog</a></p>`
      );
    }

    return { statusCode: 405, body: "Method not allowed" };
  } catch {
    return html("<p>Something went wrong. Please try again later.</p>");
  }
};
