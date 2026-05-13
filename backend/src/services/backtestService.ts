import prisma from "../utils/prismaClient";

export async function runSampleBacktest() {
  const trades: any[] = await prisma.trade.findMany({ orderBy: { createdAt: "asc" } });
  if (!trades.length) {
      console.warn("No trades found for backtest.");
      return { sharpe: 0, drawdown: 0, trades: 0 };
  }

  const pnlSeries: number[] = trades.map((t: any, i: number) => Math.sin(i / 5) * 1000 + 2000);
    const returns: number[] = pnlSeries.map((v: number, i: number) => (i === 0 ? 0 : (v - pnlSeries[i - 1]) / pnlSeries[i - 1]));

    const meanReturn = returns.reduce((a: number, b: number) => a + b, 0) / returns.length;
    const variance = returns.reduce((a: number, b: number) => a + Math.pow(b - meanReturn, 2), 0) / returns.length || 1e-12;
    const sharpe = meanReturn / Math.sqrt(variance);

    // compute worst drawdown
    let peak = pnlSeries[0];
    let maxDrawdown = 0;
    for (let i = 0; i < pnlSeries.length; i++) {
      if (pnlSeries[i] > peak) peak = pnlSeries[i];
      const dd = peak - pnlSeries[i];
      if (dd > maxDrawdown) maxDrawdown = dd;
    }

    await prisma.metric.create({
      data: { name: "SampleBacktest", sharpe, drawdown: maxDrawdown, tradesTested: trades.length }
    });

    return { sharpe, drawdown: maxDrawdown, trades: trades.length };
}
