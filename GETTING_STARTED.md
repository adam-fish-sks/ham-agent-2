# Getting Started

Follow these steps to set up and run the HAM Agent 2 project.

## Prerequisites

- Node.js >= 18.0.0
- npm >= 9.0.0
- Podman or Docker
- Git

## Step-by-Step Setup

### 1. Install Dependencies

```bash
npm install
```

This will install all dependencies for all packages in the monorepo.

### 2. Set Up Environment Variables

The `.env` file already contains your Workwize and Azure OpenAI credentials. Verify the database URL:

```env
DATABASE_URL=postgresql://ham_agent:ham_agent_password@localhost:5432/ham_agent_db
```

### 3. Start PostgreSQL Database

Using Podman:
```bash
podman-compose up -d
```

Or using Docker:
```bash
docker-compose up -d
```

Verify the database is running:
```bash
podman ps
# or
docker ps
```

You should see the `ham-agent-postgres` container running.

### 4. Initialize the Database

Generate Prisma client and push schema to database:

```bash
npm run db:generate
npm run db:push
```

### 5. Start Development Servers

In separate terminals, or use the monorepo command:

```bash
npm run dev
```

This will start both:
- Backend API server on http://localhost:3001
- Frontend Next.js app on http://localhost:3000

### 6. Sync Data from Workwize

1. Open http://localhost:3000 in your browser
2. Navigate to "Sync Data"
3. Click "Sync All Data" to pull data from Workwize API and cache it locally (with PII scrubbing)

### 7. Explore Features

- **Home**: Overview and quick links
- **Assets**: View all cached assets (PII scrubbed)
- **AI Assistant**: Chat with AI about your data
- **Sync Data**: Sync fresh data from Workwize

## Project Structure

```
ham-agent-2/
├── packages/
│   ├── backend/          # Express API server
│   │   └── src/
│   │       ├── routes/   # API endpoints
│   │       └── lib/      # Utilities (Workwize client, Azure OpenAI)
│   ├── frontend/         # Next.js web app
│   │   └── src/
│   │       ├── app/      # Pages (App Router)
│   │       └── components/
│   ├── database/         # Prisma schema and client
│   │   └── schema.prisma
│   └── shared/           # Shared utilities
│       └── pii-scrubbing.ts
├── data-samples/         # Sample JSON from Workwize APIs
└── docs/                 # Documentation
```

## Available Commands

### Root Level
- `npm run dev` - Start all dev servers
- `npm run build` - Build all packages
- `npm run db:generate` - Generate Prisma client
- `npm run db:push` - Push schema to database
- `npm run db:studio` - Open Prisma Studio

### Backend (packages/backend)
- `npm run dev` - Start backend server
- `npm run build` - Build backend

### Frontend (packages/frontend)
- `npm run dev` - Start Next.js dev server
- `npm run build` - Build frontend

## Important Notes

### PII Scrubbing
All data cached from Workwize is automatically scrubbed of PII:
- Employee names → `J***` (initial only)
- Emails → `j***@company.com` (anonymized)
- Street addresses → Removed (only city/state kept)
- Notes → PII patterns redacted

See [docs/PII_SCRUBBING_GUIDELINES.md](docs/PII_SCRUBBING_GUIDELINES.md) for details.

### Database
- PostgreSQL runs in a Podman/Docker container
- Data persists in a Docker volume
- To reset: `podman-compose down -v` (or `docker-compose down -v`)

### API Endpoints

Backend API (http://localhost:3001):
- `GET /api/employees` - List employees
- `POST /api/employees/sync` - Sync from Workwize
- `GET /api/assets` - List assets
- `POST /api/assets/sync` - Sync from Workwize
- `POST /api/sync/all` - Sync all data
- `POST /api/ai/chat` - Chat with AI assistant
- And more...

## Troubleshooting

### Database Connection Issues
1. Verify Podman/Docker container is running: `podman ps`
2. Check logs: `podman logs ham-agent-postgres`
3. Verify DATABASE_URL in `.env`

### Prisma Issues
```bash
# Regenerate Prisma client
npm run db:generate

# Reset database
podman-compose down -v
podman-compose up -d
npm run db:push
```

### Port Already in Use
- Backend uses port 3001
- Frontend uses port 3000
- PostgreSQL uses port 5432

Change ports in:
- Backend: `packages/backend/src/index.ts`
- Frontend: `packages/frontend/package.json` (dev script)
- PostgreSQL: `docker-compose.yml` or `podman-compose.yml`

## Next Steps

1. Review the PII scrubbing guidelines in `docs/PII_SCRUBBING_GUIDELINES.md`
2. Review security guidelines in `docs/SECURITY_GUIDELINES.md`
3. Customize the AI assistant prompts in `packages/backend/src/routes/ai.ts`
4. Add more features or customize the frontend UI
5. Set up proper authentication (see Security Guidelines)

## Support

For questions or issues, refer to:
- [Workwize API Docs](https://docs.goworkwize.com/)
- [Prisma Docs](https://www.prisma.io/docs/)
- [Next.js Docs](https://nextjs.org/docs)
- [Azure OpenAI Docs](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
