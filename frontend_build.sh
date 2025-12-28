REGION="us-east-1"
PLATFORM="linux/amd64"

aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 397077210492.dkr.ecr.us-east-1.amazonaws.com

docker build --platform "${PLATFORM}" -t api:latest .
docker tag api:latest 397077210492.dkr.ecr.us-east-1.amazonaws.com/from-field-dev-frontend:latest
docker push 397077210492.dkr.ecr.us-east-1.amazonaws.com/from-field-dev-frontend:latest