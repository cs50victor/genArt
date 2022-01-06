
https://github.com/AaronJackson/vrn-docker/
https://github.com/aiff22/DPED
https://towardsdatascience.com/make-your-pictures-beautiful-with-a-touch-of-machine-learning-magic-31672daa3032

**https://colab.research.google.com/drive/1mLBs9mpjdRLCq8jGCG7ZgXbiNodZ3ytk?usp=sharing**

sudo docker pull asjackson/vrn:latest

**add image to data folder**
docker run -v $PWD/data:/data:Z asjackson/vrn /runner/run.sh /data/turing.jpg