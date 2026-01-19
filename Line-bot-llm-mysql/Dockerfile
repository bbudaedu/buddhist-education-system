# Use Node.js 18 LTS as base image
FROM node:18-alpine

# Install Python 3, pip, and required packages for Selenium
RUN apk add --no-cache \
  python3 \
  py3-pip \
  chromium \
  chromium-chromedriver \
  freetype \
  harfbuzz \
  ca-certificates \
  ttf-freefont \
  docker-cli \
  docker-cli-compose \
  bash

# Install Python dependencies
RUN pip3 install --no-cache-dir --break-system-packages \
  selenium \
  google-genai \
  pypdf \
  python-docx \
  openpyxl \
  requests \
  urllib3 \
  webdriver-manager

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (include devDependencies for build)
RUN npm ci

# Copy source code
COPY . .

# Build TypeScript
RUN npm run build

# Remove devDependencies to keep image small
RUN npm prune --production

# Create non-root user for security (but allow root for now to fix permission issues with binds)
# RUN addgroup -g 1001 -S nodejs
# RUN adduser -S nodejs -u 1001
# RUN chown -R nodejs:nodejs /app
# USER nodejs

# Create symlink for docker-compose compatibility
# When docker compose runs in /app, it looks for ../ebook which resolves to /ebook
# Since we mount ./ebook to /app/ebook, we need /ebook -> /app/ebook
RUN ln -s /app/ebook /ebook

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/health', (res) => { process.exit(res.statusCode === 200 ? 0 : 1) })"

# Start the application
CMD ["npm", "start"]