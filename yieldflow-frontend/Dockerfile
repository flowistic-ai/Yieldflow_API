# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

ARG REACT_APP_API_URL=http://localhost:8000
ENV REACT_APP_API_URL=$REACT_APP_API_URL

RUN npm run build

# Production stage
FROM node:18-alpine

WORKDIR /app

# Install serve to run the React app
RUN npm install -g serve

COPY --from=builder /app/build ./build

EXPOSE 3000

ENV NODE_ENV=production
ENV REACT_APP_API_URL=http://localhost:8000

CMD ["serve", "-s", "build", "-l", "3000"]
