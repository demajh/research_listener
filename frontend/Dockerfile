# Use an official Node.js runtime as a parent image
FROM node:16-alpine

# Set working directory
WORKDIR /app

# Copy package.json and install dependencies
COPY package.json .
RUN npm install

# Copy entire frontend
COPY . /app

# Build app
RUN npm run build

# Expose port (React dev server or final build via a static server)
EXPOSE 3000

# Start the app in dev mode (change to a static server if deploying production build)
CMD ["npm", "start"]
