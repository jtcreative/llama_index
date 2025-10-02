# Use Node image
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source code and build
COPY . .
RUN npm run build

# Expose port Vite preview defaults to (4173)
EXPOSE 3978

# Start production preview server
CMD ["npm", "start"]