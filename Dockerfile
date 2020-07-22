# https://hub.docker.com
# To Find an images to inherit docker from
# Then add other specifics you need

# the name of the image is python:3.12-alpine
FROM python:3.8-alpine

# Who is maintaining the project
LABEL maintainer="ThreeTree"

#### environment variable

# set the environment variable 
# to tell python to run in an unbuffered mode
# which is needed when running a docker image
ENV PYTHONUNBUFFERED 1

# create a requirements file to put all our dependences
# copy /requirements.txt from the current directory 
# to the docker image /requirements.txt 
COPY ./requirements.txt /requirements.txt

# then run pip on the docker image /requirements.txt
RUN pip install -r /requirements.txt

##### make a directory in the docker image 
##### to store our application source code

# create an ampty folder on the docker image
RUN mkdir /app
# switch to this directory as the default working directory
# hence any application we run must start from this default location
WORKDIR /app
# copies from our local machine the app folder into our docker image
COPY ./app /app

#### create an admin user that will run our docker image

# -D means create a user that will be used for running applications only
RUN adduser -D user
#switch to that user that we have just created
USER user
