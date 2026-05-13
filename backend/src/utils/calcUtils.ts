/**
 * calcUtils - common financial calculations.
 */

// src/utils/calcUtils.ts
export function calcATR(prices: number[], period = 14) {
  if (!prices || prices.length < 2) return 0.01;
  let sum = 0;
  const start = Math.max(1, prices.length - period);
  for (let i = start; i < prices.length; i++) {
    sum += Math.abs(prices[i] - prices[i - 1]);
  }
  const denom = Math.min(period, prices.length - 1) || 1;
  return sum / denom;
}
