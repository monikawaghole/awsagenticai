import json
import boto3
import botocore.config
from datetime import datetime
import logging

# Initialize logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def content_generation(blogtopic: str, expertise_level: str, additional_context: str) -> dict:
    """
    Generate blog content using AWS Bedrock.
    Returns: Plain text blog content.
    """
    full_prompt = f"""You are a helpful AI assistant. Follow these instructions exactly:
    
    1.Generate a 200-300 word informative blog post on the following topic for a {expertise_level.lower()} audience.
    3.Do NOT add any comments, disclaimers, or follow-up dialogue. Always return the blog content as plain text.

    Topic: {blogtopic}
    Expertise Level: {expertise_level}
    Additional Context: {additional_context}
    """
    
    body = {
        "prompt": full_prompt,
        "max_gen_len": 512,
        "temperature": 0.5,
        "top_p": 0.9
    }

    try:
        logger.info(f"Invoking Bedrock model with prompt: {full_prompt}")
        
        bedrock = boto3.client(
            service_name="bedrock-runtime",
            region_name="us-east-1",
            config=botocore.config.Config(
                read_timeout=300,
                retries={'max_attempts': 3}
            )
        )
        
        response = bedrock.invoke_model(
            body=json.dumps(body),
            modelId="us.meta.llama3-3-70b-instruct-v1:0"
        )
        
        # Log the full response body to diagnose issues
        response_body = response['body'].read().decode('utf-8')
        logger.info(f"Bedrock response: {response_body}")
        
        # Try to parse the generated text
        response_json = json.loads(response_body)
        generated_text = response_json.get('generation', '').strip()

        if not generated_text:
            logger.error("No valid content returned from the model.")
            return {"blog": "Failed to generate content. Please try again."}

        return {"blog": generated_text}  # Return only the generated text without JSON structure
            
    except Exception as e:
        logger.error(f"Bedrock invocation failed: {str(e)}")
        return {"blog": "Failed to generate content. Please try again."}

def s3_uploader(content: dict, bucket: str, prefix: str) -> bool:
    """Upload generated content to S3 as a plain text file"""
    try:
        s3 = boto3.client('s3')
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        # Use .txt extension for plain text
        key = f"{prefix}/{timestamp}.txt"
        
        # Extract only the blog content as plain text
        blog_content = content.get('blog', '').strip()
        
        s3.put_object(
            Body=blog_content,  # Upload the content as plain text
            Bucket=bucket,
            Key=key,
            ContentType='text/plain'  # Set the content type to plain text
        )
        return True
    except Exception as e:
        logger.error(f"S3 upload failed: {str(e)}")
        return False

def validate_input(event: dict) -> tuple:
    """Validate and extract input parameters"""
    try:
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        blog_topic = body.get('blogTopic', '').strip()
        if not blog_topic:
            raise ValueError("Blog topic is required")
            
        return (
            blog_topic,
            body.get('level', 'Intermediate'),
            body.get('context', '')
        )
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON payload")
    except Exception as e:
        raise ValueError(str(e))

def format_response(content: dict, status_code: int = 200) -> dict:
    """Format Lambda response with proper headers"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(content)
    }

def lambda_handler(event, context):
    try:
        logger.info(f"Incoming event: {json.dumps(event)}")
        
        # Validate and extract input
        blog_topic, expertise_level, additional_context = validate_input(event)
        
        # Generate content
        generated_content = content_generation(
            blogtopic=blog_topic,
            expertise_level=expertise_level,
            additional_context=additional_context
        )
        
        logger.info(f"Generated Content: {generated_content}")
        
        # Upload to S3 as a .txt file
        s3_upload_success = s3_uploader(
            content=generated_content,
            bucket="blogcreatorbucket",  # Replace with your actual bucket name
            prefix="generated-content"
        )
        
        # Return only blog content, or error if it fails
        if s3_upload_success:
            return format_response({
                "blog": generated_content.get("blog", ""),
                "message": "Blog content successfully generated and uploaded."
            })
        else:
            return format_response({
                "blog": generated_content.get("blog", ""),
                "message": "Failed to upload blog content to S3."
            })
        
    except ValueError as e:
        logger.error(f"Input validation error: {str(e)}")
        return format_response(
            {"error": str(e), "success": False},
            400
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return format_response(
            {"error": "Internal server error", "details": str(e), "success": False},
            500
        )
