// backend/src/tests/riskEngine.test.ts
// @ts-nocheck
import { runRiskEngineForSignal } from "../services/riskEngine";

test("riskEngine returns order proposal", async () => {
  const sig = { symbol: "AAPL", score: 0.8 } as any;
  const order = await runRiskEngineForSignal(sig);
  expect(order).toBeDefined();
  expect(order.qty).toBeGreaterThan(0);
});
