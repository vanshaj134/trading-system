// backend/src/routes/signalRoute.ts
import { FastifyInstance } from 'fastify';
import { createAndPersistSignal, fetchHistory } from '../controllers/signalsController';

export default async function signalRoute(fastify: FastifyInstance) {
  fastify.get('/:symbol', async (request, reply) => {
    const symbol = String((request.params as any)?.symbol ?? '').toUpperCase();
    if (!symbol) return reply.code(400).send({ error: 'symbol required' });

    try {
      const result = await createAndPersistSignal(symbol);
      return reply.code(201).send({
        signal: result.db,
        computed: result.computed
      });
    } catch (err: any) {
      fastify.log?.error?.(err);
      return reply.code(500).send({ error: 'signal generation failed', details: String(err?.message ?? err) });
    }
  });

  fastify.get('/history', async (request, reply) => {
    const q = request.query as any;
    const symbol = q?.symbol ? String(q.symbol).toUpperCase() : undefined;
    const limit = q?.limit ? Math.min(1000, Number(q.limit)) : 100;
    try {
      const rows = await fetchHistory({ symbol, limit });
      return reply.code(200).send({ signals: rows });
    } catch (err: any) {
      fastify.log?.error?.(err);
      return reply.code(500).send({ error: 'failed reading history' });
    }
  });
}
