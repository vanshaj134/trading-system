// backend/src/routes/trades.ts
// Fastify route plugin for trades
const _tradeCtrl: any = require('../controllers/tradeController')
const { createTradeHandler, listTradesHandler, getTradeHandler } = _tradeCtrl

export default async function (server: any, opts: any) {
  server.get('/trades', async (_request: any, reply: any) => {
    const data = await listTradesHandler()
    return reply.code(200).send(data)
  })

  server.get('/trades/:id', async (request: any, reply: any) => {
    const id = String(request.params?.id ?? '')
    if (!id) return reply.code(400).send({ error: 'Missing id' })
    const t = await getTradeHandler(id)
    if (!t) return reply.code(404).send({ error: 'Trade not found' })
    return reply.code(200).send(t)
  })

  server.post('/trades', async (request: any, reply: any) => {
    const payload = request.body || {}
    if (!payload.symbol || !payload.action || typeof payload.quantity !== 'number' || typeof payload.price !== 'number') {
      return reply.code(400).send({ error: 'symbol, action, quantity(number) and price(number) are required' })
    }
    const res = await createTradeHandler(payload as any)
    return reply.code(201).send(res)
  })
}
