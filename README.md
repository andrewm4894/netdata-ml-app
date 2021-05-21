# netdata-ml-app
Netdata ML App

## Docker

Docker build:
```
docker build -t andrewm4894/netdata-mlapp:latest .
```

Docker push:
```
docker push andrewm4894/netdata-mlapp:latest
```

Docker run command:

```
docker run -d --name=netdata-mlapp \
  -p 29999:29999 \
  --env NETDATAMLAPP_HOSTS=newyork.my-netdata.io \ 
  --env NETDATAMLAPP_SCRAPE_CHILDREN=yes \ 
  --restart unless-stopped \
  andrewm4894/netdata-mlapp
```

To run via docker-compose:

```
docker-compose up
```

To run and force rebuild:

```
docker-compose up --build
```
