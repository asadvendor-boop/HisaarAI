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
    { state: "DETECTED", at: "2026-08-25T08:06:51.896741Z", reason: null },
    { state: "QUARANTINED", at: "2026-08-25T08:07:23.773578Z", reason: null },
    { state: "AWAITING_APPROVAL", at: "2026-08-25T08:07:45.889274Z", reason: null },
    { state: "APPROVED", at: "2026-08-25T08:11:08.859073Z", reason: null },
    { state: "VERIFIED", at: "2026-08-25T08:11:19.611632Z", reason: null },
  ]);

  assert.deepEqual(timing, {
    quarantine: "31.9 SEC",
    automatedPlanning: "54.0 SEC",
    humanReview: "203.0 SEC",
    approvedExecution: "10.8 SEC",
    total: "267.7 SEC",
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

test("the hosted command room declares a favicon instead of generating a 404", async () => {
  const indexPath = fileURLToPath(new URL("../index.html", import.meta.url));
  const html = await readFile(indexPath, "utf8");

  assert.match(html, /<link rel="icon"/);
});
