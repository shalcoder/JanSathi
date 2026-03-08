import boto3
from dotenv import load_dotenv

load_dotenv()

def fix_handler():
    client = boto3.client('lambda', region_name='us-east-1')
    function_name = 'jansathi-backend'
    
    print("Fetching current configuration...")
    config = client.get_function_configuration(FunctionName=function_name)
    current_handler = config['Handler']
    print(f"Current handler: {current_handler}")
    
    expected_handler = 'lambda_handler.lambda_handler'
    if current_handler != expected_handler:
        print(f"Updating handler to {expected_handler}...")
        client.update_function_configuration(
            FunctionName=function_name,
            Handler=expected_handler
        )
        print("Update successful.")
    else:
        print("Handler is already correct. This is strange.")

if __name__ == "__main__":
    fix_handler()
