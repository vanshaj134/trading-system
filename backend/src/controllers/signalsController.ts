// backend/src/controllers/signalsController.ts
import prisma from '../utils/prismaClient';
import { generateSignal } from '../services/signalService';

export async function createAndPersistSignal(symbol: string) {
  const sig = await generateSignal(symbol);

  const created = await prisma.signal.create({
    data: {
      symbol: sig.symbol,
      confidence: Number(sig.confidence),
      action: sig.action,
      source: 'engine',
      score: Number(sig.score),
    }
  });

  await prisma.systemLog.create({
    data: {
      level: 'INFO',
      message: `Signal generated for ${symbol}`,
      context: JSON.stringify({
        signalId: created.id,
        symbol: sig.symbol,
        action: sig.action,
        score: sig.score,
        confidence: sig.confidence,
        rationale: sig.rationale
      })
    }
  });

  return {
    db: created,
    computed: sig
  };
}

export async function fetchHistory(opts?: { symbol?: string; limit?: number; since?: Date }) {
  const where: any = {};
  if (opts?.symbol) where.symbol = opts.symbol;
  if (opts?.since) where.createdAt = { gte: opts.since };

  const limit = opts?.limit ?? 100;
  const rows = await prisma.signal.findMany({
    where,
    take: limit,
    orderBy: { createdAt: 'desc' },
  });

  return rows;
}
