/**
 * executionEngine - simulator and live-broker adapter placeholder.
 *
 * slippage = base_slippage + k * volatility * sqrt(order_value / ADV)
 */

// src/services/executionEngine.ts
import prisma from '../utils/prismaClient';

/**
 * executionEngine - simple simulator and live-broker adapter placeholder.
 * slippage = base_slippage + k * volatility * sqrt(order_value / ADV)
 */

export async function executeOrder(proposal: {
  symbol: string;
  side: 'BUY' | 'SELL' | string;
  qty: number;
  price: number;
}) {
  const env = (globalThis as any).process?.env ?? {};
  const paper = env.PAPER_TRADING !== 'false';
  const price = proposal.price;
  const slippage_pct = 0.001 + 0.002 * 0.5; // sample constant for demo
  const executed_price = Number((price * (1 + (proposal.side === 'BUY' ? slippage_pct : -slippage_pct))).toFixed(2));
  const order = await prisma.order.create({
    data: {
      symbol: proposal.symbol,
      side: proposal.side,
      qty: proposal.qty,
      price: executed_price,
      status: paper ? 'FILLED_PAPER' : 'SENT_TO_BROKER'
    }
  });
  return order;
}
