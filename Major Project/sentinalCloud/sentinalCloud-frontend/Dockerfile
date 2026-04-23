# ---- STAGE 1: Build the React Application ----
# Use a Node.js image to build the project's static files
FROM node:20-alpine AS builder

# Set the working directory
WORKDIR /app

# Copy package files and install dependencies
# This leverages Docker's cache. It only re-installs if dependencies change.
COPY package*.json ./
RUN npm install

# Copy the rest of the source code
COPY . .

# Run the production build script from package.json
# This creates an optimized 'dist' folder with static assets
RUN npm run build


# ---- STAGE 2: Serve the Static Files with Nginx ----
# Use a tiny, official Nginx image. It's highly performant and secure.
FROM nginx:stable-alpine

# Copy the custom Nginx configuration file
# We will create this file next. It's crucial for React Router to work.
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy the built static assets from the 'builder' stage
# This is the key step: we only take the final 'dist' folder.
# The final image won't contain Node.js or your source code.
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port 80, which is the default port Nginx listens on
EXPOSE 80

# The command to start the Nginx server in the foreground
CMD ["nginx", "-g", "daemon off;"]