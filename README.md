## Progressive Motorcycle Bot Rating Workflow

1. Request is made to xilo-api-workflows for a rate
2. InsuranceData is transformed to ProgressiveMotorcycleBot data based on the product (e.g. auto, home, motorcycle) and the US state (e.g. California, Arizona)
3. Request is made from xilo-api-workflows to progressive-motorcycle-bot lambda
4. Lambda function receives a request with modified insurance data in body
5. Bot logs into the carrier portal (using MFA if necessary which is handled in xilo-api-workflows)
6. Navigates through product and state selection
7. Fills out the quote form with provided data
8. Retrieves and structures the quote
9. Returns the structured quote or error information

## Key Components

### Workflows Adapter

Located in `xilo-api-workflows`, this component converts the input `InsuranceData` to carrier, LOB, and state-specific data formats for `progressive-motorcycle-bot`

### Lambda Function

The main entry point (`./handler.py`) handles:
- Concurrent processing
- Invocation of chrome / scrapy / selenium bots
- Orchestration of the quoting process
- Error handling and response formatting

### Form Fill Handlers

Individual modules in the `ForAgentsOnly/spiders/for_agents_boy.py` file manages fill form with specific pages on the carrier portal:
- Login
- Product and State selection
- Quote form filling

### Utility Functions

The `./ForAgentsOnly/utils.py` file contains reusable functions for:
- Field handling (filling, selecting, retrying)
- Error handling
- MFA service integration

## Input and Output

Refer to `./example_input_output.ts` in the related TypeScript repository for expected input and output structures.

## Development Guidelines

1. Use only Scrapy, Selenium, and Chrome WebDriver for web interactions
2. Implement proper error handling and logging
3. Ensure compatibility with existing CodeBuild, Serverless, and Docker setups
4. Aim for a 95%+ success rate in login, form filling, and quote retrieval
5. Implement retries and fallbacks for improved reliability

## Testing

Comprehensive unit and integration tests should be implemented in the `tests/` directory to ensure reliability and maintain the target 95%+ success rate.

## Deployment

The project uses CodeBuild, Serverless Framework, and Docker for CI/CD and deployment. Ensure any changes are compatible with the existing setup. In order to set this up locally you must:

1. Download Docker
2. Run the command `docker build --platform=linux/amd64 -t progressive_scraper .`
3. Once the image builds successfully, run the command `docker run --platform=linux/amd64 -p 9000:8080  progressive_scraper`
4. Run an API call (e.g. via Postman) to `http://localhost:9000/2015-03-31/functions/function/invocations` with the proper payload nested within `{"body":{...DATA}}` to invoke the handler.py method

## Making Pull Requests

1. Fork the progressive-motorcycle-bot repo
2. When completing code, push it up and make a PR from your forked repo to our team-xilo `develop` branch
3. team-xilo will merge it and then will merge to main where CI/CD will auto-deploy it

## MFA Handling

The `./ForAgentsOnly/utils.py` module manages Multi-Factor Authentication, supporting SMS, Auth Code, and Email methods.

## Cookie Management

Implement cookie storage and retrieval to bypass login on subsequent runs, improving efficiency.

## Error Handling

Proper error handling is crucial. Use the `./ForAgentsOnly/utils.py` module to manage and report errors consistently.

## Logging and Monitoring

Implement detailed logging throughout the Lambda function, especially during page transitions and form filling, to aid in debugging and monitoring.

## Performance Considerations

- Optimize Selenium and Scrapy usage for faster execution
- Implement intelligent waiting and retry mechanisms
- Use concurrent processing where applicable

## Security

- Ensure secure handling of login credentials and MFA information
- Implement proper IAM roles and permissions for the Lambda function
- Regularly update dependencies to patch security vulnerabilities

## Maintenance

Regular maintenance tasks:
- Update Chrome WebDriver as needed
- Monitor and adapt to changes in carrier portals
- Review and optimize performance based on CloudWatch metrics

