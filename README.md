Instrucciones:
## Servicios
1. `docker-compose -f airflow/docker-compose.yaml up -d`
2. `docker-compose -f kafka/docker-compose.yaml up -d`

## Configurar kafka
1. `docker exec redpanda -it bash`
2. `rpk topic create person`

## Configurar Airflow
1. Admin
2. Connections -> New Connection
- Connection Id: spark
- Host: spark://spark
- Port: 7077
- Extra: `{"deploy-mode": "client"}`
