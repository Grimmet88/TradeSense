FROM node:20-bullseye

# Set workdir
WORKDIR /workspaces/TradeSense

# Install dependencies early (cache-friendly)
COPY package*.json ./
RUN npm ci

# Copy source
COPY . .

# Default command for Codespaces (you can override in VS Code)
CMD ["npm", "run", "dev"]
