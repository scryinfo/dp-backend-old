# Overview
The Proof Of Concept for some of the ideas put forth in the Scry.Info whitepaper is implemented and contains following three projects:
- scry-server [scryinfo/dp-contracts-old](https://github.com/scryinfo/dp-contracts-old)
- frontend [scryinfo/dp-frontend-old](https://github.com/scryinfo/dp-frontend-old)
- dp-backend [scryinfo/dp-backend-old](https://github.com/scryinfo/dp-backend-old)

# INSTALLATION INSTRUCTIONS

## Docker

1. Install Docker: https://docs.docker.com/install/. If you are on Ubuntu 16.04, do not use docker contained in the Ubuntu repositories, it is too old. Follow this howto: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-16-04
2. Change database host and credentials in `model.py`:
```
to run in docker, hostname must point to the docker container (called "postgres" in the stack created by scry-server docker-compose):

#db =  PostgresqlExtDatabase('scry', user=DB_USER,port=5432)
db =  PostgresqlExtDatabase('scry', user='scry', password='scry',host='postgres', port=5432)

```

[TODO: configuration should not be hardcoded, but loaded from .env]

3. Build+start the environment using docker-compose. Important notes:
- **docker-compose must always be run in the directory where the docker-compose.yml is located**
- **If you have local instance of parity, postgresql or ipfs running, stop them before starting those containers**
```
docker-compose up -d
```
-d means "detached" - the containers will continue to run in background and will not block your terminal
4. to get bash shell in the running environment, and activate the python venv (to run commands like you would usually):
```
docker-compose exec dp-backend-old /bin/bash
source venv/bin/activate

```

When building the container, the source code is copied inside the container - the local repository is not attached. **This means that when you make changes and you want to try them in the container, you have to do docker-compose down; docker-compose up -d --build**. Another option is to attach the local directory that contains the repository into the container, by uncommenting following lines in docker-compose.yml:

```
#    volumes:
#      - .:/home/python/dp-backend-old

```

### to test on a different branch

1. copy Dockerfile, docker-compose.yml and .dockerignore files somewhere on the side
2. checkout the branch you want to test on (ie category_tree)
3. copy the files back
4. follow the steps above


## On your own system

### Pre-requisities

Follow the repo https://github.com/scryinfo/dp-contracts-old/ to install full system.

Runs with python 3.6.

### Setup steps

Create virtualenv and install dependencies
```
bash init.sh
```

If your database is not listening on a default local socket, but you need to point it somewhere else, edit `model.py`:
[todo: settings not hardcoded, but loaded from dotenv]

```
To connect to a database on host "postgres":

db =  PostgresqlExtDatabase('scry', user='scry', password='scry',host='postgres', port=5432)
```

Start the server (by default will listen on :2222)
```
python server.py
```


### Testing
open the front end
create a user with login=22 password=22
```
 python -m demo.demo_publisher

 python test server.py
```
