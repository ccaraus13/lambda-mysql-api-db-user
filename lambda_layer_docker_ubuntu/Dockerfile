# Create a build stage to copy the files from S3 using credentials
FROM ubuntu:latest as layer-copy

ARG AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-"eu-central-1"}
ARG AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID:-""}
ARG AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY:-""}

ENV AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}
ENV AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
ENV AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}

RUN apt-get update
RUN apt -y install curl unzip

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" --output awscliv2.zip
RUN unzip awscliv2.zip -d /opt
RUN /opt/aws/install
RUN rm awscliv2.zip
RUN rm -rf /opt/awscliv2

RUN curl $(aws lambda get-layer-version-by-arn --arn arn:aws:lambda:eu-central-1:187925254637:layer:AWS-Parameters-and-Secrets-Lambda-Extension-Arm64:11 --query 'Content.Location' --output text) --output layer.zip
RUN unzip layer.zip -d /opt
RUN rm layer.zip

# Start second stage from blank image to squash all previous history, including credentials.
FROM scratch
WORKDIR /opt
COPY --from=layer-copy /opt .