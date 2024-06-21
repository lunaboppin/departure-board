# Use Node.js base image
FROM node:latest
FROM ghcr.io/puppeteer/puppeteer:latest

# Install necessary dependencies
#RUN apt-get update \
#    && apt-get install -y libnss3 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxcomposite1 \
#    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Expose port 3000
EXPOSE 3042

# Run the application
CMD ["node", "init.js"]
