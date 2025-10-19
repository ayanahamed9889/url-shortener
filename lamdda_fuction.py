import json
import boto3
import random
import string
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('url-shortener')

def generate_short_code(length=6):
    """Generate a random 6-character short code"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))
    
    http_method = event['httpMethod']
    path = event.get('path', '')
    
    print(f"Method: {http_method}, Path: {path}")
    
    if http_method == 'POST' and path == '/create':
        return create_short_url(event)
    elif http_method == 'GET' and path.startswith('/'):
        short_code = path[1:]
        if short_code and short_code != 'create':
            return redirect_to_url(short_code)
    
    return {
        'statusCode': 400,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({'error': 'Invalid request. Use POST /create or GET /{code}'})
    }

def create_short_url(event):
    try:
        print("Creating short URL...")
        
        if 'body' not in event:
            return error_response('Missing request body')
            
        if isinstance(event['body'], str):
            body = json.loads(event['body'])
        else:
            body = event['body']
            
        long_url = body.get('long_url')
        
        if not long_url:
            return error_response('long_url is required')
        
        short_code = generate_short_code()
        print(f"Generated short code: {short_code} for URL: {long_url}")
        
        table.put_item(
            Item={
                'short_code': short_code,
                'long_url': long_url,
                'created_at': datetime.now().isoformat(),
                'click_count': 0
            }
        )
        
        domain_name = event['requestContext']['domainName']
        stage = event['requestContext']['stage']
        short_url = f"https://{domain_name}/{stage}/{short_code}"
        
        print(f"Short URL created: {short_url}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'short_code': short_code,
                'short_url': short_url,
                'long_url': long_url,
                'message': 'Short URL created successfully'
            })
        }
        
    except Exception as e:
        print(f"Error creating short URL: {str(e)}")
        return error_response(f'Internal server error: {str(e)}')

def redirect_to_url(short_code):
    try:
        print(f"Redirecting for short code: {short_code}")
        
        response = table.get_item(Key={'short_code': short_code})
        
        if 'Item' not in response:
            return error_response('URL not found', 404)
        
        item = response['Item']
        long_url = item['long_url']
        
        print(f"Found long URL: {long_url}")
        
        table.update_item(
            Key={'short_code': short_code},
            UpdateExpression='SET click_count = click_count + :val',
            ExpressionAttributeValues={':val': 1}
        )
        
        return {
            'statusCode': 302,
            'headers': {
                'Location': long_url,
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'message': 'Redirecting...', 'url': long_url})
        }
        
    except Exception as e:
        print(f"Error redirecting: {str(e)}")
        return error_response(f'Internal server error: {str(e)}')

def error_response(message, status_code=400):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({'error': message})
    }