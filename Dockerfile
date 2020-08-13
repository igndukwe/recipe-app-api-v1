FROM python:3.8-alpine
LABEL maintainer="ThreeTree"

ENV PYTHONUNBUFFERED 1

# Install dependencies
#COPY ./requirements.txt /requirements.txt
#RUN pip install -r /requirements.txt

# Install dependencies
COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache postgresql-client jpeg-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev
RUN pip install -r /requirements.txt
RUN apk del .tmp-build-deps


# Setup directory structure
RUN mkdir /app
WORKDIR /app
COPY ./app/ /app

# /vol/web/media is where to store media files uploaded by the user
RUN mkdir -p /vol/web/media
# /vol/web/static is used for storing javascript file, css file etc.
RUN mkdir -p /vol/web/static
# add our user
RUN adduser -D user
# change the ownership of this file to the user that we have added
# it sets the ownership of all of the directories 
# within the volumn directory to our custom user
# -R means recursive and will apply to all sub directories as well
RUN chown -R user:user /vol/
# user can do everything withing this directory
# and the rest can read and execute from the directory
RUN chmod -R 755 /vol/web
# switch to the user
USER user