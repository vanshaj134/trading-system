"use strict";
/**
 * calcUtils - common financial calculations.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.calcATR = calcATR;
// src/utils/calcUtils.ts
function calcATR(prices, period = 14) {
    if (!prices || prices.length < 2)
        return 0.01;
    let sum = 0;
    const start = Math.max(1, prices.length - period);
    for (let i = start; i < prices.length; i++) {
        sum += Math.abs(prices[i] - prices[i - 1]);
    }
    const denom = Math.min(period, prices.length - 1) || 1;
    return sum / denom;
}
