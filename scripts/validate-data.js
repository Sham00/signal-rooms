#!/usr/bin/env node

/**
 * Validate GitHub Pages JSON payloads used by rooms.
 *
 * Goals:
 * - Catch shape mismatches early (e.g. history.json tickers vs history arrays)
 * - Keep it dependency-free (Node only)
 */

const fs = require('fs');
const path = require('path');

function readJson(p) {
  const raw = fs.readFileSync(p, 'utf8');
  try {
    return JSON.parse(raw);
  } catch (e) {
    throw new Error(`Invalid JSON: ${p}: ${e.message}`);
  }
}

function fail(msg) {
  console.error(`DATA VALIDATION FAILED: ${msg}`);
  process.exitCode = 1;
}

function ok(msg) {
  console.log(`OK: ${msg}`);
}

function isIsoDateLike(s) {
  return typeof s === 'string' && /^\d{4}-\d{2}-\d{2}/.test(s);
}

function validateRoomHistory(filePath, roomName) {
  const j = readJson(filePath);

  if (!j || typeof j !== 'object') return fail(`${roomName} history not an object`);
  if (!j.last_updated) fail(`${roomName} history missing last_updated`);

  // Support either shape:
  // 1) { history: [...] }
  // 2) { tickers: { TICKER: [...] } }
  const hasHistoryArr = Array.isArray(j.history);
  const hasTickersObj = j.tickers && typeof j.tickers === 'object' && !Array.isArray(j.tickers);

  if (!hasHistoryArr && !hasTickersObj) {
    return fail(`${roomName} history must have either history[] or tickers{}`);
  }

  if (hasHistoryArr) {
    if (!j.history.length) fail(`${roomName} history.history is empty`);
    const first = j.history[0];
    if (!first || typeof first !== 'object') fail(`${roomName} history.history[0] not an object`);
    if (!('date' in first) || !isIsoDateLike(first.date)) fail(`${roomName} history.history[0].date invalid`);
    if (!('close' in first) || typeof first.close !== 'number') fail(`${roomName} history.history[0].close invalid`);
    ok(`${roomName} history (history[]) looks valid (${j.history.length} points)`);
  }

  if (hasTickersObj) {
    const keys = Object.keys(j.tickers);
    if (!keys.length) fail(`${roomName} history.tickers has no keys`);

    for (const k of keys) {
      const arr = j.tickers[k];
      if (!Array.isArray(arr)) {
        fail(`${roomName} history.tickers.${k} is not an array`);
        continue;
      }
      if (!arr.length) {
        fail(`${roomName} history.tickers.${k} is empty`);
        continue;
      }
      const first = arr[0];
      if (!first || typeof first !== 'object') {
        fail(`${roomName} history.tickers.${k}[0] not an object`);
        continue;
      }
      if (!('date' in first) || !isIsoDateLike(first.date)) fail(`${roomName} history.tickers.${k}[0].date invalid`);
      if (!('close' in first) || typeof first.close !== 'number') fail(`${roomName} history.tickers.${k}[0].close invalid`);
    }

    ok(`${roomName} history (tickers{}) looks valid (${keys.join(', ')})`);
  }
}

function main() {
  const repoRoot = path.resolve(__dirname, '..');

  // GPU
  validateRoomHistory(path.join(repoRoot, 'data', 'gpu', 'history.json'), 'gpu');

  // Extend to other rooms later; keep this scoped and dependency-free.

  if (process.exitCode === 1) {
    console.error('One or more validations failed.');
    process.exit(1);
  }
}

main();
