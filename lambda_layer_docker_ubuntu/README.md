# Creates image of the AWS Parameters and Secrets lambda extension to be used as layer in the resulting lambda: gets and decrypts a secret
# https://docs.aws.amazon.com/secretsmanager/latest/userguide/retrieving-secrets_lambda.html

# Since resulting lambda is build and used as image, the extension should be `imported` in the resulting lambda image

$ docker build --platform linux/amd64  -t aws-params-and-secrets-lambda-extensions-arm64:11.0 . `
--build-arg AWS_DEFAULT_REGION=eu-central-1 `                                                                                                                                      
--build-arg AWS_ACCESS_KEY_ID=AKIAR612345567890 `
--build-arg AWS_SECRET_ACCESS_KEY=njDV5123456789012345678899LZJN4S

$ docker image tag aws-params-and-secrets-lambda-extensions-arm64:11.0 kuk13/aws-params-and-secrets-lambda-extensions-arm64:11.0

# Push is required, otherwise on creating lambda image - it cannot be found, and build fails
$ docker push kuk13/aws-params-and-secrets-lambda-extensions-arm64:11.0