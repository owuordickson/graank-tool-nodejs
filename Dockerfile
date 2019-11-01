FROM nikolaik/python-nodejs:python3.6-nodejs13-alpine

RUN mkdir /py_dependencies
WORKDIR /py_dependencies
COPY python_requirements.txt /py_dependencies/requirements.txt
RUN pip install -r requirements.txt

RUN mkdir /opt/app
WORKDIR /opt/app
COPY app /opt/app
RUN npm install

ENV PORT 80
EXPOSE 80

CMD ["node", "./bin/www"]