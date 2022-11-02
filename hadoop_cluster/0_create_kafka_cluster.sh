docker network create --subnet=172.20.0.0/16 datamakingnet # create custom network

1. Create ZooKeeper Container

docker pull zookeeper:3.4

docker run -d --hostname zookeepernode --net datamakingnet --ip 172.20.1.3 --name datamaking_zookeeper --publish 2181:2181 zookeeper:3.4


2. Create Kafka Container

docker pull ches/kafka

docker run -d --hostname kafkanode --net datamakingnet --ip 172.20.1.4 --name datamaking_kafka --publish 9092:9092 --publish 7203:7203 --env KAFKA_ADVERTISED_HOST_NAME=172.16.30.89 --env ZOOKEEPER_IP=172.16.30.89 ches/kafka
