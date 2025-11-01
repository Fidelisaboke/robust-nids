# Stage 1: Builder
FROM node:22-alpine AS builder

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install project dependencies
RUN npm ci

# Copy app source code
COPY . .

# Set the API URL environment variable for production build
ARG NEXT_PUBLIC_API_BASE_URL
ENV NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL}

# Build Next.js app
RUN npm run build

# Stage 2: Production
FROM node:22-alpine AS production

# Set the working directory
WORKDIR /app

# Create a non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Copy only the necessary files from the builder stage
COPY --from=builder /app/package*.json ./
RUN npm ci --omit=dev
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.ts ./

# Give appuser ownership of the working directory
RUN chown -R appuser:appgroup /app

# Switch to the non-root user
USER appuser

# Expose the port the app runs on
EXPOSE 3000

# Start the Next.js app
CMD ["npm", "start"]
