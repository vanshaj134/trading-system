// backend/src/server.ts
// Defer requiring runtime dependencies to avoid editor TS errors when dev deps
// or generated types are not yet installed. Use dynamic `require` inside start().

declare function require(name: string): any;

async function start() {
  // Dynamically load runtime modules so the editor doesn't need their types.
  const dotenv = require("dotenv");
  dotenv.config?.();

  const pino = require("pino");
  const Fastify = require("fastify");

  const signalsRoutes = require("./routes/signals").default;
  const tradesRoutes = require("./routes/trades").default;

  const env = (globalThis as any).process?.env ?? {};
  const logger = pino({ level: env.LOG_LEVEL ?? "info" });
  const server = Fastify({ logger });

  // Register routes
  server.register(signalsRoutes, { prefix: "/api" });
  server.register(tradesRoutes, { prefix: "/api" });

  try {
  const port = Number(env.PORT) || 3000;
    await server.listen({ port, host: "0.0.0.0" });
    logger.info && logger.info(`Server listening on ${port}`);
  } catch (err) {
    logger.error && logger.error(err);
    // rethrow so process exits non-zero in CI
    throw err;
  }
}

start().catch((e) => {
  // If top-level start fails, log and exit with non-zero code
  // Use console as a fallback when logger isn't available
  try {
    console.error("Fatal error starting server:", e);
  } catch (_) {
    // ignore
  }
  // ensure non-zero exit if running locally or in CI
  const globalProcess: any = (globalThis as any).process;
  if (globalProcess && typeof globalProcess.exit === "function") globalProcess.exit(1);
});
