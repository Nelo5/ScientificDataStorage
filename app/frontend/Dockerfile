# Use an official Node.js image as a base image
FROM node:18-alpine

# Set working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./



# Install dependencies
RUN npm install
RUN npm install react-scripts --save-dev

# Copy the rest of the app's code
COPY public/ public/
COPY src/ src/

# Expose the port on which the app will run
EXPOSE 3000

# Command to start the app
CMD ["npm", "start"]
