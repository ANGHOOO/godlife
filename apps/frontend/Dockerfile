FROM node:22-alpine AS base

ENV NEXT_TELEMETRY_DISABLED=1

WORKDIR /app

RUN corepack enable

COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

FROM base AS dev
COPY . ./
EXPOSE 3000
CMD ["pnpm", "dev", "--hostname", "0.0.0.0", "--port", "3000"]

FROM base AS builder
COPY . ./
RUN pnpm build

FROM node:22-alpine AS runner

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1

WORKDIR /app

RUN corepack enable

COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/pnpm-lock.yaml ./pnpm-lock.yaml
COPY --from=builder /app/next.config.ts ./next.config.ts
COPY --from=builder /app/tsconfig.json ./tsconfig.json
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules

EXPOSE 3000

CMD ["pnpm", "start", "--hostname", "0.0.0.0", "--port", "3000"]
