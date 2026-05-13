"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.default = default_1;
// backend/src/routes/trades.ts
// Fastify route plugin for trades
const _tradeCtrl = require('../controllers/tradeController');
const { createTradeHandler, listTradesHandler, getTradeHandler } = _tradeCtrl;
async function default_1(server, opts) {
    server.get('/trades', async (_request, reply) => {
        const data = await listTradesHandler();
        return reply.code(200).send(data);
    });
    server.get('/trades/:id', async (request, reply) => {
        const id = String(request.params?.id ?? '');
        if (!id)
            return reply.code(400).send({ error: 'Missing id' });
        const t = await getTradeHandler(id);
        if (!t)
            return reply.code(404).send({ error: 'Trade not found' });
        return reply.code(200).send(t);
    });
    server.post('/trades', async (request, reply) => {
        const payload = request.body || {};
        if (!payload.symbol || !payload.action || typeof payload.quantity !== 'number' || typeof payload.price !== 'number') {
            return reply.code(400).send({ error: 'symbol, action, quantity(number) and price(number) are required' });
        }
        const res = await createTradeHandler(payload);
        return reply.code(201).send(res);
    });
}
