import assert from "node:assert/strict";
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
