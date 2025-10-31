#!/usr/bin/env node
import fs from 'fs/promises';
import path from 'path';

const root = path.resolve(new URL(import.meta.url).pathname, '..', '..');
const backend = path.join(root, 'backend');

function log(msg){ console.log('[fix-types]', msg); }

async function write(filePath, content){
  await fs.mkdir(path.dirname(filePath), { recursive: true });
  await fs.writeFile(filePath, content, 'utf8');
  log(`Wrote ${path.relative(backend, filePath)}`);
}

async function main(){
  log('Starting type-fix operation...');

  // signals route (typed)
  const signals = `import type { FastifyPluginAsync, FastifyRequest, FastifyReply } from 'fastify';
import { z } from 'zod';
import { createSignalHandler, listSignalsHandler, getSignalHandler } from '../controllers/signalsController';

const signalsRoutes: FastifyPluginAsync = async (fastify, opts): Promise<void> => {
  fastify.get('/signals', async (request: FastifyRequest, reply: FastifyReply) => {
    const data = await listSignalsHandler();
    return reply.code(200).send(data);
  });

  fastify.get('/signals/:id', async (request: FastifyRequest, reply: FastifyReply) => {
    const params = z.object({ id: z.string() }).parse(request.params as any);
    const signal = await getSignalHandler({ id: params.id });
    if (!signal) return reply.code(404).send({ error: 'Signal not found' });
    return reply.code(200).send(signal);
  });

  fastify.post('/signals', async (request: FastifyRequest, reply: FastifyReply) => {
    const bodySchema = z.object({
      symbol: z.string(),
      action: z.string(),
      confidence: z.number().optional().default(0.0),
      score: z.number().optional(),
      source: z.string().optional(),
      userId: z.string().optional()
    });
    const payload = bodySchema.parse(request.body as any);
    const res = await createSignalHandler(payload as any);
    return reply.code(201).send(res);
  });
};

export default signalsRoutes;
`;

  // trades route (typed)
  const trades = `import type { FastifyPluginAsync, FastifyRequest, FastifyReply } from 'fastify';
import { z } from 'zod';
import { createTradeHandler, listTradesHandler, getTradeHandler } from '../controllers/tradeController';

const tradesRoutes: FastifyPluginAsync = async (fastify, opts): Promise<void> => {
  fastify.get('/trades', async (request: FastifyRequest, reply: FastifyReply) => {
    const data = await listTradesHandler();
    return reply.code(200).send(data);
  });

  fastify.get('/trades/:id', async (request: FastifyRequest, reply: FastifyReply) => {
    const params = z.object({ id: z.string() }).parse(request.params as any);
    const t = await getTradeHandler(params.id);
    if (!t) return reply.code(404).send({ error: 'Trade not found' });
    return reply.code(200).send(t);
  });

  fastify.post('/trades', async (request: FastifyRequest, reply: FastifyReply) => {
    const bodySchema = z.object({
      symbol: z.string(),
      action: z.string(),
      quantity: z.number(),
      price: z.number(),
      portfolioId: z.string(),
      signalId: z.string().optional()
    });
    const payload = bodySchema.parse(request.body as any);
    const res = await createTradeHandler(payload as any);
    return reply.code(201).send(res);
  });
};

export default tradesRoutes;
`;

  // tests - backtest
  const backtestTest = `import { runSampleBacktest } from '../services/backtestService';

describe('Backtest metrics', () => {
  it('calculates Sharpe and drawdown', async () => {
    const result = await runSampleBacktest();
    expect(result).toHaveProperty('sharpe');
    expect(result).toHaveProperty('drawdown');
  });
});
`;

  // tests - riskEngine
  const riskTest = `import { runRiskEngineForSignal } from '../services/riskEngine';

test('riskEngine returns order proposal', async () => {
  const sig = { symbol: 'AAPL', score: 0.8 } as any;
  const order = await runRiskEngineForSignal(sig);
  expect(order).toBeDefined();
  expect(order.qty).toBeGreaterThan(0);
});
`;

  await write(path.join(backend, 'src', 'routes', 'signals.ts'), signals);
  await write(path.join(backend, 'src', 'routes', 'trades.ts'), trades);
  await write(path.join(backend, 'src', 'tests', 'backtest.test.ts'), backtestTest);
  await write(path.join(backend, 'src', 'tests', 'riskEngine.test.ts'), riskTest);

  log('Type-fix operation complete.');
}

main().catch((err)=>{
  console.error(err);
  process.exit(1);
});
