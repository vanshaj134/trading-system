"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
let PrismaClient;
try {
    PrismaClient = require('@prisma/client').PrismaClient;
}
catch (e) {
    // Fallback stub for editor/runtime until @prisma/client is available
    PrismaClient = class {
        constructor() { }
        async $connect() { }
        async $disconnect() { }
    };
}
const prisma = new PrismaClient({
    log: [
        { level: 'info', emit: 'stdout' },
        { level: 'warn', emit: 'stdout' },
        { level: 'error', emit: 'stdout' }
    ]
});
exports.default = prisma;
