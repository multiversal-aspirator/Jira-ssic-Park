# ─────────────────────────────────────────────
# Stage 1: Build the React app with Vite
# ─────────────────────────────────────────────
FROM node:20-alpine AS build

WORKDIR /app

# Copy package files first for better Docker layer caching
COPY package.json package-lock.json ./

# Use 'npm ci' for clean, reproducible installs from package-lock.json
# --legacy-peer-deps allows install despite vite/plugin-react peer dependency mismatch
RUN npm ci --legacy-peer-deps

# Copy the rest of the source code
COPY . .

# Allow backend URL to be injected at build time
# Example: docker build --build-arg VITE_API_URL=https://api.example.com .
ARG VITE_API_URL=/api
ENV VITE_API_URL=$VITE_API_URL

# Build production assets into /app/dist
RUN npm run build


# ─────────────────────────────────────────────
# Stage 2: Serve static files with Nginx
# ─────────────────────────────────────────────
FROM nginx:1.27-alpine

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy our custom nginx config (handles SPA routing + /api proxy)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy the built React app from the build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Set proper permissions
RUN chown -R nginx:nginx /usr/share/nginx/html \
    && chmod -R 755 /usr/share/nginx/html

EXPOSE 80

# Healthcheck to verify the container is serving content
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
