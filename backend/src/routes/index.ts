// backend/src/routes/index.ts
import { FastifyInstance } from 'fastify';
import marketDataRoute from './marketDataRoute';
import signalRoute from './signalRoute';

export default async function routes(app: FastifyInstance) {
  app.register(marketDataRoute, { prefix: '/market' });
  app.register(signalRoute, { prefix: '/signal' });
}
