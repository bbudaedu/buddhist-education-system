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
  ttf-freefont

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

# Create non-root user for security
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nodejs -u 1001

# Change ownership of the app directory
RUN chown -R nodejs:nodejs /app
USER nodejs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/health', (res) => { process.exit(res.statusCode === 200 ? 0 : 1) })"

# Start the application
CMD ["npm", "start"]