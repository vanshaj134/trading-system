"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.createTradeHandler = createTradeHandler;
exports.listTradesHandler = listTradesHandler;
exports.getTradeHandler = getTradeHandler;
// src/controllers/tradeController.ts
const prismaClient_1 = __importDefault(require("../utils/prismaClient"));
async function createTradeHandler(payload) {
    const { symbol, action, quantity, price, portfolioId, signalId } = payload;
    const trade = await prismaClient_1.default.trade.create({
        data: {
            symbol,
            action,
            quantity,
            price,
            status: 'PENDING',
            portfolioId,
            signalId
        }
    });
    // Simulate execution (paper trade)
    const executed = await prismaClient_1.default.trade.update({
        where: { id: trade.id },
        data: { status: 'EXECUTED', executionTime: new Date() }
    });
    await prismaClient_1.default.systemLog.create({
        data: {
            level: 'INFO',
            message: `Trade executed: ${symbol} ${action} qty=${quantity} @${price}`,
            context: { tradeId: executed.id }
        }
    });
    return executed;
}
async function listTradesHandler() {
    return await prismaClient_1.default.trade.findMany({ orderBy: { createdAt: 'desc' }, include: { portfolio: true, signal: true } });
}
async function getTradeHandler(id) {
    return await prismaClient_1.default.trade.findUnique({ where: { id }, include: { portfolio: true, signal: true } });
}
