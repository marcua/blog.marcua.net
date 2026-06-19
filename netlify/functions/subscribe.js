const { AybClient } = require("@aybdb/client");
const nodemailer = require("nodemailer");
const crypto = require("crypto");

// Schema migrations are owned by the GitHub Actions cron job
// (newsletter/migrations.py). This function assumes the `subscribers`
// table already exists; run the newsletter workflow at least once first.

function getAybClient() {
  const db = new AybClient({ appId: "newsletter" });
  db.saveConfig(process.env.AYB_API_URL, process.env.AYB_TOKEN);
  return db;
}

function getTransporter() {
  const port = parseInt(process.env.SMTP_PORT || "587", 10);
  return nodemailer.createTransport({
    host: process.env.SMTP_HOST,
    port,
    secure: port === 465,
    auth: {
      user: process.env.SMTP_USERNAME,
      pass: process.env.SMTP_PASSWORD,
    },
  });
}

function unsubscribeUrl(token) {
  const blogUrl = process.env.BLOG_URL || "";
  return `${blogUrl}/.netlify/functions/unsubscribe?token=${encodeURIComponent(token)}`;
}

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
  if (!email || !email.includes("@")) {
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
    const existing = await db.queryObjects(
      `SELECT id, unsubscribed_at FROM subscribers WHERE email = '${escaped}'`
    );

    const tokenEscaped = AybClient.escapeSQL(token);
    if (existing.length > 0) {
      await db.query(
        `UPDATE subscribers SET unsubscribed_at = NULL, unsubscribe_token = '${tokenEscaped}' WHERE id = ${parseInt(existing[0].id, 10)}`
      );
    } else {
      await db.query(
        `INSERT INTO subscribers (email, unsubscribe_token) VALUES ('${escaped}', '${tokenEscaped}')`
      );
    }

    const unsub = unsubscribeUrl(token);
    const blogName = process.env.BLOG_NAME || "";
    const blogUrl = process.env.BLOG_URL || "";

    const transporter = getTransporter();
    await transporter.sendMail({
      from: process.env.FROM_EMAIL,
      replyTo: process.env.REPLY_TO || undefined,
      to: email,
      subject: `You're subscribed to ${blogName}`,
      text: [
        "Thank you for subscribing! You'll get an email whenever I publish a new post.",
        "",
        `Visit the blog: ${blogUrl}`,
        "",
        `To unsubscribe: ${unsub}`,
      ].join("\n"),
      headers: {
        "List-Unsubscribe": `<${unsub}>`,
        "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
      },
    });

    return {
      statusCode: 200,
      headers: corsHeaders,
      body: JSON.stringify({ ok: true }),
    };
  } catch (e) {
    return {
      statusCode: 500,
      headers: corsHeaders,
      body: JSON.stringify({ error: e.message }),
    };
  }
};
