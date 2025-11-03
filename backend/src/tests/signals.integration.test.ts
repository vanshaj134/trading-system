// backend/src/tests/signals.integration.test.ts
import prisma from '../utils/prismaClient';
import { createAndPersistSignal, fetchHistory } from '../controllers/signalsController';

describe('signals persistence', () => {
  beforeAll(async () => {
    await prisma.$connect();
  });

  afterAll(async () => {
    await prisma.signal.deleteMany({ where: { source: 'engine' } });
    await prisma.$disconnect();
  });

  test('create and fetch', async () => {
    const symbol = 'TESTIN';
    const created = await createAndPersistSignal(symbol);
    expect(created.db).toBeDefined();
    expect(created.db.symbol).toBe(symbol);
    const rows = await fetchHistory({ symbol, limit: 5 });
    expect(Array.isArray(rows)).toBe(true);
    expect(rows.length).toBeGreaterThanOrEqual(1);
    expect(rows[0].symbol).toBe(symbol);
  }, 20000);
});
