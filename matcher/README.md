# matching-service

Service responsible for matching the matches data from different bookmakers.

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

