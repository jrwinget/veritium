FROM node:18-alpine

WORKDIR /app

# Create non-root user/group with fixed IDs for better volume compatibility
RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001 -G nodejs

# Copy package files with correct ownership and install deps
COPY --chown=nextjs:nodejs package*.json ./
RUN npm ci

# Copy rest of app
COPY . .

# Fix ownership recursively so nextjs can write anywhere under /app (including creating timestamp files)
RUN chown -R nextjs:nodejs /app

# Drop privileges
USER nextjs

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]
