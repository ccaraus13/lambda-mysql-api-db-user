FROM kuk13/aws-params-and-secrets-lambda-extensions-alpine-arm64:11.0 AS extension-layer
FROM public.ecr.aws/lambda/python:3.11
# Layer Code

COPY --from=extension-layer /opt /opt

#FROM public.ecr.aws/lambda/python:3.11
# Function code
ENV PARAMETERS_SECRETS_EXTENSION_CACHE_ENABLED=true
ENV PARAMETERS_SECRETS_EXTENSION_CACHE_SIZE=1000
ENV PARAMETERS_SECRETS_EXTENSION_HTTP_PORT=2773
ENV PARAMETERS_SECRETS_EXTENSION_LOG_LEVEL="info"
ENV PARAMETERS_SECRETS_EXTENSION_MAX_CONNECTIONS=3
ENV SECRETS_MANAGER_TIMEOUT_MILLIS=0
ENV SECRETS_MANAGER_TTL=300
ENV SSM_PARAMETER_STORE_TIMEOUT_MILLIS=0
ENV SSM_PARAMETER_STORE_TTL=300

WORKDIR ${LAMBDA_TASK_ROOT}
# Copy requirements.txt
COPY requirements.txt .

# Install the specified packages
RUN pip install -r requirements.txt

# Copy function code
COPY create_db_api_user.py .

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "create_db_api_user.handler" ]