# ─────────────────────────────────────────────
# Stage 1: Build the React app with Vite
# ─────────────────────────────────────────────
FROM node:20-alpine AS build

WORKDIR /app

# Copy package files for better caching
COPY package.json package-lock.json ./

# Install dependencies with npm ci for reproducible builds
RUN npm ci

# Copy source code
COPY . .

# Build argument for API URL
ARG VITE_API_URL=/api
ENV VITE_API_URL=$VITE_API_URL

# Build React app with Vite
RUN npm run build


# ─────────────────────────────────────────────
# Stage 2: Serve with Nginx
# ─────────────────────────────────────────────
FROM nginx:1.27-alpine

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built React app from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Set proper permissions
RUN chown -R nginx:nginx /usr/share/nginx/html \
    && chmod -R 755 /usr/share/nginx/html

EXPOSE 80

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
