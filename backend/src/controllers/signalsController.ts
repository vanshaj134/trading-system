// src/controllers/signalsController.ts
import prisma from '../utils/prismaClient';

export async function createSignalHandler(payload: {
  symbol: string;
  action: string;
  confidence?: number;
  score?: number;
  source?: string;
  userId?: string;
}) {
  const { symbol, action, confidence = 0, score, source, userId } = payload;

  const signal = await prisma.signal.create({
    data: {
      symbol,
      action,
      confidence,
      score,
      source,
      userId
    }
  });

  // Log
  await prisma.systemLog.create({
    data: {
      level: 'INFO',
      message: `Signal created: ${symbol} ${action}`,
      context: { signalId: signal.id }
    }
  });

  // If auto-trade logic is desired, call a trade engine here (defer to tradeController)
  return { success: true, signal };
}

export async function listSignalsHandler() {
  return await prisma.signal.findMany({ orderBy: { createdAt: 'desc' }, take: 200 });
}

export async function getSignalHandler({ id }: { id: string }) {
  return await prisma.signal.findUnique({ where: { id } });
}
