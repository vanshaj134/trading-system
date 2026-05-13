"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
// backend/src/tests/riskEngine.test.ts
// @ts-nocheck
const riskEngine_1 = require("../services/riskEngine");
test("riskEngine returns order proposal", async () => {
    const sig = { symbol: "AAPL", score: 0.8 };
    const order = await (0, riskEngine_1.runRiskEngineForSignal)(sig);
    expect(order).toBeDefined();
    expect(order.qty).toBeGreaterThan(0);
});
