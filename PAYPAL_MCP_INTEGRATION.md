# PayPal MCP Integration Guide

This guide explains how to integrate PayPal's Model Context Protocol (MCP) server with your TTS-LLM-STT voice assistant for real-world business operations.

## 🎯 Overview

PayPal's MCP server provides access to powerful business tools through natural language, enabling your voice assistant to:
- Create and manage invoices
- Process payments and refunds
- Handle subscriptions
- Manage customer data
- Generate reports

## 🔧 Setup Instructions

### 1. PayPal Developer Account Setup

1. **Create PayPal Developer Account**
   - Visit [PayPal Developer Dashboard](https://developer.paypal.com/)
   - Sign up or log in with your PayPal account

2. **Create Application**
   - Go to "My Apps & Credentials"
   - Click "Create App"
   - Select "Sandbox" for testing
   - Choose "Default Application" or create custom scopes

3. **Get API Credentials**
   - Copy your **Client ID** and **Client Secret**
   - Note your **Sandbox Account** details

### 2. Environment Configuration

Add PayPal credentials to your `.env` file:

```bash
# PayPal Configuration
PAYPAL_CLIENT_ID="your_paypal_client_id"
PAYPAL_CLIENT_SECRET="your_paypal_client_secret"
PAYPAL_ENVIRONMENT="SANDBOX"  # or PRODUCTION

# Enable PayPal MCP Server
MCP_PAYPAL_SANDBOX_ENABLED=true
```

### 3. MCP Server Configuration

PayPal provides two MCP server options:

#### Remote MCP Server (Recommended)
- **Sandbox**: `https://mcp.sandbox.paypal.com/sse`
- **Production**: `https://mcp.paypal.com/sse`
- **Transport**: Server-Sent Events (SSE) or Streamable HTTP

#### Local MCP Server
```bash
npx -y @paypal/mcp --tools=all
```

## 🚀 Available PayPal Tools

Based on the [PayPal Agent Tools Reference](https://www.paypal.ai/docs/tools/agent-tools-ref), your voice assistant can:

### Invoice Management
- **Create Invoice**: Generate invoices with customer details
- **Send Invoice**: Email invoices to customers
- **List Invoices**: Retrieve invoice history
- **Get Invoice Details**: View specific invoice information
- **Update Invoice**: Modify existing invoices

### Payment Processing
- **Process Payment**: Handle one-time payments
- **Refund Payment**: Process refunds
- **Capture Payment**: Complete authorized payments
- **Void Payment**: Cancel pending payments

### Subscription Management
- **Create Subscription**: Set up recurring billing
- **Update Subscription**: Modify subscription details
- **Cancel Subscription**: Stop recurring payments
- **List Subscriptions**: View active subscriptions

### Customer Management
- **Create Customer**: Add new customer records
- **Update Customer**: Modify customer information
- **List Customers**: Retrieve customer database
- **Get Customer Details**: View specific customer info

## 🎤 Voice Assistant Usage Examples

### Authentication
**User**: "Authenticate with PayPal"

**Assistant**: "I'll help you authenticate with PayPal. You'll need to visit the PayPal MCP server URL to complete OAuth authentication. Here are the steps..."

### Invoice Creation
**User**: "Create an invoice for John Smith for $500 for web development services"

**Assistant**: "I'll create a PayPal invoice for John Smith for $500 for web development services. Let me process that for you..."

### Payment Processing
**User**: "Process a $100 payment from customer@example.com"

**Assistant**: "I'll process a $100 payment from customer@example.com through PayPal. Processing payment now..."

### Subscription Management
**User**: "Set up a monthly subscription for $50 for premium support"

**Assistant**: "I'll create a monthly subscription for $50 for premium support. Setting up recurring billing..."

## 🔐 Authentication Flow

### Remote MCP Server Authentication

1. **Credential Setup**: Configure Client ID and Client Secret from PayPal Developer Dashboard
2. **MCP Server Connection**: Connect to PayPal's remote MCP server using OAuth
3. **Browser Authentication**: User visits PayPal MCP server URL for OAuth flow
4. **Authorization**: Grant permissions to MCP client
5. **Token Exchange**: Receive access token for API calls
6. **Session Management**: Maintain authenticated session

### Security Considerations

- **Sandbox Testing**: Always test with sandbox environment first
- **Credential Management**: Securely store Client ID and Client Secret
- **OAuth Flow**: Use proper OAuth 2.0 flow for authentication
- **Scope Permissions**: Only request necessary PayPal permissions
- **HTTPS Only**: Ensure all communications use secure connections

## 🛠️ Implementation Details

### Function Schema
```python
paypal_function = FunctionSchema(
    name="paypal_invoice_management",
    description="Manage PayPal invoices, payments, and subscriptions",
    properties={
        "action": {
            "type": "string",
            "enum": ["create_invoice", "list_invoices", "get_invoice", "send_invoice"],
            "description": "The PayPal action to perform"
        },
        "customer_email": {
            "type": "string",
            "description": "Customer email address"
        },
        "amount": {
            "type": "number",
            "description": "Invoice amount in USD"
        },
        "description": {
            "type": "string",
            "description": "Invoice description"
        }
    },
    required=["action"]
)
```

### Error Handling
- **Authentication Errors**: Guide users to complete OAuth flow
- **API Errors**: Provide clear error messages and next steps
- **Rate Limiting**: Handle PayPal API rate limits gracefully
- **Network Issues**: Retry failed requests with exponential backoff

## 📊 Testing & Validation

### Sandbox Testing
1. **Test Invoice Creation**: Create test invoices with sandbox accounts
2. **Verify Payment Flow**: Test payment processing with sandbox payments
3. **Validate Webhooks**: Ensure webhook events are properly handled
4. **Check Error Scenarios**: Test various error conditions

### Production Deployment
1. **Switch to Production**: Update environment variables
2. **Update MCP Server URL**: Use production PayPal MCP endpoint
3. **Verify Permissions**: Ensure all required scopes are granted
4. **Monitor Performance**: Track API response times and success rates

## 🔄 Future Enhancements

### Additional PayPal Tools
- **Dispute Management**: Handle payment disputes
- **Reporting**: Generate financial reports
- **Webhook Management**: Configure event notifications
- **Multi-Currency**: Support international payments

### Integration Opportunities
- **CRM Integration**: Connect with customer databases
- **Accounting Software**: Sync with QuickBooks, Xero
- **E-commerce Platforms**: Integrate with Shopify, WooCommerce
- **Analytics**: Track payment patterns and trends

## 📚 Resources

- [PayPal MCP Quickstart Guide](https://www.paypal.ai/docs/tools/mcp-quickstart)
- [PayPal Agent Tools Reference](https://www.paypal.ai/docs/tools/agent-tools-ref)
- [PayPal Developer Documentation](https://developer.paypal.com/docs/)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)

## 🆘 Troubleshooting

### Common Issues

**Authentication Failed**
- Verify PayPal credentials are correct
- Check if OAuth flow was completed
- Ensure proper scopes are requested

**API Errors**
- Check PayPal API status
- Verify request format and parameters
- Review rate limiting and quotas

**MCP Connection Issues**
- Verify MCP server URL is accessible
- Check network connectivity
- Review MCP client configuration

### Support
- **PayPal Developer Support**: [PayPal Developer Community](https://developer.paypal.com/support/)
- **MCP Documentation**: [Model Context Protocol](https://modelcontextprotocol.io/)
- **Voice Assistant Issues**: Check application logs and error messages

---

*This integration enables your voice assistant to perform real-world business operations through natural conversation, making it a powerful tool for merchants and service providers.*
