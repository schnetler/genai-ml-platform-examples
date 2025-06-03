# Travel Planner Frontend

This is the frontend application for the Travel Planning Demo application. It connects to the AWS backend services to provide a real-time travel planning experience.

## Connecting to AWS Backend

To connect the frontend to your deployed AWS backend:

1. Retrieve the CloudFormation outputs from your deployed stack:

```bash
aws cloudformation describe-stacks --query "Stacks[?contains(StackName, 'infrastructure')].Outputs[*].[OutputKey, OutputValue]" --output table
```

2. Look for the following outputs:
   - `ApiEndpoint` - The REST API endpoint URL
   - `WebSocketApiEndpoint` - The WebSocket API endpoint URL

3. Create a `.env.local` file in the frontend directory with these values:

```
REACT_APP_API_ENDPOINT=<ApiEndpoint value>
REACT_APP_WEBSOCKET_ENDPOINT=<WebSocketApiEndpoint value>
```

Example:
```
REACT_APP_API_ENDPOINT=https://abcdef123.execute-api.us-east-1.amazonaws.com/dev
REACT_APP_WEBSOCKET_ENDPOINT=wss://abcdef123.execute-api.us-east-1.amazonaws.com/dev
```

## Local Development

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

## Testing the Connection

After configuring the endpoints, you can test the connection:

1. Open the browser console to check for any connection errors
2. Submit a travel planning request through the UI
3. Monitor the WebSocket connection status in the UI
4. Check for any API errors in the console

## Troubleshooting

Common issues:
- **CORS errors**: Ensure the backend API Gateway has CORS properly configured
- **WebSocket connection failures**: Verify the WebSocket endpoint is correct and accessible
- **Authentication errors**: If using authentication, ensure the token is correctly provided

## Architecture

The frontend uses several services to communicate with the backend:

- `apiClient.ts` - Handles REST API calls
- `WebSocketService.ts` - Manages WebSocket connections
- `WorkflowUpdateService.ts` - Processes workflow updates from WebSocket
- `TravelPlanService.ts` - Manages travel plan data
- `InteractionService.ts` - Handles user interactions with the workflow

## Workflow

1. User submits a travel plan request via the UI
2. The request is sent to the `/plan` API endpoint
3. The backend orchestrates Strands Agents powered by AWS KnowledgeBases and Amazon DSQL
4. Real-time updates are sent via WebSocket
5. If user interaction is needed, an interaction request is sent
6. User responds via the `/interaction/{interactionId}` endpoint
7. The workflow continues and final results are displayed 