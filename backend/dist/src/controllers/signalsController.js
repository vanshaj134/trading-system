"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.createSignalHandler = createSignalHandler;
exports.listSignalsHandler = listSignalsHandler;
exports.getSignalHandler = getSignalHandler;
// src/controllers/signalsController.ts
const prismaClient_1 = __importDefault(require("../utils/prismaClient"));
async function createSignalHandler(payload) {
    const { symbol, action, confidence = 0, score, source, userId } = payload;
    const signal = await prismaClient_1.default.signal.create({
        data: {
            symbol,
            action,
            confidence,
            score,
            source,
            userId
        }
    });
    // Log
    await prismaClient_1.default.systemLog.create({
        data: {
            level: 'INFO',
            message: `Signal created: ${symbol} ${action}`,
            context: { signalId: signal.id }
        }
    });
    // If auto-trade logic is desired, call a trade engine here (defer to tradeController)
    return { success: true, signal };
}
async function listSignalsHandler() {
    return await prismaClient_1.default.signal.findMany({ orderBy: { createdAt: 'desc' }, take: 200 });
}
async function getSignalHandler({ id }) {
    return await prismaClient_1.default.signal.findUnique({ where: { id } });
}
