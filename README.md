# netdata-ml-app
Netdata ML App

## Docker

Docker pull command:
```
docker image pull andrewm4894/netdata-mlapp 
```

Docker run command:

```
docker run -d --network="host" --name=netdata-mlapp \
  -p 29999:29999 \
  --env NETDATAMLAPP_HOSTS=127.0.0.1:19999 \
  --restart unless-stopped \
  andrewm4894/netdata-mlapp
```

To get logs:

```
docker logs netdata-mlapp
```

