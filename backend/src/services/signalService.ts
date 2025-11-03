// backend/src/services/signalService.ts
import marketDataService from './marketDataService';
import { mean, std } from '../utils/calcUtils';

export type GeneratedSignal = {
  symbol: string;
  action: 'BUY' | 'SELL' | 'HOLD';
  score: number;
  confidence: number;
  momentum: number;
  volatility: number;
  rationale: string;
};

export async function generateSignal(symbol: string, opts?: { lookback?: number }): Promise<GeneratedSignal> {
  const lookback = opts?.lookback ?? 30;
  const series = await marketDataService.generateSeries(symbol, { length: lookback, stepMinutes: 5 });

  if (!series || series.length < 3) {
    return {
      symbol,
      action: 'HOLD',
      score: 0,
      confidence: 0.25,
      momentum: 0,
      volatility: 0,
      rationale: 'insufficient data',
    };
  }

  const prices = series.map((p) => p.price);
  const first = prices[0];
  const last = prices[prices.length - 1];

  const momentum = (last - first) / Math.max(1e-8, first);

  const logRets: number[] = [];
  for (let i = 1; i < prices.length; i++) {
    logRets.push(Math.log(prices[i] / prices[i - 1] || 1));
  }
  const volatility = Math.max(1e-8, std(logRets));

  const score = momentum / (volatility + 1e-8);

  const n = prices.length;
  const raw = Math.abs(score);
  const sigmoid = (x: number) => 1 / (1 + Math.exp(-x));
  const sampleFactor = Math.min(1, Math.sqrt(n) / Math.sqrt(lookback));
  const confidence = Math.min(0.999, Math.max(0.01, sigmoid(raw) * sampleFactor));

  const buyThreshold = 0.15;
  const sellThreshold = -0.15;
  let action: 'BUY' | 'SELL' | 'HOLD' = 'HOLD';
  if (score >= buyThreshold) action = 'BUY';
  else if (score <= sellThreshold) action = 'SELL';

  const rationale = `momentum=${momentum.toFixed(5)}, vol=${volatility.toFixed(5)}, score=${score.toFixed(4)}`;

  return {
    symbol,
    action,
    score,
    confidence,
    momentum,
    volatility,
    rationale,
  };
}

export default generateSignal;
