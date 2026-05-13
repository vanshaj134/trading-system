"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const prismaClient_1 = __importDefault(require("../src/utils/prismaClient"));
async function main() {
    console.log("🌱 Seeding demo data...");
    const user = await prismaClient_1.default.user.upsert({
        where: { email: "demo@trader.ai" },
        update: {},
        create: {
            email: "demo@trader.ai",
            name: "Demo Trader",
            portfolios: {
                create: {
                    name: "Default Portfolio"
                }
            }
        }
    });
    const portfolio = await prismaClient_1.default.portfolio.findFirst({ where: { userId: user.id } });
    if (portfolio) {
        await prismaClient_1.default.signal.createMany({
            data: [
                { symbol: "AAPL", action: "BUY", confidence: 0.82, source: "seed", userId: user.id },
                { symbol: "MSFT", action: "SELL", confidence: 0.65, source: "seed", userId: user.id }
            ]
        });
    }
    console.log("✅ Seeding complete!");
}
main()
    .then(async () => {
    await prismaClient_1.default.$disconnect();
})
    .catch(async (e) => {
    console.error(e);
    try {
        await prismaClient_1.default.$disconnect();
    }
    catch (_) {
        // ignore
    }
    throw e;
});
