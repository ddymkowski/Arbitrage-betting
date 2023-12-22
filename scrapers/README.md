# scraping-service

Service responsible for web scraping bookmaker sites and publishing serialized data into a message queue.

## Getting started
```
cp .env.template .env
docker-compose up
```
## Running jobs
Betclic
```
curl -X 'POST' 'http://0.0.0.0:8000/betlic' 
```
LVBet
```
curl -X 'POST' 'http://0.0.0.0:8000/lvbet' 
```

