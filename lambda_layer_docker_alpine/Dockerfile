# Create a build stage to copy the files from S3 using credentials
FROM alpine:latest as layer-copy

ARG AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-"eu-central-1"}
ARG AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID:-""}
ARG AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY:-""}

ENV AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}
ENV AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
ENV AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}

COPY enjoying-root.cer  /usr/local/share/ca-certificates/enjoying-root.cer
RUN cat /usr/local/share/ca-certificates/enjoying-root.cer >> /etc/ssl/certs/ca-certificates.crt



RUN apk add aws-cli curl unzip

RUN mkdir -p /opt

RUN curl $(aws lambda get-layer-version-by-arn --arn arn:aws:lambda:eu-central-1:187925254637:layer:AWS-Parameters-and-Secrets-Lambda-Extension-Arm64:11 --query 'Content.Location' --output text) --output layer.zip
RUN unzip layer.zip -d /opt
RUN rm layer.zip

# Start second stage from blank image to squash all previous history, including credentials.
FROM scratch
WORKDIR /opt
COPY --from=layer-copy /opt .