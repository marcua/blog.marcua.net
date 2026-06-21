const { AybClient } = require("@aybdb/client");

const BLOG_URL = process.env.BLOG_URL || "";
const BLOG_NAME = process.env.BLOG_NAME || "";

function getAybClient() {
  const db = new AybClient({ appId: "newsletter" });
  const parsed = AybClient.parseDatabaseUrl(process.env.AYB_API_URL);
  db._config = { ...parsed, token: process.env.AYB_TOKEN };
  return db;
}

function html(body) {
  return {
    statusCode: 200,
    headers: { "Content-Type": "text/html" },
    body: `<html><head><meta name="viewport" content="width=device-width,initial-scale=1"></head><body style="font-family:system-ui,sans-serif;max-width:480px;margin:2em auto;padding:0 1em;">${body}</body></html>`,
  };
}

module.exports = { AybClient, BLOG_URL, BLOG_NAME, getAybClient, html };
