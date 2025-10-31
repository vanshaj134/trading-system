// backend/src/routes/signals.ts
// Use `any` for request/reply types to avoid type errors before dev deps are installed.

import {
  createSignalHandler,
  listSignalsHandler,
  getSignalHandler
} from "../controllers/signalsController";

export default async function (server: any, opts: any) {
  server.get("/signals", async (_request: any, reply: any) => {
    const data = await listSignalsHandler();
    return reply.code(200).send(data);
  });

  server.get(
    "/signals/:id",
    async (request: any, reply: any) => {
  const params = { id: String(request.params?.id ?? "") };
  if (!params.id) return reply.code(400).send({ error: "Missing id" });
  const s = await getSignalHandler({ id: params.id });
      if (!s) return reply.code(404).send({ error: "Not found" });
      return reply.code(200).send(s);
    }
  );

  server.post(
    "/signals",
    async (request: any, reply: any) => {
      const payload = request.body as any || {};
      if (!payload.symbol || !payload.action) {
        return reply.code(400).send({ error: "symbol and action are required" });
      }
      const res = await createSignalHandler(payload as any);
      return reply.code(201).send(res);
    }
  );
}
