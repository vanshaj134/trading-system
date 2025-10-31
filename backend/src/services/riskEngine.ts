/**
 * riskEngine - position sizing and risk checks.
 *
 * Formula:
 * volatility = ATR(14) / price
 * position_size = (risk_budget * account_value) / (volatility * price) * liquidity_adj
 *
 * Returns a proposed order object { symbol, side, qty, price, reason }
 */

import prisma from '../utils/prismaClient';
import { calcATR } from '../utils/calcUtils';

export async function runRiskEngineForSignal(signal: any) {
  const account_value = 100000;
  const risk_budget = 0.01;
  const lastPrices = await getMockPrices(signal.symbol);
  const price = lastPrices[lastPrices.length - 1] || 100;
  const atr = calcATR(lastPrices, 14);
  const volatility = atr / price || 0.02;
  const liquidity_adj = 1.0;

  const raw_size = (risk_budget * account_value) / (volatility * price);
  const size = Math.max(1, Math.floor(raw_size * liquidity_adj));
  const side = signal.score >= 0 ? 'BUY' : 'SELL';
  const order = {
    symbol: signal.symbol,
    side,
    qty: size,
    price,
    status: 'PROPOSED',
    reason: `position_size based on risk_budget=${risk_budget}, vol=${volatility.toFixed(4)}`
  };
  return order;
}

// Mock price generator (replace with real marketDataService)
async function getMockPrices(symbol: string) {
  const base = 100 + (symbol.charCodeAt(0) % 50);
  const series = [];
  for (let i = 0; i < 30; i++) series.push(base + Math.sin(i / 3) * 2 + (i % 5));
  return series;
}
