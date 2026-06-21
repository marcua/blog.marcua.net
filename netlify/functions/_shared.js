const { AybClient } = require("@aybdb/client");
const nodemailer = require("nodemailer");

const BLOG_URL = (process.env.BLOG_URL || "").replace(/\/+$/, "");
const BLOG_NAME = process.env.BLOG_NAME || "";

function getAybClient() {
  const db = new AybClient({ appId: "newsletter" });
  const parsed = AybClient.parseDatabaseUrl(process.env.AYB_API_URL);
  db._config = { ...parsed, token: process.env.AYB_TOKEN };
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

function html(body) {
  return {
    statusCode: 200,
    headers: { "Content-Type": "text/html" },
    body: `<html><head><meta name="viewport" content="width=device-width,initial-scale=1"></head><body style="font-family:system-ui,sans-serif;max-width:480px;margin:2em auto;padding:0 1em;">${body}</body></html>`,
  };
}

module.exports = { AybClient, BLOG_URL, BLOG_NAME, getAybClient, getTransporter, html };
