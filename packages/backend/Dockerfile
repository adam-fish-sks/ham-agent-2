# Backend Dockerfile - Multi-stage build
FROM node:20-alpine AS base

# Install pnpm
RUN npm install -g pnpm

WORKDIR /app

# Copy workspace files
COPY package.json pnpm-workspace.yaml ./
COPY turbo.json ./

# Copy package files
COPY packages/backend/package.json ./packages/backend/
COPY packages/shared/package.json ./packages/shared/
COPY packages/database/package.json ./packages/database/

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy source files
COPY packages/backend ./packages/backend
COPY packages/shared ./packages/shared
COPY packages/database ./packages/database

# Build
FROM base AS builder
WORKDIR /app
RUN pnpm turbo run build --filter=@ham-agent/backend

# Production image
FROM node:20-alpine AS runner
WORKDIR /app

# Copy built files
COPY --from=builder /app/packages/backend/dist ./dist
COPY --from=builder /app/packages/backend/package.json ./
COPY --from=builder /app/node_modules ./node_modules

# Set environment
ENV NODE_ENV=production
ENV PORT=3001

EXPOSE 3001

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3001/health', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"

CMD ["node", "dist/index.js"]
