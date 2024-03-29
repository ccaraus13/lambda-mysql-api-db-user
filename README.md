Lambda function that creates an additional DB user by using secrets stored in AWS Secrets Manager:
1. Root secret - used to connect to DB and to run SQL queries that creates a new user
2. API DB User secret - credentials of the user to be created

# Build extension image
## Build image from `ubuntu`(as base layer)
$ cd lambda_layer_docker_ubuntu

## Or Build image from `alpine`(as base layer)
$ cd lambda_layer_docker_alpine

## Build extension image itself
$ docker build --platform linux/amd64  -t aws-params-and-secrets-lambda-extensions-arm64:11.0 . `
 --build-arg AWS_DEFAULT_REGION=eu-central-1 `                                                                                                                                      
 --build-arg AWS_ACCESS_KEY_ID=AKIAR612345567890 `
 --build-arg AWS_SECRET_ACCESS_KEY=njDV5123456789012345678899LZJN4S

# Build Lambda image
## Create `requirements.txt` in default Environment
$ pip freeze > requirements.txt

### Create (optional) other environment, install packages in it, create `requirements.txt`
#### create an `environment` where all libraries will be stored, not globally
$ python3.11.exe -m venv my_env
$ .\my_env\Scripts\activate

#### For Example install `boto3` dependency in activated `my_env`
$ pip install boto3
#### create requirements.txt
$ pip freeze > requirements.txt
$ deactivate

## Build Lamda image itself
### Build AMD platform image, and run (for local test)
$ docker build --platform linux/amd64 -t create_db_api_user:0.2 .
$ docker run --platform linux/amd64 --name lambda-create_db_api_user -p 9000:8080 create_db_api_user:0.2

### Or Build ARM platform image, and run (for local test)
$ docker build --platform linux/arm64 -t create_db_api_user:0.4 .
$ docker run --platform linux/arm64 --name lambda-create_db_api_user -p 9000:8080 create_db_api_user:0.4

### Test local running image by making a request
$ curl "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -d '{"DB_ROOT_SECRET_ID":"root", "DB_API_USER_SECRET_ID":"api", "DB_HOST": "localhost", "DB_PORT": 3313}'
### or with PowerShell
$ Invoke-WebRequest -Uri "http://localhost:9000/2015-03-31/functions/function/invocations" `
   -Method Post `
   -Body '{"DB_ROOT_SECRET_ID":"root", "DB_API_USER_SECRET_ID":"api", "DB_HOST": "localhost", "DB_PORT": 3313}' `
   -ContentType "application/json"


## Push built image to AWS ECR repository
$ docker image tag create_db_api_user:0.4 133566492045.dkr.ecr.eu-central-1.amazonaws.com/lambda-create-api-user:0.4
$ docker push 133566492045.dkr.ecr.eu-central-1.amazonaws.com/lambda-create-api-user:0.4