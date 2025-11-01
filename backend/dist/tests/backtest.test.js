"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
// backend/src/tests/backtest.test.ts
// @ts-nocheck
const backtestService_1 = require("../services/backtestService");
describe("Backtest metrics", () => {
    it("calculates Sharpe and drawdown", async () => {
        const result = await (0, backtestService_1.runSampleBacktest)();
        expect(result).toHaveProperty("sharpe");
        expect(result).toHaveProperty("drawdown");
    });
});
