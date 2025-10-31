// backend/src/routes/trades.ts
// Use `any` for request/reply types to avoid requiring dev type packages in the editor.
// Removed dependency on zod for runtime checks.
import {
  createTradeHandler,
  listTradesHandler,
  getTradeHandler
} from "../controllers/tradeController";

export default async function (server: any, opts: any) {
  server.get("/trades", async (_request: any, reply: any) => {
    const data = await listTradesHandler();
    return reply.code(200).send(data);
  });

  server.get("/trades/:id", async (request: any, reply: any) => {
    try {
        const params = { id: String(request.params?.id ?? "") };
        if (!params.id) return reply.code(400).send({ error: "Missing id" });
      const t = await getTradeHandler(params.id);
      if (!t) return reply.code(404).send({ error: "Trade not found" });
      return reply.code(200).send(t);
    } catch (err) {
      server.log?.error?.(err);
      return reply.code(400).send({ error: "Invalid request" });
    }
  });

  server.post("/trades", async (request: any, reply: any) => {
    try {
        const payload = request.body as any || {};
        if (!payload.symbol || !payload.action || typeof payload.quantity !== 'number' || typeof payload.price !== 'number') {
          return reply.code(400).send({ error: 'symbol, action, quantity(number) and price(number) are required' });
        }
      const res = await createTradeHandler(payload as any);
      return reply.code(201).send(res);
    } catch (err) {
      server.log?.error?.(err);
      return reply.code(400).send({ error: "Invalid payload" });
    }
  });
}
