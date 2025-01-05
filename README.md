# Data Flow Engine

## Requisitos

### Para ejecutar el proyecto:

* docker

### Para desarrollar:

* python 3.12
* [uv](https://docs.astral.sh/uv/)
* zip

## Instrucciones

En el directorio del proyecto:

### Iniciar Airflow

1. `docker-compose -f airflow/docker-compose.yaml up -d`

### Configurar Airflow

1. Admin
2. Connections -> New Connection

- Connection Id: spark
- Host: spark://spark
- Port: 7077
- Extra: `{"deploy-mode": "client"}`

### Cargar las dependencias de Spark

* Ejecutar el dag `spark_package_upload`

### Ejecutar el Data Flow Engine:

* Actualizar [este archivo](airflow/data/metadata.json) con la metadata soportada por el proyecto
* Actualizar [este archivo](airflow/data/input/events/person/input-data.json) con el dato a procesar
* Ejecutar el DAG `data_flow_engine` en Airflow.

## Lanzar los tests

En el directorio del proyecto:

1. `cd engine`
2. `uv run pytest unit/tests`

## Cargar una nueva revisión del Data Flow Engine:

En el directorio del proyecto:

1. `cd engine`
2. Modificar la versión en el archivo [pyproject.toml](engine/pyproject.toml)
3. `. scripts/build_package.sh`
4. Ejecutar el dag `spark_package_upload`

## Servicios

* Airflow: `http://localhost:8080/`
* Spark: `http://localhost:8070/`
* Kafka: `http://localhost:8090/topics`
* Hadoop: `http://localhost:9870/`


## Troubleshooting

### Error al conectar con hadoop o kafka

Es posible que la primera ejecución Docker tarde más de 60 segundos en descargar y construir las imágenes.
Se puede resolver levantando los contenedores manualmente una vez con cualquiera de estos comandos:

`docker-compose -f hadoop/docker-compose.yaml`
`docker-compose -f engine/docker-compose.yaml`
`docker-compose -f kafka/docker-compose.yaml`

También se puede aumentar el tiempo de sleep en el comando que ejecuta Airflow en el propio DAG, en las líneas
41, 45 y 54 de [este archivo](airflow/dags/data_flow_engine.py)

### Problemas de memoria en Docker

Es posible que todos los servicios al mismo tiempo consuman más memoria de la permitida y los contenedores se
interrumpan por un OOM.
Para resolver esto, en el dashboard de Docker:
`Ajustes -> Resources -> Advanced` e incrementar el valor de Memory limit.

### Arquitectura

He desarrollado el proyecto con un Macbook Pro M3 (arquitectura arm) con lo que para poder ejecutar el proyecto en
arquitectura amd64 hay que actualizar la [línea 19 de este archivo](airflow/Dockerfile) y
reemplazar `ENV JAVA_HOME /usr/lib/jvm/java-17-openjdk-arm64/` por
`ENV JAVA_HOME /usr/lib/jvm/java-17-openjdk-amd64/`

