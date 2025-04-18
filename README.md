
Serverless Computing : Serverless computing is an application development and execution model that allows developers to build and run code without provisioning or managing servers or back-end infrastructure.

Cold start latency: Cold start latency refers to the increased response time experienced when a serverless function or application is invoked after a period of inactivity


### **1. Configure AWS CLI**

Before we start, make sure your **AWS CLI** is configured correctly with your AWS credentials.

### Command:

```bash

aws configure
```

You will be prompted for the following:

- **AWS Access Key ID**: (Enter your access key)
- **AWS Secret Access Key**: (Enter your secret key)
- **Default region name**: (e.g., `us-west-2` — change to the appropriate region)
- **Default output format**: (e.g., `json`)

### **2. Create IAM Role for Lambda Execution**

Lambda functions need a specific IAM role with permissions to execute and access resources like CloudWatch logs. If you don’t have the role yet, here’s how to create one:

### Command to create the IAM role:

```bash

aws iam create-role \
    --role-name lambda-role \
    --assume-role-policy-document file://trust-policy.json

```

Where the **`trust-policy.json`** file contains the following JSON to allow Lambda to assume this role:

```json

{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}

```

### Attach necessary policies to the role:

For Lambda to run properly, it needs permissions to write logs to CloudWatch. Attach the following managed policy for basic Lambda execution:

```bash

aws iam attach-role-policy \
    --role-name lambda-role \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

```

---

### **3. Create Lambda Function**

Now that we have the IAM role, let’s create a simple Lambda function.

### **Create the Lambda function code**

- Create a file called `index.js` for a simple Node.js function:

```jsx

// Simulating a basic invocation history and prediction analysis
const window_size = 24; // In hours (for simplicity)
const threshold = 0.6;  // Prediction confidence threshold
const warm_up_time = 0.1; // in seconds (for simulation)

// Simulated invocation history for PRP
let invocationHistory = [];

// Function to simulate invocation frequency over time
function getInvocationFrequency() {
    const now = new Date();
    const recentInvocations = invocationHistory.filter(invocation => {
        const timeDiff = (now - new Date(invocation.timestamp)) / (1000 * 60 * 60); // In hours
        return timeDiff <= window_size;
    });
    return recentInvocations.length / window_size; // Invocations per hour
}

// Function to simulate prediction analysis
function predictionAnalysis() {
    const frequency = getInvocationFrequency();
    console.log("Recent Invocation Frequency: ", frequency);

    // Simulate prediction confidence (probability) based on frequency
    const probability = frequency >= 0.5 ? 0.8 : 0.4; // Simple threshold logic
    console.log("Predicted Confidence: ", probability);

    return probability;
}

// Function to simulate cold start behavior
function coldStart() {
    console.log("Starting a cold start...");
    // Simulate some warm-up time for the container
    return new Promise(resolve => setTimeout(resolve, warm_up_time * 1000));
}

// Lambda handler
exports.handler = async (event) => {
    // Simulate a new invocation event
    const now = new Date();
    invocationHistory.push({ timestamp: now });

    // Prediction analysis
    const predictedConfidence = predictionAnalysis();

    let response;

    if (predictedConfidence >= threshold) {
        console.log("Using existing container...");
        // Simulate using a pre-warmed container
        response = {
            statusCode: 200,
            body: JSON.stringify({ message: "Used pre-warmed container" }),
        };
    } else {
        console.log("Cold start path triggered...");
        await coldStart(); // Simulate cold start
        response = {
            statusCode: 200,
            body: JSON.stringify({ message: "Cold start completed" }),
        };
    }

    // Return the response
    return response;
};

```

### **Zip the Lambda function**

Lambda requires the code to be uploaded in a zip file. Let’s zip it up:

```bash
 compress-Archive -Path index.js -DestinationPath function.zip
```

### **Create the Lambda function using AWS CLI**

Run the following command to create your Lambda function using the zip file:

```bash

aws lambda create-function \
    --function-name HelloWorldFunction \
    --runtime nodejs18.x \
    --role arn:aws:iam::<your-aws-account-id>:role/lambda-role \
    --handler index.handler \
    --zip-file fileb://function.zip
```

Make sure to replace `<your-aws-account-id>` with your actual AWS account ID.

---

### **4. Test Lambda Function**

### **Invoke the Lambda function**

Once the function is created, invoke it to generate logs.

```bash

aws lambda invoke \
    --function-name HelloWorldFunction \
    --payload '{}' \
    output.json

```

This will invoke the Lambda function with an empty payload and store the result in `output.json`.

### **Check the invocation result**

You can inspect the `output.json` file to verify that the function executed successfully.

---

### **5. Check CloudWatch Logs**

Lambda logs are automatically sent to **CloudWatch Logs**. Now, let’s check the logs.

### **List log streams in CloudWatch**

To list the available log streams for your Lambda function, use the following command:

```bash

aws logs describe-log-streams \
    --log-group-name /aws/lambda/HelloWorldFunction \
    --region us-west-2  # Replace with your region

```

This command will list the log streams. Look for a stream like `2025/03/09/[$LATEST]xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`.

### **Get log events from the correct stream**

Once you have the exact log stream name, fetch the log events with this command:

```bash

aws logs get-log-events \
    --log-group-name /aws/lambda/HelloWorldFunction \
    --log-stream-name "2025/03/09/[$LATEST]xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
    --region us-west-2  # Replace with your region

```

Make sure to replace the `log-stream-name` with the exact value from the list of log streams you fetched earlier.

---

### **6. Troubleshooting Tips**

- **No logs?** Ensure that the Lambda function has run at least once. If it hasn't, trigger the function using `aws lambda invoke` and wait for CloudWatch to process the logs.
- **Wrong region?** Ensure that your AWS CLI commands are being executed in the correct region where the Lambda function was deployed.
- **Permissions:** Ensure that the IAM role used by Lambda has the appropriate permissions, especially for logging to CloudWatch (`AWSLambdaBasicExecutionRole`).

---

### **7. Clean Up**

If you want to delete everything after testing:

### Delete Lambda function:

```bash

aws lambda delete-function --function-name HelloWorldFunction

```

### Detach IAM policies and delete role:

```bash

aws iam detach-role-policy --role-name lambda-role --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam delete-role --role-name lambda-role

```

### Delete CloudWatch log group:

```bash

aws logs delete-log-group --log-group-name /aws/lambda/HelloWorldFunction

```

---

plotting graph

with the csv file

```c
import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file
df = pd.read_csv('prp_vs_trad.csv')

# Convert timestamp to datetime format
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Separate data for Traditional and PRP methods
df_traditional = df[df['method'] == 'Traditional']
df_prp = df[df['method'] == 'PRP']

# Plot the comparison
plt.figure(figsize=(10, 6))

# Plot for Traditional method
plt.plot(df_traditional['timestamp'], df_traditional['cold_start_duration'], label="Traditional Cold Start", color='blue', marker='o')

# Plot for PRP method
plt.plot(df_prp['timestamp'], df_prp['cold_start_duration'], label="PRP Algorithm", color='green', marker='s')

# Add labels and title
plt.title('Cold Start Duration Comparison: PRP vs. Traditional Method')
plt.xlabel('Time')
plt.ylabel('Cold Start Duration (ms)')
plt.legend()

# Rotate the x-axis labels for better readability
plt.xticks(rotation=45)

# Show the plot
plt.tight_layout()
plt.show()

```
