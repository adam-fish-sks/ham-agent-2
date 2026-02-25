# HAM Agent 2 - Workwize Management Platform

A monorepo project for managing Workwize data with PII scrubbing, PostgreSQL caching, and AI assistance.

## Features

- 🔐 PII scrubbing for all cached data
- 📊 PostgreSQL database with Prisma ORM
- 🚀 Next.js frontend with asset management
- 🤖 AI assistant powered by Azure OpenAI
- 🔄 Workwize API integration
- 🐳 Podman/Docker PostgreSQL setup

## Project Structure

```
ham-agent-2/
├── packages/
│   ├── backend/       # API server and Workwize integration
│   ├── frontend/      # Next.js web application
│   ├── database/      # Prisma schema and migrations
│   └── shared/        # Shared utilities and PII scrubbing
├── data-samples/      # Sample JSON from Workwize APIs
└── docs/              # Documentation
```

## Prerequisites

- Node.js >= 18.0.0
- Podman or Docker
- npm >= 9.0.0

## Getting Started

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Set up environment variables**
   - Copy `.env.example` to `.env`
   - Add your Workwize API key and Azure OpenAI credentials

3. **Start PostgreSQL database**
   ```bash
   podman-compose up -d
   ```

4. **Initialize database**
   ```bash
   npm run db:push
   ```

5. **Start development servers**
   ```bash
   npm run dev
   ```

## Database Tables

- Orders
- Products
- Employees (PII scrubbed)
- Assets (PII scrubbed)
- Offices
- Warehouses
- Addresses (PII scrubbed)
- Offboards

## PII Scrubbing

All personally identifiable information is scrubbed before caching. See [PII Scrubbing Guidelines](docs/PII_SCRUBBING_GUIDELINES.md) for details.

## Security

See [Security Guidelines](docs/SECURITY_GUIDELINES.md) for security best practices.

## License

Private - All rights reserved
