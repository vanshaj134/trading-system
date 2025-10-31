import prisma from "../src/utils/prismaClient";

async function main() {
  console.log("🌱 Seeding demo data...");

  const user = await prisma.user.upsert({
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

  const portfolio = await prisma.portfolio.findFirst({ where: { userId: (user as any).id } });

  if (portfolio) {
    await prisma.signal.createMany({
      data: [
        { symbol: "AAPL", action: "BUY", confidence: 0.82, source: "seed", userId: (user as any).id },
        { symbol: "MSFT", action: "SELL", confidence: 0.65, source: "seed", userId: (user as any).id }
      ]
    });
  }

  console.log("✅ Seeding complete!");
}

main()
  .then(async () => {
    await prisma.$disconnect();
  })
  .catch(async (e) => {
    console.error(e);
    try {
      await prisma.$disconnect();
    } catch (_) {
      // ignore
    }
    throw e;
  });
