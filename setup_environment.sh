#! bin/bash

# before running, verify IP using ifconfig(install net-tools if needed)
# HOST_IP=$(ip -o route get to 8.8.8.8 | sed -n 's/.*src \([0-9.]\+\).*/\1/p')
# export HOST_IP_ADDRESS=$HOST_IP
# echo "$HOST_IP_ADDRESS"
# install hadoop
# steps to install Git and download project
bash hadoop_cluster/0_create_kafka_cluster.sh
bash hadoop_cluster/1_create_hadoop_spark_image.sh
bash hadoop_cluster/2_create_hadoop_spark_cluster.sh start
 
