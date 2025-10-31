// src/utils/prismaClient.ts
// Use dynamic require with a safe fallback so the editor doesn't fail
// before `npm ci` and `npx prisma generate` have been run.
declare function require(name: string): any;

let PrismaClient: any;
try {
  PrismaClient = require('@prisma/client').PrismaClient;
} catch (e) {
  // Fallback stub for editor/runtime until @prisma/client is available
  PrismaClient = class {
    constructor() {}
    async $connect() {}
    async $disconnect() {}
  };
}

const prisma = new PrismaClient({
  log: [
    { level: 'info', emit: 'stdout' },
    { level: 'warn', emit: 'stdout' },
    { level: 'error', emit: 'stdout' }
  ]
});

export default prisma;
