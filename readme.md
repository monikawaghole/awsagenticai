
# **AI-Powered Blog Generator using AWS Bedrock**

## **Overview**

An AI-powered blog generator that uses AWS Bedrock’s LLaMA3-70B-instruct model to create engaging blog posts based on user input. The application generates blog content based on a specified topic, expertise level, and context, then uploads the content to Amazon S3 for easy access.

## **Features**

- **Dynamic Blog Generation**: Automatically generates blog posts based on the user’s topic, expertise level, and context.
- **S3 Storage**: Stores generated content in an Amazon S3 bucket as plain text files.
- **Error Handling**: Includes robust error handling and logging to ensure smooth execution.

## **Tech Stack**

- **AWS Bedrock**: For content generation using advanced LLaMA3-70B model.
- **AWS Lambda**: For serverless execution of the blog generation process.
- **Amazon S3**: For storing generated blog content as .txt files.
- **Boto3 SDK**: To interact with AWS services.
- **Python**: Core language used for logic and integration.

## **How It Works**

1. **User Input**: A POST request with blog topic, expertise level, and context is received.
2. **Content Generation**: AWS Bedrock’s LLaMA3-70B model is invoked to generate the blog content.
3. **Content Storage**: The generated content is stored as a plain text file in an S3 bucket.
4. **Response**: A success or failure message is returned to the user.

## **Setup Instructions**

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-blog-generator.git
   ```

2. Install dependencies:
   ```bash
   pip install boto3 botocore
   ```

3. Deploy the Lambda function:
   - Zip the project files and upload them to AWS Lambda.
   - Ensure that the Lambda function has the required IAM roles for Bedrock and S3 access.

4. Configure API Gateway (optional) to expose the Lambda function as a RESTful API.

5. Set up your S3 bucket for storing generated content and update the bucket name in the code.

## **API Usage**

- **POST /generate-blog**
  
  **Request Body:**
  ```json
  {
    "blogTopic": "Machine Learning",
    "level": "Expert",
    "context": "The future of AI in healthcare."
  }
  ```

  **Response:**
  ```json
  {
    "blog": "Generated blog content...",
    "message": "Content successfully generated and uploaded."
  }
  ```
## 🔐 Authentication Setup (Safe Usage)

To run this project securely, you must configure AWS credentials properly. **Never hardcode keys or commit them to GitHub.**

### 🔧 Step 1: Create a `.env` file

Copy the template below into a `.env` file in your project root:

```env
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_DEFAULT_REGION=us-east-1
S3_BUCKET_NAME=your-s3-bucket-name
MODEL_ID=your-model-id  # Example: us.meta.llama3-3-70b-instruct-v1:0

## **License**

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.


