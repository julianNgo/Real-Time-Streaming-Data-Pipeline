echo "create custom network"
docker network create --subnet=172.20.0.0/16 datamakingnet

echo "2. start ZooKeeper container"

docker container start datamaking_zookeeper

echo "2. start Kafka container"

docker container start datamaking_kafka
echo "3. start hadoop cluster container"
docker container start masternode
docker container start postgresqlnode
# bash hadoop_cluster/2_create_hadoop_spark_cluster.sh start