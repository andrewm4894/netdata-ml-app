![logo](assets/logo.svg)  
`Experimental Machine Learning Application`

# netdata-ml-app
__Netdata ML App__ - A collection of [dash](https://plotly.com/dash/) based python apps that will take in a netdata host ip and some input parameters, pull the data from the host, crunch it, and display some results. 

This is all experimental and nowhere near stable yet, but you might find something interesting in your data so why not play around and see :) 

Click below to play with the latest version of the app, deployed to Heroku and configured to use data from our demo servers:

https://netdata-ml-app.herokuapp.com/

https://netdata-ml-app-develop.herokuapp.com/

### Apps

Each app focuses on a particular use case: 

- __Metrics Explorer__: You give it a list of metrics you are interested in, and it will plot them together in various ways.
- __Changepoint Detection__: Look over a subset of charts to find which metrics have obvious ['changepoints'](https://en.wikipedia.org/wiki/Change_detection) within a window of interest.
- __Clustered Heatmap__: A heatmap of your metrics from netdata, overed by a clustering algorithm to group similar 'looking' metrics together.
- __Metric Percentiles__: Overlay percentiles on your plots based on a window of interest and a reference window. Results will be ordered by those with the higher 'crossover' percentage.
- __Alarms Affinity__: Perform some [market basket analysis](https://en.wikipedia.org/wiki/Affinity_analysis) on your alarms to see which ones "co-occur" together.
- __Time Series Clustering__: User clustering to 'group' similar 'looking' metrics together.
- __Correlations__: Some correlation plots and exploration of recent correlation changes between metrics.
- __Anomalies__: Given a reference window to train on, build some anomaly detection models to find any hotspots for anomalies within a window of interest.
- __Matrix Profile Anomalies__: Use a [matrix profile](https://matrixprofile.org/#:~:text=The%20matrix%20profile%20is%20a,scalable%20and%20largely%20parameter%2Dfree.) driven approach to detect which metrics might be most anomalous.
- __Metric Model__: Given a metric of interest, build a predictive model of that metric - how good is that model and what other metrics are important to it? This could be another way to find some evidence of what other metrics might be 'driving' some metric you are interested in.
- __Metric Similarity__: Given a metric of interest, find the other most similar 'looking' metrics.

## Using Docker

Docker pull command:
```bash
docker image pull andrewm4894/netdata-ml-app:latest
```

Docker run command:

```bash
docker run -d --network="host" --name=netdata-ml-app \
  -p 29999:29999 \
  --env NETDATAMLAPP_HOSTS=127.0.0.1:19999 \
  --restart unless-stopped \
  andrewm4894/netdata-ml-app:latest
```

Stop all running containers: 
```
docker stop $(docker ps -a -q)
```

Delete all stopped containers: 
```
docker rm $(docker ps -a -q)
```


To get logs:

```bash
docker logs netdata-ml-app
```

## Running locally

```bash
# clone the repo
git clone https://github.com/andrewm4894/netdata-ml-app.git
# cd into folder
cd netdata-ml-app
# create a virtual env using something like pipenv
pipenv install
# activate the virtual env
pipenv shell
# launch the app
python index.py
```

The app should now be running on port 29999. 

## Configuration

### Environment Variables

Main way to define various config options is via environment variables you can define locally or pass into the docker container when running it. 

- `NETDATAMLAPP_HOSTS`: A string list of hosts you would like the app to pull data from. Default is a local netdata `127.0.0.1:19999`. But for example if you wanted to tell the ml app to look at our two demo netdata hosts you could do `london.my-netdata.io,newyork.my-netdata.io`.
- `NETDATAMLAPP_SCRAPE_CHILDREN`: `yes` to also include any child netdata in the hosts list for the app, default is `no`.
- `NETDATAMLAPP_LOG_LEVEL`: Default is `info`, set to `debug` for debug level.