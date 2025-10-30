# Backend — GitHub Actions CI

This backend runs entirely in GitHub Actions — no local setup required.

### Workflow steps
1. Install dependencies
2. Generate Prisma client
3. Run SQLite migrations
4. Seed demo data
5. Run lint & tests

Check your workflow logs in **Actions → Backend CI**.

If you do run locally:
```powershell
cd backend
npm install
npx prisma generate
npx prisma migrate dev --name init
npx ts-node prisma/seed.ts
npm test
npm run dev
```
// trigger CI backend workflow
