FROM node:12

RUN mkdir /py_dependencies
WORKDIR /py_dependencies
COPY python_requirements.txt /py_dependencies/requirements.txt
RUN apt-get update
RUN apt-get install -y python3-pip python3
RUN pip3 install -r requirements.txt

RUN mkdir /opt/app
WORKDIR /opt/app
COPY app /opt/app
RUN npm install

ENV PORT 80
EXPOSE 80

CMD ["node", "./bin/www"]