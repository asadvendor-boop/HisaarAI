import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { createServer } from "vite";

test("clean trusted path marks absent recovery-only states as not needed", async (t) => {
  const previousWindow = globalThis.window;
  globalThis.window = { location: { search: "" } };
  t.after(() => {
    globalThis.window = previousWindow;
  });

  const server = await createServer({
    appType: "custom",
    logLevel: "silent",
    root: fileURLToPath(new URL("..", import.meta.url)),
    server: { middlewareMode: true },
  });
  t.after(() => server.close());

  const app = await server.ssrLoadModule("/src/App.tsx");

  assert.equal(typeof app.missingTimelineStepLabel, "function");
  assert.equal(app.missingTimelineStepLabel("QUARANTINED", true), "NOT NEEDED");
  assert.equal(app.missingTimelineStepLabel("INVESTIGATING", true), "NOT NEEDED");
});

test("observed flagship timing separates automation from human review", async (t) => {
  const previousWindow = globalThis.window;
  globalThis.window = { location: { search: "" } };
  t.after(() => {
    globalThis.window = previousWindow;
  });

  const server = await createServer({
    appType: "custom",
    logLevel: "silent",
    root: fileURLToPath(new URL("..", import.meta.url)),
    server: { middlewareMode: true },
  });
  t.after(() => server.close());

  const app = await server.ssrLoadModule("/src/App.tsx");
  const timing = app.phaseTimingLabels([
    { state: "DETECTED", at: "2026-08-30T17:14:48.348321Z", reason: null },
    { state: "QUARANTINED", at: "2026-08-30T17:14:59.967605Z", reason: null },
    { state: "AWAITING_APPROVAL", at: "2026-08-30T17:15:22.950458Z", reason: null },
    { state: "APPROVED", at: "2026-08-30T17:15:36.747819Z", reason: null },
    { state: "VERIFIED", at: "2026-08-30T17:15:43.754250Z", reason: null },
  ]);

  assert.deepEqual(timing, {
    quarantine: "11.6 SEC",
    automatedPlanning: "34.6 SEC",
    humanReview: "13.8 SEC",
    approvedExecution: "7.01 SEC",
    total: "55.4 SEC",
  });
});

test("Model Armor detection is labeled as a security block, not a workflow match", async (t) => {
  const previousWindow = globalThis.window;
  globalThis.window = { location: { search: "" } };
  t.after(() => {
    globalThis.window = previousWindow;
  });

  const server = await createServer({
    appType: "custom",
    logLevel: "silent",
    root: fileURLToPath(new URL("..", import.meta.url)),
    server: { middlewareMode: true },
  });
  t.after(() => server.close());

  const app = await server.ssrLoadModule("/src/App.tsx");

  assert.equal(app.modelArmorLabel("MATCH", true), "INJECTION MATCH / BLOCKED");
  assert.equal(app.modelArmorLabel("CLEAR", false), "CLEAR");
});

test("agent roster presents the deployed Gemini 3.7 Flash model", async (t) => {
  const previousWindow = globalThis.window;
  globalThis.window = { location: { search: "" } };
  t.after(() => {
    globalThis.window = previousWindow;
  });

  const server = await createServer({
    appType: "custom",
    logLevel: "silent",
    root: fileURLToPath(new URL("..", import.meta.url)),
    server: { middlewareMode: true },
  });
  t.after(() => server.close());

  const app = await server.ssrLoadModule("/src/App.tsx");
  const models = app.agents.map((agent) => agent[2]);
  const legacyFlashLabel = `Gemini 3.${"6"} Flash`;

  assert.equal(models.includes(legacyFlashLabel), false);
  assert.equal(models.filter((model) => model === "Gemini 3.7 Flash").length, 4);
});

test("default public recovery points to the current Gemini 3.7 flagship", async (t) => {
  const previousWindow = globalThis.window;
  globalThis.window = { location: { search: "" } };
  t.after(() => {
    globalThis.window = previousWindow;
  });

  const server = await createServer({
    appType: "custom",
    logLevel: "silent",
    root: fileURLToPath(new URL("..", import.meta.url)),
    server: { middlewareMode: true },
  });
  t.after(() => server.close());

  const app = await server.ssrLoadModule("/src/App.tsx");
  assert.equal(app.publicProofs[0][1], "inc-invoice-a171b0ff1b9644e0");
});

test("the hosted command room declares a favicon instead of generating a 404", async () => {
  const indexPath = fileURLToPath(new URL("../index.html", import.meta.url));
  const html = await readFile(indexPath, "utf8");

  assert.match(html, /<link rel="icon"/);
});
