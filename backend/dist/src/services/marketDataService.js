"use strict";
/**
 * marketDataService - adapter layer to fetch price series, fundamentals, and news.
 * For starter, returns deterministic mock data.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.getHistoricalPrices = getHistoricalPrices;
async function getHistoricalPrices(symbol, lookback = 100) {
    const base = 100 + (symbol.charCodeAt(0) % 30);
    const series = [];
    for (let i = 0; i < lookback; i++)
        series.push(Number((base + Math.sin(i / 4) * 2 + (i % 7) * 0.2).toFixed(2)));
    return series;
}
