# 🏭 Production Configuration Guide

This guide covers production-ready deployment of your Notion MCP server.

## 🔧 Environment Variables

### **Required Variables**

| Variable       | Description                   | Example                                              |
| -------------- | ----------------------------- | ---------------------------------------------------- |
| `NOTION_TOKEN` | Your Notion integration token | `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` |

### **Optional Variables**

| Variable                   | Description                          | Default         | Example                                |
| -------------------------- | ------------------------------------ | --------------- | -------------------------------------- |
| `NOTION_DEFAULT_PARENT_ID` | Default parent page ID for new pages | Auto-discovered | `22150c4e-aa2a-8078-b15a-cd26efe9dfb1` |
| `MCP_TRANSPORT`            | Transport protocol                   | `http`          | `http` or `stdio`                      |
| `MCP_HOST`                 | Server host                          | `0.0.0.0`       | `localhost`                            |
| `MCP_PORT`                 | Server port                          | `8080`          | `3000`                                 |
| `PORT`                     | Render/Heroku port override          | Uses `MCP_PORT` | `8080`                                 |

## 🚀 Deployment Options

### **Option 1: Render (Recommended)**

1. **Create Web Service**:

   - Image: `ankitmalik84/notion-mcp-server:latest`
   - Port: `8080`

2. **Set Environment Variables**:

   ```bash
   NOTION_TOKEN=your_notion_token_here
   NOTION_DEFAULT_PARENT_ID=optional_parent_page_id
   ```

3. **Deploy**: Your service will be available at `https://your-app.onrender.com/`

### **Option 2: Docker Compose**

```yaml
version: "3.8"
services:
  notion-mcp:
    image: ankitmalik84/notion-mcp-server:latest
    ports:
      - "8080:8080"
    environment:
      - NOTION_TOKEN=your_notion_token_here
      - NOTION_DEFAULT_PARENT_ID=optional_parent_page_id
      - MCP_TRANSPORT=http
    restart: unless-stopped
```

### **Option 3: Kubernetes**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: notion-mcp-server
spec:
  replicas: 1
  selector:
    matchLabels:
      app: notion-mcp-server
  template:
    metadata:
      labels:
        app: notion-mcp-server
    spec:
      containers:
        - name: notion-mcp-server
          image: ankitmalik84/notion-mcp-server:latest
          ports:
            - containerPort: 8080
          env:
            - name: NOTION_TOKEN
              valueFrom:
                secretKeyRef:
                  name: notion-secrets
                  key: token
            - name: NOTION_DEFAULT_PARENT_ID
              value: "your_parent_id_here"
---
apiVersion: v1
kind: Service
metadata:
  name: notion-mcp-service
spec:
  selector:
    app: notion-mcp-server
  ports:
    - port: 80
      targetPort: 8080
  type: LoadBalancer
```

## 🔍 Parent Page Discovery

The server uses intelligent parent page discovery:

### **Strategy 1: Environment Variable**

```bash
NOTION_DEFAULT_PARENT_ID=22150c4e-aa2a-8078-b15a-cd26efe9dfb1
```

### **Strategy 2: Auto-Discovery**

The server searches for pages with these names (in order):

1. "MCP Pages"
2. "AI Assistant Pages"
3. "Generated Content"
4. "Notes"

### **Strategy 3: First Available Page**

Uses the first accessible page in your workspace

### **Strategy 4: Auto-Create Parent**

Attempts to create "MCP Generated Pages" (if permissions allow)

## ⚙️ Configuration Examples

### **Minimal Configuration**

```bash
# Only required variable
NOTION_TOKEN=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
```

### **Recommended Configuration**

```bash
# Required
NOTION_TOKEN=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

# Optional but recommended
NOTION_DEFAULT_PARENT_ID=22150c4e-aa2a-8078-b15a-cd26efe9dfb1
```

### **Custom Port Configuration**

```bash
NOTION_TOKEN=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
MCP_PORT=3000
MCP_HOST=localhost
```

## 🧪 Testing Your Deployment

### **Health Check**

```bash
curl https://your-deployment-url.com/
```

**Expected Response:**

```json
{
  "status": "running",
  "server": "notion-mcp-server",
  "transport": "http",
  "available_tools": [
    "search_notion_pages",
    "get_notion_page",
    "create_notion_page",
    "get_notion_database"
  ]
}
```

### **Test Page Creation**

```bash
curl -X POST https://your-deployment-url.com/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "create_notion_page",
      "arguments": {
        "title": "Production Test Page",
        "content": "This page was created to test the production deployment."
      }
    },
    "id": 1
  }'
```

## 🔒 Security Best Practices

### **1. Environment Variables**

- Never commit tokens to version control
- Use secure environment variable storage
- Rotate tokens regularly

### **2. Network Security**

- Use HTTPS in production
- Consider IP allowlisting if needed
- Monitor access logs

### **3. Notion Permissions**

- Use least privilege principle
- Limit integration permissions to necessary capabilities
- Regularly review workspace access

## 📊 Monitoring

### **Health Endpoints**

- `GET /` - Server status and available tools
- Monitor HTTP response codes
- Set up alerts for downtime

### **Logs**

- Monitor server startup logs
- Check for parent page discovery status
- Watch for API rate limiting

### **Metrics to Track**

- Request latency
- Success/error rates
- Page creation frequency
- Parent page discovery success

## 🚨 Troubleshooting

### **"No suitable parent page found"**

```bash
# Solution 1: Set explicit parent
NOTION_DEFAULT_PARENT_ID=your_page_id_here

# Solution 2: Create a page named "MCP Pages" in Notion
# Solution 3: Ensure integration has access to existing pages
```

### **"Notion API error"**

- Check token validity
- Verify integration permissions
- Ensure pages are shared with integration

### **Connection refused**

- Check if container is running: `docker ps`
- Verify port mapping
- Check firewall rules

## 🔄 Updates

### **Updating the Server**

```bash
# Pull latest image
docker pull ankitmalik84/notion-mcp-server:latest

# Restart with new image
docker-compose up -d --force-recreate
```

### **Migration Notes**

- Environment variables are backward compatible
- Parent page discovery is automatic
- No manual migration required

---

## 📞 Support

If you encounter issues:

1. Check the logs for error messages
2. Verify environment variables
3. Test Notion API connectivity
4. Review this configuration guide

Your production deployment is now ready! 🎉
