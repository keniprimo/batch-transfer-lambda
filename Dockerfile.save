# 🆕 Force Linux x86_64 (Amazon Linux matching AWS Lambda)
FROM --platform=linux/amd64 public.ecr.aws/lambda/python:3.9

RUN yum install -y gcc git python3-devel zip

WORKDIR /app

COPY requirements.txt .
COPY batch_transfer_lambda.py .
COPY solana_utils.py .

RUN pip install -r requirements.txt -t .

RUN zip -r9 /tmp/batch_transfer_lambda.zip .
