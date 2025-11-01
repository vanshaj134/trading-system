"use strict";
/**
 * executionEngine - simulator and live-broker adapter placeholder.
 *
 * slippage = base_slippage + k * volatility * sqrt(order_value / ADV)
 */
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.executeOrder = executeOrder;
// src/services/executionEngine.ts
const prismaClient_1 = __importDefault(require("../utils/prismaClient"));
/**
 * executionEngine - simple simulator and live-broker adapter placeholder.
 * slippage = base_slippage + k * volatility * sqrt(order_value / ADV)
 */
async function executeOrder(proposal) {
    const env = globalThis.process?.env ?? {};
    const paper = env.PAPER_TRADING !== 'false';
    const price = proposal.price;
    const slippage_pct = 0.001 + 0.002 * 0.5; // sample constant for demo
    const executed_price = Number((price * (1 + (proposal.side === 'BUY' ? slippage_pct : -slippage_pct))).toFixed(2));
    const order = await prismaClient_1.default.order.create({
        data: {
            symbol: proposal.symbol,
            side: proposal.side,
            qty: proposal.qty,
            price: executed_price,
            status: paper ? 'FILLED_PAPER' : 'SENT_TO_BROKER'
        }
    });
    return order;
}
