REGION="us-east-1"
PLATFORM="linux/amd64"


API_REPO="397077210492.dkr.ecr.us-east-1.amazonaws.com/from-field-dev-api"


echo "Logging into ECR in region ${REGION}..."
aws ecr get-login-password --region "${REGION}" \
	| docker login --username AWS --password-stdin "${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"

docker build --platform "${PLATFORM}" -t api:latest .
docker tag api:latest ${API_REPO}:latest
docker push ${API_REPO}:latest