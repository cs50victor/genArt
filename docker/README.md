
https://github.com/AaronJackson/vrn-docker/


sudo docker pull asjackson/vrn:latest

**add image to data folder**
docker run -v $PWD/data:/data:Z asjackson/vrn /runner/run.sh /data/turing.jpg