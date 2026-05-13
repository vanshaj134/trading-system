// Minimal ambient declarations to silence missing type packages in the skeleton
// Minimal ambient declarations to silence missing type packages in the skeleton
declare module 'express'
declare module 'fastify'

declare var process: any

// Declarations for local modules (skeleton) to avoid requiring external type packages
declare module './routes/signals' {
	const router: any
	export default router
}

declare module '../controllers/signalsController' {
	export function getSignals(): any
}

declare module '../controllers/tradeController' {
	export function createTradeHandler(...args: any[]): any
	export function listTradesHandler(...args: any[]): any
	export function getTradeHandler(...args: any[]): any
}

// Jest globals used in tests (ambient for editor/CI until types are installed)
declare var test: any
declare var it: any
declare var describe: any
declare var expect: any
