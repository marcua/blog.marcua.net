const { AybClient } = require("@aybdb/client");

function getAybClient() {
  const db = new AybClient({ appId: "newsletter" });
  db.saveConfig(process.env.AYB_API_URL, process.env.AYB_TOKEN);
  return db;
}

const BLOG_URL = process.env.BLOG_URL || "";

exports.handler = async (event) => {
  const corsHeaders = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
  };

  if (event.httpMethod === "OPTIONS") {
    return { statusCode: 200, headers: corsHeaders, body: "" };
  }

  if (event.httpMethod !== "GET") {
    return {
      statusCode: 405,
      headers: corsHeaders,
      body: JSON.stringify({ error: "Method not allowed" }),
    };
  }

  const token = (event.queryStringParameters || {}).token || "";
  if (!token.trim()) {
    return {
      statusCode: 400,
      headers: { ...corsHeaders, "Content-Type": "text/html" },
      body: "<html><body><p>Invalid or missing unsubscribe link.</p></body></html>",
    };
  }

  try {
    const db = getAybClient();
    const escaped = AybClient.escapeSQL(token.trim());
    const rows = await db.queryObjects(
      `SELECT id FROM subscribers WHERE unsubscribe_token = '${escaped}' AND unsubscribed_at IS NULL`
    );

    if (rows.length === 0) {
      return {
        statusCode: 200,
        headers: { ...corsHeaders, "Content-Type": "text/html" },
        body: "<html><body><p>This unsubscribe link is not valid or you are already unsubscribed.</p></body></html>",
      };
    }

    await db.query(
      `UPDATE subscribers SET unsubscribed_at = CURRENT_TIMESTAMP WHERE id = ${parseInt(rows[0].id, 10)}`
    );

    return {
      statusCode: 200,
      headers: { ...corsHeaders, "Content-Type": "text/html" },
      body: `<html><body><p>You've been unsubscribed. You won't receive any more emails.</p><p><a href="${BLOG_URL}">Back to blog</a></p></body></html>`,
    };
  } catch {
    return {
      statusCode: 500,
      headers: { ...corsHeaders, "Content-Type": "text/html" },
      body: "<html><body><p>Something went wrong. Please try again later.</p></body></html>",
    };
  }
};
