"use strict";
// backend/src/routes/signals.ts
// Use `any` for request/reply types to avoid type errors before dev deps are installed.
Object.defineProperty(exports, "__esModule", { value: true });
exports.default = default_1;
const signalsController_1 = require("../controllers/signalsController");
async function default_1(server, opts) {
    server.get("/signals", async (_request, reply) => {
        const data = await (0, signalsController_1.listSignalsHandler)();
        return reply.code(200).send(data);
    });
    server.get("/signals/:id", async (request, reply) => {
        const params = { id: String(request.params?.id ?? "") };
        if (!params.id)
            return reply.code(400).send({ error: "Missing id" });
        const s = await (0, signalsController_1.getSignalHandler)({ id: params.id });
        if (!s)
            return reply.code(404).send({ error: "Not found" });
        return reply.code(200).send(s);
    });
    server.post("/signals", async (request, reply) => {
        const payload = request.body || {};
        if (!payload.symbol || !payload.action) {
            return reply.code(400).send({ error: "symbol and action are required" });
        }
        const res = await (0, signalsController_1.createSignalHandler)(payload);
        return reply.code(201).send(res);
    });
}
