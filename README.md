# HAM Agent 2 - Workwize Management Platform

A monorepo project for managing Workwize data with PII scrubbing, PostgreSQL caching, and AI assistance.

## ✨ Features

- 🔐 PII scrubbing for all cached data
- 📊 PostgreSQL database with Prisma ORM
- 🚀 Next.js frontend with asset management
- 🤖 AI assistant powered by Azure OpenAI
  - **Automatic query execution** - no code snippets, direct results
  - **Intelligent device classification** - Enhanced/Standard Windows/Mac detection
  - **Persistent chat history** - survives page navigation
  - **Single system prompt** - configured in Settings, auto-migrates from old versions
  - **Natural language filtering** - understands "in warehouse" vs "in Canada"
- 🔄 Workwize API integration
- 🐳 Podman/Docker PostgreSQL setup
- ⚙️ Settings page for AI configuration

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

6. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:3001
   - AI Assistant: http://localhost:3000/ai-assistant
   - Settings: http://localhost:3000/settings

## 📚 Documentation

- [INITIAL_BUILD.md](docs/INITIAL_BUILD.md) - Project setup and architecture
- [AI_ASSISTANT_FEATURES.md](docs/AI_ASSISTANT_FEATURES.md) - AI assistant guide (NEW)
- [CHANGELOG.md](docs/CHANGELOG.md) - Version history and changes (NEW)
- [RECENT_UPDATES.md](docs/RECENT_UPDATES.md) - Quick reference for latest updates (NEW)
- [PII_SCRUBBING_GUIDELINES.md](docs/PII_SCRUBBING_GUIDELINES.md) - Data handling
- [SECURITY_GUIDELINES.md](docs/SECURITY_GUIDELINES.md) - Security best practices
- [WORKWIZE_APIS.md](docs/WORKWIZE_APIS.md) - API reference

## Database Tables

- Orders
- Products
- Employees (PII scrubbed)
- Assets (PII scrubbed)
- Offices
- Warehouses
- Addresses (PII scrubbed)
- Offboards

**Current Data** (v2.0.3):

- 1,632 employees (94% with addresses)
- 1,699 assets
- 1,550 addresses
- 16 warehouses
- 5 offices

## 🤖 AI Assistant

The platform includes an AI-powered assistant for natural language queries:

**Features**:

- Ask questions about Workwize data in plain English
- Persistent chat history across page navigation
- Customizable system prompts via Settings page
- Scope-limited to Workwize data only (no general knowledge)
- Clear History button for conversation reset

**Example Queries**:

- "How many laptops are assigned to employees in the UK?"
- "Show me all offboarded employees from last quarter"
- "Which warehouses serve Germany?"

See [AI_ASSISTANT_FEATURES.md](docs/AI_ASSISTANT_FEATURES.md) for complete documentation.

## PII Scrubbing

All personally identifiable information is scrubbed before caching. See [PII Scrubbing Guidelines](docs/PII_SCRUBBING_GUIDELINES.md) for details.

## Security

See [Security Guidelines](docs/SECURITY_GUIDELINES.md) for security best practices.

## Version

**Current Version**: 2.0.3

**Recent Updates** (February 26, 2026):

- ✅ Persistent chat history with localStorage
- ✅ Custom system prompt support
- ✅ Settings page with smart UX
- ✅ Scope-limited AI default prompt
- ✅ Python script integration for data sync
- ✅ Fixed Azure OpenAI SSL certificate issue
- ✅ Repository cleanup (removed build artifacts)

See [CHANGELOG.md](docs/CHANGELOG.md) for complete version history.

## License

Private - All rights reserved
