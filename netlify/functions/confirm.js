const { AybClient } = require("@aybdb/client");
const { BLOG_URL, BLOG_NAME, getAybClient, getTransporter, html } = require("./_shared");

function unsubscribeUrl(token) {
  return `${BLOG_URL}/newsletter/unsubscribe?token=${encodeURIComponent(token)}`;
}

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
        `<form method="POST" action="/newsletter/confirm?token=${encodeURIComponent(token.trim())}">` +
        `<button type="submit" style="padding:0.5em 1.5em;font-size:1em;cursor:pointer;">Yes, subscribe me</button>` +
        `</form>`
      );
    }

    if (event.httpMethod === "POST") {
      const rows = await db.queryObjects(
        `SELECT id, email, confirmed_at FROM subscribers WHERE secret_token = '${escaped}' AND unsubscribed_at IS NULL`
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

      const unsub = unsubscribeUrl(token.trim());
      try {
        const transporter = getTransporter();
        await transporter.sendMail({
          from: process.env.FROM_EMAIL,
          replyTo: process.env.REPLY_TO || undefined,
          to: rows[0].email,
          subject: `You're subscribed to ${BLOG_NAME}`,
          text: [
            "You're confirmed! You'll get an email whenever I publish a new post.",
            "",
            `Visit the blog: ${BLOG_URL}`,
            "",
            `To unsubscribe: ${unsub}`,
          ].join("\n"),
          headers: {
            "List-Unsubscribe": `<${unsub}>`,
            "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
          },
        });
      } catch {
        // Don't fail the confirmation if the welcome email fails
      }

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
