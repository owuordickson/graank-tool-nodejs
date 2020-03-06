# graank-tool-nodejs

Graank tool is a gradual pattern mining Web application implemented in Node.js. It allows users to:

* Extract gradual patterns, fuzzy-temporal gradual patterns and emerging gradual patterns from numeric data sets (csv format)

* Cross different time-series data sets (in csv format)

## Installation

Download/clone into a local package. There are two options for installing this application (through a command line program with the local package):

1. (**\*\*RECOMMENDED\*\***) Install **Docker**, build the image from the ```Dockerfile``` and create a container to run the image:

``` shell
cd graank-tool-nodejs-master && docker image build -t graank:nodejs

docker run -d graank:nodejs

```

### or

``` shell
docker pull owuordickson/graank:nodejs-tool

docker run -d -p 80:80 owuordickson/graank:nodejs-tool

```

2. Install **Nodejs** & **npm**, **Python3** & **Pip3**, then run the application:

``` shell

cd app && npm install

sudo apt-get install -y python3-pip python3

sudo pip3 install scikit-fuzzy python-dateutil

npm start

```

## Usage

Launch your Browser and go to: <http://localhost:80> or <http://localhost:80/x>
