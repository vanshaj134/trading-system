// backend/src/routes/marketDataRoute.ts
import { FastifyInstance } from 'fastify';
import marketDataService from '../services/marketDataService';

export default async function marketDataRoute(fastify: FastifyInstance) {
  fastify.get('/:symbol', async (request, reply) => {
    const symbol = String((request.params as any)?.symbol ?? '').toUpperCase();
    if (!symbol) return reply.code(400).send({ error: 'symbol required' });

    try {
      const snapshot = await marketDataService.fetch(symbol);
      const recent = await marketDataService.generateSeries(symbol, { length: 20, stepMinutes: 5 });
      return reply.code(200).send({ snapshot, recent });
    } catch (err: any) {
      fastify.log?.warn?.('market fetch failed, returning mock', err?.message ?? err);
      const now = Date.now();
      return reply.code(200).send({
        snapshot: { symbol, price: 100 + (symbol.charCodeAt(0) % 10), ts: now },
        recent: [{ ts: now, price: 100 + (symbol.charCodeAt(0) % 10) }]
      });
    }
  });
}
