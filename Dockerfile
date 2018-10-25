# look at best practices document to understand why we use multi-stage build: https://docs.docker.com/develop/develop-images/dockerfile_best-practices/

#
# ---- Base Node Image ----
FROM python:3.6-slim AS base
# add user "python"
RUN adduser --disabled-password --gecos '' python
# use non-root "python" user
USER python
# set working directory
RUN mkdir -p /home/python/publisher-backend
WORKDIR /home/python/publisher-backend
# copy requirements.txt file
COPY --chown=python:python requirements.txt .

#
# ---- Dependencies ----
FROM base AS dependencies
# note: using venv so that we can easily copy all the python dependencies
RUN python3 -m venv venv
#Activating virtual environment doesn't work for building docker image, use python path in the environment instead
# install python requirements
RUN venv/bin/pip3 install -r requirements.txt
# create working folders
RUN mkdir uploaded

#
# ---- Release ----
FROM base AS release
# copy python dependencies
COPY --chown=python:python --from=dependencies /home/python/publisher-backend/venv ./venv
# copy app sources
COPY --chown=python:python . .
# put the correct .env file in place | # .env not used now
# RUN cp .env.docker .env
# expose port and define ENTRYPOINT and default CMD
EXPOSE 2222
ENTRYPOINT ["/home/python/publisher-backend/venv/bin/python"]
CMD ["server.py"]
