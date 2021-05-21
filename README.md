# netdata-ml-app
Netdata ML App

## Docker

Docker run command:

```
docker run -d --name=netdata-mlapp \
  -p 29999:29999 \
  --env NETDATAMLAPP_HOSTS=newyork.my-netdata.io \ 
  --env NETDATAMLAPP_SCRAPE_CHILDREN=yes \ 
  --restart unless-stopped \
  andrewm4894/netdata-mlapp
```
