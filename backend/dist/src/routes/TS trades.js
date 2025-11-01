"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.default = default_1;
// backend/src/routes/trades.ts
// Use `any` for request/reply types to avoid requiring dev type packages in the editor.
// Removed dependency on zod for runtime checks.
const tradeController_1 = require("../controllers/tradeController");
async function default_1(server, opts) {
    server.get("/trades", async (_request, reply) => {
        const data = await (0, tradeController_1.listTradesHandler)();
        return reply.code(200).send(data);
    });
    server.get("/trades/:id", async (request, reply) => {
        try {
            const params = { id: String(request.params?.id ?? "") };
            if (!params.id)
                return reply.code(400).send({ error: "Missing id" });
            const t = await (0, tradeController_1.getTradeHandler)(params.id);
            if (!t)
                return reply.code(404).send({ error: "Trade not found" });
            return reply.code(200).send(t);
        }
        catch (err) {
            server.log?.error?.(err);
            return reply.code(400).send({ error: "Invalid request" });
        }
    });
    server.post("/trades", async (request, reply) => {
        try {
            const payload = request.body || {};
            if (!payload.symbol || !payload.action || typeof payload.quantity !== 'number' || typeof payload.price !== 'number') {
                return reply.code(400).send({ error: 'symbol, action, quantity(number) and price(number) are required' });
            }
            const res = await (0, tradeController_1.createTradeHandler)(payload);
            return reply.code(201).send(res);
        }
        catch (err) {
            server.log?.error?.(err);
            return reply.code(400).send({ error: "Invalid payload" });
        }
    });
}
