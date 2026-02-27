# Start Development Servers

## Quick Start

```powershell
# From project root
pnpm dev
```

This starts both frontend (port 3000) and backend (port 3001) simultaneously.

## Individual Servers

### Backend Only

```powershell
cd packages/backend
pnpm dev
```

### Frontend Only

```powershell
cd packages/frontend
pnpm dev
```

## Prerequisites

1. **Environment Variables** - Ensure `.env` file exists in project root with:

   ```
   DATABASE_URL=postgresql://ham_agent_2:ham_agent_2_password@localhost:5432/ham_agent_2_db
   WORKWIZE_KEY=your_key_here
   AZURE_OPENAI_ENDPOINT=your_endpoint
   AZURE_OPENAI_API_KEY=your_key
   ```

2. **PostgreSQL** - Database must be running on localhost:5432

3. **Dependencies** - Run `pnpm install` if first time

## Troubleshooting

**Port Already in Use:**

```powershell
# Kill processes on ports 3000 and 3001
Get-NetTCPConnection -LocalPort 3000,3001 -ErrorAction SilentlyContinue |
  Select-Object -ExpandProperty OwningProcess -Unique |
  ForEach-Object { Stop-Process -Id $_ -Force }
```

**Backend Won't Start:**

- Check DATABASE_URL is set in `.env`
- Verify PostgreSQL is running
- Ensure port 3001 is available

## Access Points

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:3001
- **API Status:** http://localhost:3000/status
- **Health Check:** http://localhost:3001/health
