import { runRiskEngineForSignal } from '../services/riskEngine'

test('basic backtest risk check', async () => {
  const signal = { symbol: 'AAPL', score: 0.9 }
  const r = await runRiskEngineForSignal(signal)
  expect(r).toHaveProperty('qty')
  expect(r).toHaveProperty('symbol', 'AAPL')
})
