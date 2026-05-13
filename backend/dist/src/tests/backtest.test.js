"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const riskEngine_1 = require("../services/riskEngine");
test('basic backtest risk check', async () => {
    const signal = { symbol: 'AAPL', score: 0.9 };
    const r = await (0, riskEngine_1.runRiskEngineForSignal)(signal);
    expect(r).toHaveProperty('qty');
    expect(r).toHaveProperty('symbol', 'AAPL');
});
