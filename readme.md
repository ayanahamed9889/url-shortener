# Serverless URL Shortener

A completely serverless URL shortener built with AWS Lambda, API Gateway, and DynamoDB.

## Features
- Shorten long URLs
- Redirect to original URLs  
- Click tracking
- Serverless architecture
- Free Tier compatible

## AWS Services Used
- AWS Lambda
- API Gateway
- DynamoDB
- IAM

## API Endpoints

### Create Short URL
```bash
POST /create
{
    "long_url": "https://example.com"
}
