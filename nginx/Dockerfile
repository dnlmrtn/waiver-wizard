# Stage 1: Build react app
FROM node:20 as react_build


WORKDIR /code

# Copy package.json and package-lock.json
COPY ./frontend/package.json /code/

# Install Dependencies
RUN npm install

# Copy application code
COPY ./frontend/ ./

# Setup environment variables (optional)
#ARG REACT_APP_API_ENDPOINT
#ENV REACT_APP_API_ENDPOINT $REACT_APP_API_ENDPOINT

# Build app using npm
RUN npm run build

# Stage 2: Serve built app using Nginx
FROM nginx:1.18.0-alpine
# Setup nginx configuration
RUN rm /etc/nginx/conf.d/default.conf
COPY /nginx.conf /etc/nginx/conf.d

# Setup SSL Certificates here
# COPY nginx/ssl/*.crt /etc/ssl/*.crt
# COPY nginx/ssl/*.key /etc/ssl/*.key


# Copy built React app from the previous stage
COPY --from=react_build /code/build /usr/share/nginx/html
COPY ./nginx/nginx.conf /etc/nginx/conf.d/default.conf