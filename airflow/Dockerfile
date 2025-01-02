FROM apache/airflow:2.10.4-python3.12

ADD requirements.txt .
USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    gcc \
    heimdal-dev \
    procps \
    openjdk-17-jdk \
    ant \
    docker.io \
    docker-compose \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME
ENV JAVA_HOME /usr/lib/jvm/java-17-openjdk-arm64/
RUN export JAVA_HOME

USER airflow
RUN pip install -r requirements.txt
