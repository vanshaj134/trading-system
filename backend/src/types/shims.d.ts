// Temporary shims to keep TypeScript happy in the editor before dependencies are installed.
// These are lightweight and only intended to suppress 'cannot find module' errors
// so you can work in-editor. Once `npm ci` and `npx prisma generate` run, these
// can be removed.

declare module 'fastify' {
  export type FastifyInstance = any;
  export type FastifyRequest<T = any> = any;
  export type FastifyReply<T = any> = any;
  export default function Fastify(opts?: any): FastifyInstance;
}

declare module 'zod' {
  export const z: any;
}

declare module 'pino' {
  const pino: any;
  export default pino;
}

declare module 'dotenv' {
  export function config(): { parsed?: Record<string, string> };
}

declare module '@prisma/client' {
  // Minimal shims used by the editor. Real types are provided by generated @prisma/client
  export class PrismaClient {
    constructor(arg?: any);
    connect(): Promise<void>;
    $connect(): Promise<void>;
    $disconnect(): Promise<void>;
    [key: string]: any;
  }
  export type Trade = any;
  export type Metric = any;
  export type User = any;
  export { PrismaClient as default };
}

// Basic NodeJS env typings (helps with `process.env` usage)
declare namespace NodeJS {
  interface ProcessEnv {
    NODE_ENV?: string;
    PORT?: string;
    LOG_LEVEL?: string;
    PAPER_TRADING?: string;
  }
}

// Jest globals for tests (editor only)
declare var describe: any;
declare var it: any;
declare var test: any;
declare var expect: any;

export {};

// Minimal `process` global for editor/typechecker before @types/node is available
declare const process: {
  env: NodeJS.ProcessEnv;
  exit(code?: number): void;
  [key: string]: any;
};
