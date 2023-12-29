import boto3
import json
import zipfile
import io
import time

def create_or_update_lambda_function(function_name: str, code: str, handler: str = 'lambda_function.lambda_handler', runtime: str = 'python3.8') -> dict:
    """
    Create or update a Lambda function.

    Args:
        function_name (str): The name of the function.
        code (str): The code for the function.
        handler (str): The handler for the function.
        runtime (str, optional): The runtime for the function. Defaults to 'python3.8'.

    Returns:
        dict: The response from the Lambda client, or an error dictionary.

    Raises:
        Exception: If an error occurs during the creation or update of the Lambda function.
    """
    iam_client = boto3.client('iam')
    lambda_client = boto3.client('lambda')

    # Create a unique role name based on the function name
    role_name = f"{function_name.lower()}Role"

    # Create or get role
    try:
        # Create a role with basic Lambda execution permissions and CloudWatch Logs access
        assume_role_policy_document = json.dumps({
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }]
        })
        create_role_response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=assume_role_policy_document
        )
        role_arn = create_role_response['Role']['Arn']

        # Attach policies
        iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/AmazonS3FullAccess'
        )
        iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/CloudWatchLogsFullAccess'
        )
    except iam_client.exceptions.EntityAlreadyExistsException:
        # If the role already exists, get its ARN
        role_arn = iam_client.get_role(RoleName=role_name)['Role']['Arn']

    # Create a zip file in memory containing the code
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a') as zf:
        zf.writestr('lambda_function.py', code)
    zip_buffer.seek(0)

    try:
        # Check if the function already exists
        try:
            lambda_client.get_function(FunctionName=function_name)
            update = True
        except lambda_client.exceptions.ResourceNotFoundException:
            update = False

        # Delay for role propagation
        time.sleep(10)  # 10 seconds delay

        # Create or update the Lambda function
        if update:
            # Update the existing function
            response = lambda_client.update_function_code(
                FunctionName=function_name,
                ZipFile=zip_buffer.read(),
                Publish=True
            )
        else:
            # Create a new function
            response = lambda_client.create_function(
                FunctionName=function_name,
                Runtime=runtime,
                Role=role_arn,
                Handler=handler,
                Code={'ZipFile': zip_buffer.read()},
                Publish=True,
                Timeout=900  # Maximum timeout of 15 minutes
            )
        return response
    except Exception as e:
        return {'Error': str(e)}