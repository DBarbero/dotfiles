FROM nginx:1.9

# Install Apache 2 Utils
RUN apt-get update
RUN apt-get install apache2-utils -y

COPY dist  /usr/share/nginx/html/
