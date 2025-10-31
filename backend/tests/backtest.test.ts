// backend/src/tests/backtest.test.ts
// @ts-nocheck
import { runSampleBacktest } from "../services/backtestService";

describe("Backtest metrics", () => {
  it("calculates Sharpe and drawdown", async () => {
    const result = await runSampleBacktest();
    expect(result).toHaveProperty("sharpe");
    expect(result).toHaveProperty("drawdown");
  });
});
