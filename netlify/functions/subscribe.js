const { AybClient } = require("@aybdb/client");
const crypto = require("crypto");
const { BLOG_NAME, getAybClient, getTransporter } = require("./_shared");

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

exports.handler = async (event) => {
  const corsHeaders = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
  };

  if (event.httpMethod === "OPTIONS") {
    return { statusCode: 200, headers: corsHeaders, body: "" };
  }

  if (event.httpMethod !== "POST") {
    return {
      statusCode: 405,
      headers: corsHeaders,
      body: JSON.stringify({ error: "Method not allowed" }),
    };
  }

  let body;
  try {
    body = JSON.parse(event.body || "{}");
  } catch {
    return {
      statusCode: 400,
      headers: corsHeaders,
      body: JSON.stringify({ error: "Invalid JSON" }),
    };
  }

  const email = (body.email || "").trim();
  if (!email || !EMAIL_RE.test(email)) {
    return {
      statusCode: 400,
      headers: corsHeaders,
      body: JSON.stringify({ error: "A valid email is required" }),
    };
  }

  try {
    const db = getAybClient();
    const token = crypto.randomBytes(32).toString("base64url");
    const escaped = AybClient.escapeSQL(email);
    const tokenEscaped = AybClient.escapeSQL(token);

    const existing = await db.queryObjects(
      `SELECT id, confirmed_at, unsubscribed_at FROM subscribers WHERE email = '${escaped}'`
    );

    if (existing.length > 0) {
      const sub = existing[0];
      if (sub.confirmed_at && !sub.unsubscribed_at) {
        return {
          statusCode: 200,
          headers: corsHeaders,
          body: JSON.stringify({ ok: true, already: true }),
        };
      }
      await db.query(
        `UPDATE subscribers SET unsubscribed_at = NULL, confirmed_at = NULL, ` +
        `secret_token = '${tokenEscaped}' ` +
        `WHERE id = ${parseInt(sub.id, 10)}`
      );
    } else {
      await db.query(
        `INSERT INTO subscribers (email, secret_token) ` +
        `VALUES ('${escaped}', '${tokenEscaped}')`
      );
    }

    const blogUrl = process.env.BLOG_URL || "";
    const confirmUrl = `${blogUrl}/newsletter/confirm?token=${encodeURIComponent(token)}`;

    const transporter = getTransporter();
    await transporter.sendMail({
      from: process.env.FROM_EMAIL,
      replyTo: process.env.REPLY_TO || undefined,
      to: email,
      subject: `Confirm your subscription to ${BLOG_NAME}`,
      text: [
        `Please confirm your subscription to ${BLOG_NAME} by visiting this link:`,
        "",
        confirmUrl,
        "",
        "If you didn't request this, you can ignore this email.",
      ].join("\n"),
    });

    return {
      statusCode: 200,
      headers: corsHeaders,
      body: JSON.stringify({ ok: true }),
    };
  } catch {
    return {
      statusCode: 500,
      headers: corsHeaders,
      body: JSON.stringify({ error: "Something went wrong, please try again." }),
    };
  }
};
