Does not work because of the forticlient firewall: some alpine repo URLs must be whitelisted, use 
`Docker` definition from `lambda_layer_docker_ubuntu`

$ docker build --platform linux/arm64  -t aws-params-and-secrets-lambda-extensions-alpine-arm64:11.0 . `
 --build-arg AWS_DEFAULT_REGION=eu-central-1 `
 --build-arg AWS_ACCESS_KEY_ID=AKI123124 `
 --build-arg AWS_SECRET_ACCESS_KEY=njDV5ul231231231231231231231LZJN4S

$ docker tag aws-params-and-secrets-lambda-extensions-alpine-arm64:11.0 kuk13/aws-params-and-secrets-lambda-extensions-alpine-arm64:11.0
$ docker push kuk13/aws-params-and-secrets-lambda-extensions-alpine-arm64:11.0


