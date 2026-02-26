# Technology Stack Contract

**Date:** January 8, 2026  
**Purpose:** Define standard technology stack for internal enterprise applications  
**Scope:** All future internal software development projects

---

## Table of Contents

1. [Monorepo Architecture](#1-monorepo-architecture)
2. [Frontend Technologies](#2-frontend-technologies)
3. [Backend Technologies](#3-backend-technologies)
4. [Database & Data Layer](#4-database--data-layer)
5. [Cloud Infrastructure (Azure)](#5-cloud-infrastructure-azure)
6. [DevOps & CI/CD](#6-devops--cicd)
7. [Development Tools](#7-development-tools)
8. [Security & Authentication](#8-security--authentication)
9. [Monitoring & Observability](#9-monitoring--observability)
10. [Integration & Messaging](#10-integration--messaging)

---

## 1. Monorepo Architecture

### 1.1 Turborepo

**Version:** 2.6.3+  
**Purpose:** Monorepo orchestration and build system

**Description:**  
Turborepo provides high-performance build system with intelligent caching, parallel execution, and task orchestration across multiple packages. It enables fast, incremental builds and simplified dependency management.

**Justification:**
- **Performance:** Caches build outputs locally and remotely, reducing build times by 80%+
- **Scalability:** Handles multiple apps/packages efficiently as project grows
- **Developer Experience:** Simple configuration, works with existing tools
- **Task Pipelines:** Manages complex build dependencies automatically
- **Remote Caching:** Teams share build artifacts via cloud cache

**Use Cases:**
- Building all apps/packages with single command
- Running tests across entire monorepo
- Managing dependencies between workspace packages
- Coordinating deployment pipelines

**Configuration:** `turbo.json`

---

### 1.2 pnpm Workspaces

**Version:** 9.0.0+  
**Purpose:** Package management and workspace organization

**Description:**  
pnpm is a fast, disk-space efficient package manager that uses hard links and symlinks to save disk space. Workspaces enable sharing code between multiple packages in a monorepo.

**Justification:**
- **Efficiency:** Uses ~33% less disk space than npm/yarn through content-addressable storage
- **Speed:** 2x faster than npm, competitive with yarn
- **Strict:** Prevents phantom dependencies by default
- **Workspace Protocol:** Native monorepo support with `workspace:*` dependencies
- **Security:** Better handling of package integrity

**Structure:**
```
├── apps/
│   ├── web/          # Next.js application
│   ├── api/          # Express API server
│   ├── worker/       # Background job processor
│   └── desktop/      # Tauri desktop app
├── packages/
│   ├── shared/       # Shared utilities & types
│   └── database/     # Prisma schema & client
```

**Configuration:** `pnpm-workspace.yaml`

---

## 2. Frontend Technologies

### 2.1 Next.js 14

**Version:** 14.2.35  
**Purpose:** Web application framework

**Description:**  
React-based framework with server-side rendering (SSR), static site generation (SSG), API routes, and App Router with React Server Components.

**Justification:**
- **Performance:** Automatic code splitting, image optimization, font optimization
- **SEO:** Server-side rendering improves search engine visibility
- **Developer Experience:** File-based routing, hot module replacement, TypeScript support
- **Deployment:** Optimized for serverless and container deployments
- **Standalone Output:** Generates minimal Docker images with `output: "standalone"`
- **Server Actions:** Type-safe server mutations without API routes

**Key Features Used:**
- App Router with Server Components
- Server Actions for mutations
- Standalone output for containerization
- Instrumentation hook for Application Insights
- Image optimization
- Environment variable handling

---

### 2.2 React 18

**Version:** 18.2.0  
**Purpose:** UI component library

**Description:**  
JavaScript library for building user interfaces with component-based architecture, hooks, and concurrent features.

**Justification:**
- **Industry Standard:** Most popular UI library with massive ecosystem
- **Concurrent Features:** Automatic batching, transitions, suspense
- **Hooks:** Modern state management and side effects
- **Server Components:** Reduces JavaScript bundle size via Next.js integration
- **Community:** Extensive resources, libraries, and talent pool

---

### 2.3 TypeScript

**Version:** 5.9.3  
**Purpose:** Type-safe JavaScript

**Description:**  
Strongly typed superset of JavaScript that compiles to plain JavaScript, providing static type checking and enhanced IDE support.

**Justification:**
- **Safety:** Catches errors at compile-time before runtime
- **Maintainability:** Self-documenting code through type definitions
- **Refactoring:** Confident large-scale refactors with type safety
- **IDE Support:** Autocomplete, inline documentation, refactoring tools
- **Team Collaboration:** Explicit contracts between modules/teams
- **Enterprise Standard:** Required for large codebases

**Configuration:** Individual `tsconfig.json` per package extending base configs

---

### 2.4 Tailwind CSS

**Version:** 3.3.6+  
**Purpose:** Utility-first CSS framework

**Description:**  
CSS framework that provides low-level utility classes for building custom designs directly in markup.

**Justification:**
- **Productivity:** Rapid UI development without context switching
- **Consistency:** Design system enforced through configuration
- **Performance:** Purges unused CSS automatically, minimal bundle size
- **Responsive:** Mobile-first responsive design built-in
- **Dark Mode:** Class-based dark mode support
- **Customization:** Highly configurable via `tailwind.config.js`

**Extensions:**
- `tailwindcss-animate`: Animation utilities
- Custom color palette (Uplift brand + Microsoft 365 colors)

---

### 2.5 Radix UI

**Version:** Latest (multiple packages)  
**Purpose:** Headless UI component library

**Description:**  
Unstyled, accessible UI components that provide behavior and accessibility while giving full control over styling.

**Justification:**
- **Accessibility:** WCAG compliant, keyboard navigation, screen reader support
- **Unstyled:** Complete styling control via Tailwind/CSS
- **Composability:** Build complex components from primitives
- **Quality:** Well-maintained by Modulz team, used by shadcn/ui
- **Type Safety:** Full TypeScript support

**Components Used:**
- Dialog, Dropdown Menu, Popover, Tooltip
- Select, Radio Group, Checkbox, Switch, Slider
- Tabs, Collapsible, Accordion
- Avatar, Progress, Separator, Scroll Area

---

### 2.6 shadcn/ui

**Purpose:** Pre-built component collection

**Description:**  
Collection of re-usable components built on Radix UI and Tailwind CSS that can be copied into projects and customized.

**Justification:**
- **Ownership:** Components live in your codebase, not node_modules
- **Customization:** Full control to modify components
- **Quality:** Production-ready, accessible components
- **Consistency:** Design system with built-in theming
- **Integration:** Works seamlessly with Radix + Tailwind

**Configuration:** `components.json`

---

### 2.7 React Hook Form + Zod

**Versions:** react-hook-form ^7.68.0, zod ^4.1.13  
**Purpose:** Form management and validation

**Description:**  
React Hook Form provides performant form handling with minimal re-renders. Zod provides TypeScript-first schema validation.

**Justification:**
- **Performance:** Minimal re-renders, uncontrolled components
- **DX:** Simple API, TypeScript integration via @hookform/resolvers
- **Validation:** Zod schemas provide runtime + compile-time type safety
- **Bundle Size:** Lightweight compared to Formik (20KB vs 50KB)
- **Features:** Field arrays, watch, conditional fields, async validation

**Integration:** `@hookform/resolvers/zod` bridges both libraries

---

### 2.8 Zustand

**Version:** 4.4.0+  
**Purpose:** Client-side state management

**Description:**  
Lightweight state management library using hooks with minimal boilerplate.

**Justification:**
- **Simplicity:** No providers, no Context API boilerplate
- **Performance:** Selective subscriptions prevent unnecessary re-renders
- **Size:** 1KB gzipped vs Redux (3KB+)
- **TypeScript:** Excellent type inference
- **DevTools:** Redux DevTools integration
- **Flexibility:** Works with or without React

---

### 2.9 Tauri 2

**Version:** 2.x  
**Purpose:** Desktop application framework

**Description:**  
Framework for building lightweight desktop applications using web technologies for UI and Rust for backend. Alternative to Electron with significantly smaller bundle sizes.

**Justification:**
- **Performance:** Native Rust backend, 10x smaller than Electron
- **Security:** Process isolation, capability-based security model
- **System Access:** Native OS integrations (notifications, tray, deep links)
- **Cross-Platform:** Single codebase for Windows, macOS, Linux
- **Modern:** Uses system WebView instead of bundling Chromium
- **Updater:** Built-in auto-update mechanism

**Common Plugins:**
- `tauri-plugin-notification`: Native system notifications
- `tauri-plugin-autostart`: Launch on login
- `tauri-plugin-opener`: Open URLs in browser
- `tauri-plugin-deep-link`: Custom URL scheme handling
- `tauri-plugin-clipboard-manager`: Clipboard access
- `tauri-plugin-localhost`: Local server hosting

**Configuration:** `tauri.conf.json`, `Cargo.toml`

**Note:** Desktop applications are optional depending on project requirements.

---

### 2.10 Vite

**Version:** 6.0.3+  
**Purpose:** Frontend build tool for desktop app

**Description:**  
Next-generation frontend build tool that leverages native ES modules for lightning-fast HMR and optimized production builds.

**Justification:**
- **Speed:** Instant HMR, fast cold starts
- **Simplicity:** Minimal configuration needed
- **Modern:** ESM-first approach
- **Tauri Integration:** Official Tauri integration
- **Production:** Rollup-based optimized builds

---

## 3. Backend Technologies

### 3.1 Node.js

**Version:** 20.0.0+  
**Purpose:** JavaScript runtime for backend services

**Description:**  
Event-driven JavaScript runtime built on Chrome's V8 engine for building scalable network applications.

**Justification:**
- **Full-Stack TypeScript:** Share code/types between frontend and backend
- **Performance:** Non-blocking I/O suitable for I/O-heavy workloads
- **Ecosystem:** npm/pnpm provides access to 2M+ packages
- **Deployment:** Wide cloud provider support, containerization
- **Long-Term Support:** Version 20 is LTS until April 2026
- **Modern Features:** ESM, top-level await, fetch API

---

### 3.2 Express

**Version:** 4.22.0+  
**Purpose:** Web application framework

**Description:**  
Minimal and flexible Node.js web application framework providing robust features for web and mobile applications.

**Justification:**
- **Maturity:** Battle-tested, 13+ years of production use
- **Simplicity:** Straightforward API, minimal learning curve
- **Middleware:** Extensive middleware ecosystem
- **Performance:** Lightweight, handles 15k+ req/sec
- **Documentation:** Comprehensive docs and community resources
- **Flexibility:** Unopinionated, allows architectural freedom

**Middleware Used:**
- `helmet`: Security headers
- `cors`: Cross-origin resource sharing
- `express-rate-limit`: Rate limiting
- Body parsers for JSON/URL-encoded data

---

### 3.3 tsup

**Version:** 8.0.0+  
**Purpose:** TypeScript bundler

**Description:**  
Zero-config TypeScript bundler powered by esbuild for building libraries and Node.js applications.

**Justification:**
- **Speed:** 100x faster than tsc for bundling
- **Simple:** Minimal configuration required
- **Features:** Automatic entry detection, source maps, declaration files
- **Watch Mode:** Fast rebuilds during development
- **Format Support:** CJS, ESM, IIFE outputs

**Configuration:** `tsup.config.ts` files

---

### 3.4 Pino

**Version:** 8.17.0+  
**Purpose:** Logging library

**Description:**  
Very low overhead Node.js logger with fast JSON serialization.

**Justification:**
- **Performance:** 5x faster than Winston, minimal overhead
- **Structured:** JSON logs for easy parsing and querying
- **Integration:** Works with Application Insights, log aggregators
- `pino-pretty`: Human-readable output during development
- **Child Loggers:** Context propagation through request lifecycle
- **Redaction:** Built-in secret redaction

---

### 3.5 BullMQ

**Version:** 5.1.0+  
**Purpose:** Job queue and background processing

**Description:**  
Redis-based queue for Node.js with advanced features like priorities, retries, rate limiting, and concurrency control.

**Justification:**
- **Reliability:** At-least-once delivery, job persistence
- **Features:** Priorities, delays, repeatable jobs, job events
- **Observability:** Built-in UI, progress tracking, metrics
- **Performance:** Handles 10,000+ jobs/second per queue
- **TypeScript:** Full type safety for job data
- **Redis:** Leverages Redis for speed and reliability

**Use Cases:**
- Email delivery and notifications
- Data synchronization with external systems
- Report generation
- Image processing
- Scheduled tasks
- Background data processing

---

## 4. Database & Data Layer

### 4.1 PostgreSQL

**Version:** 16 (Azure Flexible Server)  
**Purpose:** Primary relational database

**Description:**  
Advanced open-source relational database with support for JSON, full-text search, and strong ACID compliance.

**Justification:**
- **Reliability:** 35+ years of development, proven at scale
- **Features:** JSON/JSONB, full-text search, advanced indexing
- **Performance:** Handles millions of rows efficiently
- **Standards:** SQL standard compliant, portable queries
- **Azure Integration:** Fully managed via Azure Flexible Server
- **Security:** Row-level security, encryption at rest/transit
- **Extensibility:** PostGIS, pg_vector for future AI features

**Hosting:** Azure Database for PostgreSQL Flexible Server

---

### 4.2 Prisma ORM

**Version:** 5.7.0+  
**Purpose:** Database toolkit and ORM

**Description:**  
Next-generation TypeScript ORM with type-safe database client, declarative migrations, and visual database browser.

**Justification:**
- **Type Safety:** Auto-generated types matching exact schema
- **Developer Experience:** Intuitive API, excellent error messages
- **Migrations:** Declarative schema with automatic migration generation
- **Studio:** Built-in visual database browser (`prisma studio`)
- **Performance:** Optimized queries, connection pooling
- **Relations:** Easy relation traversal with `include`/`select`
- **Raw SQL:** Escape hatch for complex queries

**Features Used:**
- Schema definition in `schema.prisma`
- Auto-generated TypeScript client
- Migration management (`prisma migrate`)
- Database seeding scripts
- Multiple binary targets for Docker deployment

---

### 4.3 Redis

**Version:** 7 (Azure Cache for Redis)  
**Purpose:** Caching and session storage

**Description:**  
In-memory data structure store used as cache, message broker, and session store with sub-millisecond latency.

**Justification:**
- **Speed:** In-memory storage, <1ms response times
- **Features:** Pub/sub, sorted sets, geospatial, streams
- **Persistence:** Snapshot + AOF for durability
- **BullMQ Backend:** Queue job storage
- **Caching:** Application-level caching, session storage
- **Azure Managed:** Fully managed via Azure Cache for Redis

**Use Cases:**
- Session storage (user sessions)
- Application cache (frequently accessed data)
- BullMQ job queue backend
- Real-time metrics aggregation

**Library:** `ioredis` for Node.js client

---

## 5. Cloud Infrastructure (Azure)

### 5.1 Azure Container Apps

**Purpose:** Serverless container hosting

**Description:**  
Fully managed serverless container platform that automatically scales based on HTTP traffic, events, or CPU/memory load.

**Justification:**
- **Serverless:** No VM management, auto-scaling to zero
- **Cost-Effective:** Pay only for resources used
- **Scaling:** Automatic horizontal scaling based on demand
- **Deployment:** Direct integration with Azure Container Registry
- **Networking:** VNet integration, private endpoints
- **Managed:** Built on Kubernetes without K8s complexity

**Services Hosted:**
- API server (Express)
- Worker services (BullMQ processors)
- Future microservices

**Alternative:** Azure App Service (for simpler non-container deployments)

---

### 5.2 Azure Static Web Apps

**Purpose:** Hosting for Next.js frontend

**Description:**  
Globally distributed static site hosting with integrated CI/CD, custom domains, and built-in authentication.

**Justification:**
- **Performance:** Global CDN distribution, <50ms latency
- **Integration:** Native GitHub Actions integration
- **Free Tier:** Generous free tier for development
- **Features:** Custom domains, SSL, API routes
- **Scaling:** Automatic global scaling
- **Deployment:** Direct from GitHub with preview environments

**Alternative:** Azure App Service with standalone Next.js build

---

### 5.3 Azure Database for PostgreSQL Flexible Server

**Purpose:** Managed PostgreSQL hosting

**Description:**  
Fully managed PostgreSQL database service with zone-redundant high availability and flexible scaling.

**Justification:**
- **Managed:** Automatic backups, patching, monitoring
- **High Availability:** Zone-redundant HA with auto-failover
- **Performance:** Burstable to high-memory SKUs available
- **Security:** Private endpoints, encryption, Azure AD auth
- **Cost Control:** Stop/start capability, burstable SKUs for dev
- **Compliance:** SOC, ISO, HIPAA certifications

---

### 5.4 Azure Cache for Redis

**Purpose:** Managed Redis hosting

**Description:**  
Fully managed Redis cache with enterprise features and guaranteed SLA.

**Justification:**
- **Managed:** Automatic updates, backups, monitoring
- **Availability:** Multi-zone replication, 99.9% SLA
- **Performance:** Low latency, high throughput
- **Security:** Private endpoints, VNet integration, SSL
- **Tiers:** Basic (dev) to Premium (production) with clustering

---

### 5.5 Azure Service Bus

**Purpose:** Enterprise message broker

**Description:**  
Fully managed enterprise message broker with queues, topics, and reliable message delivery.

**Justification:**
- **Reliability:** At-least-once delivery, dead-letter queues
- **Features:** Topics/subscriptions, sessions, scheduled messages
- **Integration:** Native Azure SDK support across services
- **Scalability:** Handles millions of messages
- **Compliance:** Enterprise-grade security and compliance
- **Patterns:** Pub/sub, request-reply, message routing

**Use Cases:**
- Service-to-service communication
- Event distribution
- Decoupling microservices
- Integration with Azure Functions/Logic Apps

**Library:** `@azure/service-bus`

---

### 5.6 Azure Blob Storage

**Purpose:** Object storage

**Description:**  
Massively scalable object storage for unstructured data with hot, cool, and archive tiers.

**Justification:**
- **Scalability:** Exabyte-scale storage capacity
- **Cost Tiers:** Hot, cool, archive for cost optimization
- **Integration:** Native SDK, CDN integration
- **Security:** Encryption, SAS tokens, Azure AD RBAC
- **Features:** Versioning, soft delete, immutability
- **Performance:** Low latency, high throughput

**Use Cases:**
- User-uploaded images
- Generated reports/exports
- Static assets
- Backup storage

**Library:** `@azure/storage-blob`

---

### 5.7 Azure Communication Services

**Purpose:** Email and SMS delivery

**Description:**  
Cloud-based communication platform for email, SMS, voice, and video.

**Justification:**
- **Integrated:** Native Azure service, no third-party dependencies
- **Compliance:** Enterprise-grade security and compliance
- **Reliability:** High deliverability rates
- **Cost:** Competitive pricing vs SendGrid/Twilio
- **Features:** Email tracking, templates via Handlebars

**Use Cases:**
- Transactional emails
- User notifications
- System alerts
- Automated communications

**Library:** `@azure/communication-email`

---

### 5.8 Azure Key Vault

**Purpose:** Secrets management

**Description:**  
Cloud service for securely storing and accessing secrets, keys, and certificates.

**Justification:**
- **Security:** Hardware security module (HSM) backed
- **Access Control:** Azure AD RBAC, audit logging
- **Integration:** Native SDK integration across Azure services
- **Compliance:** Meets compliance requirements (SOC, ISO, HIPAA)
- **Versioning:** Secret versioning and rotation
- **Automation:** Bicep/ARM integration for IaC

**Stored Secrets:**
- Database connection strings
- API keys for third-party services
- Azure AD client secrets
- Encryption keys
- Service credentials

**Library:** `@azure/keyvault-secrets`

---

### 5.9 Azure Application Insights

**Purpose:** Application performance monitoring (APM)

**Description:**  
Application monitoring service with distributed tracing, metrics, and log analytics.

**Justification:**
- **Observability:** End-to-end request tracing across services
- **Integration:** Native Node.js SDK, auto-instrumentation
- **Analytics:** Kusto Query Language (KQL) for log analysis
- **Alerting:** Proactive alerts on anomalies
- **Cost:** Included with Azure subscription
- **Features:** Live metrics, dependency tracking, performance profiling

**Library:** `applicationinsights`

---

### 5.10 Azure Container Registry

**Purpose:** Container image registry

**Description:**  
Private Docker registry service for storing and managing container images.

**Justification:**
- **Private:** Secure, private image storage
- **Integration:** Native Azure service, RBAC integration
- **Geo-Replication:** Multi-region replication for availability
- **Security:** Vulnerability scanning, image signing
- **Performance:** Co-located with compute resources
- **Tasks:** Build automation with ACR Tasks

---

### 5.11 Azure AI Foundry (Optional)

**Purpose:** AI/ML platform (formerly Azure OpenAI)

**Description:**  
Managed service providing access to OpenAI models (GPT-4, embeddings) with enterprise security. Include only when AI capabilities are required.

**Justification:**
- **Enterprise:** Data privacy, compliance, dedicated capacity
- **Models:** GPT-4 Turbo, GPT-3.5, embeddings
- **Security:** Private endpoints, Azure AD auth, data residency
- **Performance:** Low latency, high throughput
- **Cost Control:** Token-based pricing with usage limits

**Potential Use Cases:**
- Content generation
- Intelligent assistance
- Data analysis
- Natural language processing

**Library:** `openai` SDK configured for Azure endpoints

**Note:** Only provision when AI features are part of project requirements.

---

### 5.12 Azure Front Door

**Purpose:** Global load balancer and CDN

**Description:**  
Global, scalable entry point with CDN, WAF, and SSL offloading.

**Justification:**
- **Performance:** Anycast routing, <50ms latency globally
- **Security:** Web Application Firewall (WAF), DDoS protection
- **Features:** SSL termination, URL rewriting, caching
- **Reliability:** 99.99% SLA, automatic failover
- **Routing:** Path-based routing, A/B testing support

---

### 5.13 Azure Entra ID (Azure AD)

**Purpose:** Identity and access management

**Description:**  
Cloud-based identity service providing authentication, authorization, and application management.

**Justification:**
- **Enterprise SSO:** Single sign-on for all apps
- **Security:** MFA, conditional access, identity protection
- **Integration:** Native Microsoft 365 integration
- **Standards:** OAuth 2.0, OpenID Connect
- **Administration:** Centralized user/group management
- **Compliance:** SOC 2, ISO 27001, GDPR compliant

**Features Used:**
- App registrations for MSAL authentication
- Microsoft Graph API access
- User/group synchronization
- Conditional access policies

**Library:** `@azure/msal-browser`, `@azure/msal-react`

---

## 6. DevOps & CI/CD

### 6.1 Docker

**Purpose:** Application containerization

**Description:**  
Platform for developing, shipping, and running applications in containers.

**Justification:**
- **Consistency:** Identical environments across dev/staging/prod
- **Portability:** Run anywhere Docker is supported
- **Efficiency:** Lightweight vs VMs, fast startup
- **Isolation:** Process isolation, resource limits
- **Ecosystem:** Standard for cloud-native applications

**Files:**
- `Dockerfile` per application (api, web, worker)
- Multi-stage builds for optimization
- `docker-compose.yml` for local development

---

### 6.2 Docker Compose

**Purpose:** Multi-container development environment

**Description:**  
Tool for defining and running multi-container Docker applications using YAML configuration.

**Justification:**
- **Local Development:** Matches production environment locally
- **Simplicity:** Single command to start all services
- **Configuration:** Infrastructure as code for dev environment
- **Profiles:** Conditional service startup (worker, tools, all)
- **Networking:** Automatic service discovery via container names

**Services Defined:**
- PostgreSQL database
- Redis cache
- Azurite (local Azure Storage emulator)
- Optional: Redis Commander, pgAdmin (admin UIs)

---

### 6.3 GitHub

**Purpose:** Version control and collaboration

**Description:**  
Cloud-based Git repository hosting with issue tracking, code review, and project management.

**Justification:**
- **Collaboration:** Pull requests, code review, discussions
- **Integration:** GitHub Actions, third-party integrations
- **Security:** Secret scanning, Dependabot, security advisories
- **Project Management:** Issues, projects, milestones
- **Documentation:** README, wikis, GitHub Pages
- **Industry Standard:** Most popular platform, large talent pool

---

### 6.4 GitHub Actions

**Purpose:** CI/CD automation

**Description:**  
Native CI/CD platform integrated with GitHub for automated workflows.

**Justification:**
- **Integration:** Native GitHub integration, no external service
- **Matrix Builds:** Test across multiple Node.js versions, OS
- **Caching:** Action caching for faster builds (pnpm, Turbo)
- **Secrets:** Built-in secrets management
- **Free Tier:** 2,000 minutes/month for private repos
- **Marketplace:** Extensive action library

**Typical Workflows:**
- **CI:** Lint, typecheck, test on PR
- **Build:** Build all apps via Turbo on push to main
- **Deploy:** Build Docker images, push to ACR, deploy to Azure
- **Database:** Run Prisma migrations on deployment
- **Desktop:** Build and sign desktop apps for all platforms

**Example Pipeline:**
```yaml
name: CI/CD

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v2
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'pnpm'
      - run: pnpm install
      - run: pnpm turbo lint test typecheck

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - run: pnpm turbo build
      - uses: docker/build-push-action@v5
      # ... push to ACR, deploy to Azure
```

---

### 6.5 Bicep

**Purpose:** Infrastructure as Code (IaC)

**Description:**  
Domain-specific language (DSL) for deploying Azure resources declaratively.

**Justification:**
- **Azure-Native:** First-class Azure support vs Terraform
- **Simplicity:** Cleaner syntax than ARM JSON templates
- **Type Safety:** Strong typing, IntelliSense support
- **Modularity:** Module system for reusable components
- **Idempotency:** Safe to re-run deployments
- **Validation:** What-if deployments, linting

**Structure:**
```
infra/bicep/
├── main.bicep              # Main deployment
├── main-skillsoft.bicep    # Skillsoft-specific config
├── modules/                # Reusable modules
│   ├── networking.bicep
│   ├── postgres.bicep
│   ├── redis.bicep
│   ├── keyvault.bicep
│   └── containers.bicep
└── deploy.sh              # Deployment script
```

**Deployment:**
```bash
az deployment sub create \
  --location eastus \
  --template-file main.bicep \
  --parameters @params.json
```

---

## 7. Development Tools

### 7.1 Prettier

**Version:** 3.7.4+  
**Purpose:** Code formatting

**Description:**  
Opinionated code formatter supporting JavaScript, TypeScript, JSON, Markdown, and more.

**Justification:**
- **Consistency:** Enforces uniform code style across team
- **Automation:** Format on save, pre-commit hooks
- **Configuration:** Minimal setup, smart defaults
- **Integration:** Works with all editors
- **Team Efficiency:** Eliminates style debates

---

### 7.2 ESLint

**Purpose:** JavaScript/TypeScript linting

**Description:**  
Pluggable linting utility for JavaScript and TypeScript.

**Justification:**
- **Quality:** Catch bugs and anti-patterns early
- **Consistency:** Enforce coding standards
- **TypeScript:** Full TypeScript support via plugins
- **Extensible:** Plugin ecosystem for frameworks (React, Next.js)
- **Auto-fix:** Many issues auto-fixable

**Configs Used:**
- `eslint-config-next`: Next.js specific rules

---

### 7.3 Vitest

**Version:** 2.0.0+  
**Purpose:** Unit testing framework

**Description:**  
Fast unit test framework powered by Vite with Jest-compatible API.

**Justification:**
- **Speed:** Faster than Jest, uses Vite's transform pipeline
- **Compatibility:** Jest-compatible API, easy migration
- **TypeScript:** Native TypeScript support
- **ESM:** First-class ESM support
- **Watch Mode:** Fast re-runs on file changes

---

### 7.4 tsx

**Version:** 4.21.0+  
**Purpose:** TypeScript execution

**Description:**  
TypeScript execution environment for Node.js with fast compilation.

**Justification:**
- **Development:** Run .ts files directly without compilation
- **Watch Mode:** Auto-restart on file changes
- **Speed:** Faster than ts-node
- **ESM Support:** Modern ESM module support

**Usage:** `tsx watch src/index.ts` for development

---

## 8. Security & Authentication

### 8.1 MSAL (Microsoft Authentication Library)

**Versions:** @azure/msal-browser 4.27.0, @azure/msal-react 3.0.23  
**Purpose:** Microsoft identity authentication

**Description:**  
Official Microsoft library for authenticating users via Azure AD/Entra ID using OAuth 2.0 and OpenID Connect.

**Justification:**
- **Official:** Microsoft-maintained library
- **Features:** SSO, MFA, conditional access support
- **Token Management:** Automatic token refresh, caching
- **Graph Access:** Acquire tokens for Microsoft Graph API
- **Security:** PKCE flow, token validation
- **React Integration:** Hooks, context providers

**Flow:**
1. User signs in via Azure AD
2. Acquire access token
3. Call Microsoft Graph API
4. Call backend API with bearer token

---

### 8.2 Helmet

**Version:** 7.1.0+  
**Purpose:** HTTP security headers

**Description:**  
Express middleware that sets various HTTP headers to secure applications.

**Justification:**
- **Security:** Protects against common vulnerabilities
- **Headers Set:**
  - Content Security Policy (CSP)
  - X-Content-Type-Options
  - X-Frame-Options
  - Strict-Transport-Security
- **Best Practice:** Industry standard for Express apps

---

### 8.3 express-rate-limit

**Version:** 7.1.0+  
**Purpose:** API rate limiting

**Description:**  
Rate limiting middleware for Express to prevent abuse.

**Justification:**
- **Protection:** Prevent brute force, DoS attacks
- **Flexible:** Per-endpoint, per-user rate limits
- **Storage:** Redis-backed for distributed rate limiting
- **Responses:** Return 429 status with retry headers

---

### 8.4 jsonwebtoken

**Version:** 9.0.0+  
**Purpose:** JWT token generation/verification

**Description:**  
Implementation of JSON Web Tokens for secure information exchange.

**Justification:**
- **Stateless:** No server-side session storage needed
- **Secure:** Cryptographically signed tokens
- **Standard:** Industry standard (RFC 7519)
- **Flexible:** Custom claims, expiration, validation

---

## 9. Monitoring & Observability

### 9.1 Application Insights SDK

**Version:** 3.12.1+  
**Purpose:** Application telemetry

**Description:**  
Node.js SDK for Azure Application Insights providing automatic instrumentation.

**Justification:**
- **Auto-Instrumentation:** Automatic HTTP, database, Redis tracking
- **Distributed Tracing:** Correlation across services
- **Custom Events:** Track business metrics
- **Performance:** Low overhead monitoring
- **Integration:** Works with Winston, Pino logs

**Setup:**
```typescript
import appInsights from 'applicationinsights';

appInsights.setup(process.env.APPLICATIONINSIGHTS_CONNECTION_STRING)
  .setAutoCollectRequests(true)
  .setAutoCollectPerformance(true)
  .setAutoCollectExceptions(true)
  .setAutoCollectDependencies(true)
  .start();
```

---

### 9.2 Pino Pretty

**Version:** 10.3.0+  
**Purpose:** Development log formatting

**Description:**  
Pretty printer for Pino logs during development.

**Justification:**
- **Readability:** Human-readable logs in dev
- **Production:** Disabled in production for performance
- **Customization:** Configurable formatting
- **Performance:** No impact when disabled

---

## 10. Integration & Messaging

### 10.1 WebSockets (ws)

**Version:** 8.18.0+  
**Purpose:** Real-time bidirectional communication

**Description:**  
WebSocket client and server implementation for Node.js.

**Justification:**
- **Real-Time:** Low-latency bidirectional communication
- **Performance:** Efficient binary/text messaging
- **Standard:** WebSocket protocol (RFC 6455)
- **Simple:** Lightweight, easy to use
- **Compatibility:** Works with modern browsers

**Use Cases:**
- Real-time notifications
- Live status updates
- Progress tracking
- Chat/collaboration features
- Push notifications to desktop apps

---

### 10.2 Handlebars

**Version:** 4.7.0+  
**Purpose:** Email template rendering

**Description:**  
Simple templating language for generating HTML emails.

**Justification:**
- **Simplicity:** Easy-to-learn syntax
- **Security:** Auto-escaping prevents XSS
- **Reusability:** Partials, helpers for DRY templates
- **Logic-less:** Separation of logic and presentation
- **Industry Standard:** Popular email template engine

**Use Cases:**
- Email templates
- Notification emails
- Report generation
- Document generation

---

## 11. Additional Libraries

### 11.1 Sharp

**Version:** 0.34.0+  
**Purpose:** Image processing

**Description:**  
High-performance Node.js image processing library using libvips.

**Justification:**
- **Performance:** 4-5x faster than ImageMagick
- **Features:** Resize, crop, rotate, format conversion
- **Memory:** Low memory usage
- **Formats:** JPEG, PNG, WebP, AVIF, GIF, SVG

---

### 11.2 date-fns

**Version:** 4.1.0+  
**Purpose:** Date manipulation

**Description:**  
Modern JavaScript date utility library.

**Justification:**
- **Immutable:** Pure functions, no mutations
- **Tree-Shakeable:** Import only what you need
- **TypeScript:** Full type definitions
- **i18n:** Internationalization support

---

### 11.3 nanoid

**Version:** 5.1.6+  
**Purpose:** Unique ID generation

**Description:**  
Tiny, secure, URL-friendly unique string ID generator.

**Justification:**
- **Security:** Cryptographically strong random
- **Size:** 130 bytes, no dependencies
- **Collision-Safe:** 1% probability only after ~36M IDs
- **URL-Safe:** Safe for URLs, filenames

---

### 11.4 Framer Motion

**Version:** 12.23.26+  
**Purpose:** Animation library

**Description:**  
Production-ready animation library for React.

**Justification:**
- **Declarative:** Simple, declarative API
- **Performance:** GPU-accelerated animations
- **Gestures:** Drag, hover, tap interactions
- **Layout Animations:** Automatic layout transitions
- **Spring Physics:** Natural-feeling animations

---

### 11.5 Recharts

**Version:** 2.15.4  
**Purpose:** Data visualization

**Description:**  
Composable charting library built on React components.

**Justification:**
- **React-Native:** Built for React
- **Composable:** Build custom charts from components
- **Responsive:** Automatic responsive sizing
- **Customizable:** Full control over styling
- **Types:** TypeScript support

---

## Technology Selection Principles

### 1. **Type Safety First**
- TypeScript across entire stack
- Runtime validation with Zod
- Prisma for type-safe database access

### 2. **Developer Experience**
- Fast feedback loops (Vite, tsx, Turbo)
- Minimal configuration
- Comprehensive tooling (Prettier, ESLint, TypeScript)

### 3. **Performance**
- Optimized bundling (Next.js standalone, tsup)
- Caching strategies (Turbo, Redis, CDN)
- Efficient runtimes (Node 20, Tauri vs Electron)

### 4. **Cloud-Native**
- Containerization (Docker)
- Infrastructure as Code (Bicep)
- Managed services (Azure PaaS)

### 5. **Enterprise-Ready**
- Security (MSAL, Helmet, rate limiting)
- Monitoring (Application Insights)
- Compliance (Azure certifications)
- Scalability (auto-scaling, load balancing)

### 6. **Cost Optimization**
- Serverless where appropriate (Container Apps)
- Right-sized SKUs (burstable PostgreSQL for dev)
- Caching to reduce compute (Redis)
- Storage tiers (hot/cool/archive)

### 7. **Maintainability**
- Monorepo for code sharing
- Shared packages (@uplift/shared, @uplift/database)
- Consistent patterns across services
- Comprehensive documentation

---

## Cost Estimate (Monthly)

### Development Environment
- **GitHub:** Free (public repos) or $4/user (private)
- **Azure Dev Resources:** ~$100-200
  - PostgreSQL (Burstable B1ms): $15
  - Redis (Basic C0): $16
  - Container Apps: ~$50
  - Storage: $5
  - Service Bus: $10

### Production Environment (Small)
- **Azure Resources:** ~$500-800/month
  - PostgreSQL (General Purpose D2s_v3): $180
  - Redis (Standard C1): $76
  - Container Apps: ~$150
  - Storage + CDN: $50
  - Application Insights: $30
  - Service Bus (Standard): $10

### Scaling
- Costs scale linearly with usage
- Auto-scaling prevents over-provisioning
- Optimize using reserved instances (30-70% savings)

---

## Conclusion

This technology stack provides:

✅ **Enterprise-Grade:** Security, compliance, monitoring  
✅ **Developer-Friendly:** TypeScript, modern tooling, great DX  
✅ **Scalable:** Cloud-native, auto-scaling, globally distributed  
✅ **Cost-Effective:** Serverless, right-sized resources, caching  
✅ **Maintainable:** Monorepo, shared packages, IaC  
✅ **Proven:** Battle-tested in production

**Recommendation:** Use this stack as the foundation for all new internal enterprise applications. The architecture, tooling, and patterns are broadly applicable across various use cases.

**Project-Specific Considerations:**
- Select only the components needed for your specific project
- Desktop applications (Tauri) are optional
- AI capabilities (Azure AI Foundry) only when required
- Add project-specific integrations and business logic as separate packages
- Adapt database schema to domain requirements

---

**Document Version:** 1.0  
**Last Updated:** January 8, 2026  
**Maintained By:** IT Engineering Team
