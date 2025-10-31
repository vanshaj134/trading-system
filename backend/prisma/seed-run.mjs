import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

async function main() {
  console.log('🌱 Seeding demo data (JS runner)...')

  const user = await prisma.user.upsert({
    where: { email: 'demo@trader.ai' },
    update: {},
    create: {
      email: 'demo@trader.ai',
      name: 'Demo Trader',
      portfolios: {
        create: { name: 'Default Portfolio' }
      }
    }
  })

  const portfolio = await prisma.portfolio.findFirst({ where: { userId: user.id } })

  if (portfolio) {
    await prisma.signal.createMany({
      data: [
        { symbol: 'AAPL', action: 'BUY', confidence: 0.82, source: 'seed', userId: user.id },
        { symbol: 'MSFT', action: 'SELL', confidence: 0.65, source: 'seed', userId: user.id }
      ]
    })
  }

  console.log('✅ Seeding complete (JS runner)!')
}

main()
  .then(async () => {
    await prisma.$disconnect()
  })
  .catch(async (e) => {
    console.error(e)
    try {
      await prisma.$disconnect()
    } catch (_) {}
    process.exit(1)
  })
