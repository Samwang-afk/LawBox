#!/usr/bin/env node

import fs from "node:fs";

const endpoint = process.env.PKULAW_MCP_URL || "https://apim-gateway.pkulaw.com/mcp-law";
const configPath = process.env.PKULAW_ENV_FILE;

function readEnvFile(filePath) {
  if (!filePath) return {};
  if (!fs.existsSync(filePath)) return {};
  const env = {};
  const text = fs.readFileSync(filePath, "utf8");
  for (const line of text.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const index = trimmed.indexOf("=");
    if (index === -1) continue;
    const key = trimmed.slice(0, index).trim();
    const value = trimmed.slice(index + 1).trim();
    env[key] = value.replace(/^["']|["']$/g, "");
  }
  return env;
}

const fileEnv = readEnvFile(configPath);
const apiKey =
  process.env.PKULAW_BEARER_TOKEN ||
  fileEnv.PKULAW_BEARER_TOKEN ||
  process.env.PKULAW_API_KEY ||
  fileEnv.PKULAW_API_KEY;

function usage() {
  console.error("Usage: node pkulaw_get_law_list.mjs [--title TEXT] [--fulltext TEXT]");
  console.error("Reads credentials from environment variables or optional PKULAW_ENV_FILE.");
}

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i += 1) {
    const key = argv[i];
    if (key === "--title" || key === "--fulltext") {
      args[key.slice(2)] = argv[i + 1];
      i += 1;
    }
  }
  return args;
}

function extractJsonFromSse(text) {
  const dataLines = text
    .split(/\r?\n/)
    .filter((line) => line.startsWith("data:"))
    .map((line) => line.replace(/^data:\s?/, "").trim())
    .filter(Boolean);
  if (dataLines.length === 0) return null;
  return dataLines
    .map((line) => {
      try {
        return JSON.parse(line);
      } catch {
        return null;
      }
    })
    .filter(Boolean);
}

function authHeaders(mode) {
  if (mode === "bearer") return { Authorization: `Bearer ${apiKey}` };
  if (mode === "basic") return { Authorization: `Basic ${apiKey}` };
  if (mode === "authorization-apikey") return { Authorization: `ApiKey ${apiKey}` };
  if (mode === "authorization-api-key") return { Authorization: `APIKey ${apiKey}` };
  if (mode === "ApiKey") return { ApiKey: apiKey };
  if (mode === "apikey") return { apikey: apiKey };
  if (mode === "x-api-key") return { "x-api-key": apiKey };
  if (mode === "api-key") return { "api-key": apiKey };
  return { Authorization: `Bearer ${apiKey}` };
}

async function postJson(body, extraHeaders = {}, authMode = "bearer") {
  const res = await fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json, text/event-stream",
      ...authHeaders(authMode),
      ...extraHeaders,
    },
    body: JSON.stringify(body),
  });

  const text = await res.text();
  const contentType = res.headers.get("content-type") || "";
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${text.slice(0, 1000)}`);
  }
  if (contentType.includes("text/event-stream")) {
    const events = extractJsonFromSse(text);
    if (events) return events.length === 1 ? events[0] : events;
  }
  try {
    return JSON.parse(text);
  } catch {
    return { raw: text };
  }
}

async function main() {
  if (!apiKey) {
    usage();
    throw new Error("Missing PKULAW_API_KEY or PKULAW_BEARER_TOKEN");
  }

  const args = parseArgs(process.argv);
  if (!args.title && !args.fulltext) {
    usage();
    throw new Error("At least one of --title or --fulltext is required");
  }

  const authModes = (process.env.PKULAW_AUTH_MODE || "bearer,ApiKey,basic,authorization-apikey,authorization-api-key,apikey,x-api-key,api-key")
    .split(",")
    .map((mode) => mode.trim())
    .filter(Boolean);

  let initialize;
  let authModeUsed;
  let lastError;
  for (const authMode of authModes) {
    try {
      initialize = await postJson(
        {
          jsonrpc: "2.0",
          id: 1,
          method: "initialize",
          params: {
            protocolVersion: "2024-11-05",
            capabilities: {},
            clientInfo: {
              name: "legal-skills-client",
              version: "0.1.0",
            },
          },
        },
        {},
        authMode,
      );
      authModeUsed = authMode;
      break;
    } catch (error) {
      lastError = error;
      if (!String(error.message).includes("401")) break;
    }
  }

  if (!initialize) {
    throw lastError || new Error("Initialize failed");
  }

  const result = await postJson(
    {
      jsonrpc: "2.0",
      id: 2,
      method: "tools/call",
      params: {
        name: "get_law_list",
        arguments: args,
      },
    },
    authModeUsed,
  );

  const output = {
    endpoint,
    query: args,
    authModeUsed,
    initialized: Boolean(initialize && !initialize.error),
    result,
  };
  process.stdout.write(`${JSON.stringify(output, null, 2)}\n`);
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
