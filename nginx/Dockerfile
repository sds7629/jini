FROM nginx:latest

USER root

RUN rm /etc/nginx/conf.d/default.conf

COPY default.conf /etc/nginx/conf.d

COPY ./jini-build /usr/share/nginx/html

CMD ["nginx", "-g", "daemon off;"]