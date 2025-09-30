# 🔧 TicketZero AI - Admin Panel Guide

## **📋 Overview**

The TicketZero AI MSP Dashboard now includes a comprehensive **Admin Configuration Panel** that allows administrators to manage API keys, configure integrations, and monitor system status directly from the web interface.

## **🚀 Features Added**

### **✅ API Configuration Management**
- **Visual Interface**: Professional web-based configuration forms
- **Real-Time Validation**: Instant feedback on configuration issues
- **Secure Storage**: All settings saved directly to `.env` file
- **Multiple Providers**: Support for Atera, OpenAI, Azure OpenAI, LM Studio, and Email/SMTP

### **✅ System Integration**
- **Embedded in Dashboard**: No separate admin interface needed
- **Toggle Access**: Hidden admin panel with one-click access
- **Live Updates**: Configuration changes take effect immediately
- **Status Monitoring**: Real-time validation and health checks

## **🎯 How to Access**

### **Method 1: Through Dashboard**
1. **Start the MSP system**:
   ```bash
   python src/production/msp_ticketzero_optimized.py
   ```

2. **Open dashboard**: http://localhost:8080

3. **Click "Admin Panel"** button (top-right corner)

4. **Configure APIs** in the expanded admin interface

### **Method 2: Direct Admin URL**
- Access directly: http://localhost:8080/admin

## **🔧 Configuration Sections**

### **🎫 Atera RMM Integration**
- **API Key**: Your Atera API key for ticket processing
- **API URL**: Atera endpoint (default: https://app.atera.com/api/v3)
- **Test Connection**: Verify API connectivity

### **🤖 OpenAI Integration**
- **API Key**: OpenAI API key for AI processing
- **Model**: Model selection (default: gpt-3.5-turbo)
- **Test Connection**: Validate API access

### **☁️ Azure OpenAI Integration**
- **API Key**: Azure OpenAI service key
- **Endpoint**: Your Azure OpenAI resource URL
- **Deployment**: Model deployment name
- **Test Connection**: Check Azure connectivity

### **🏠 LM Studio Local AI**
- **Endpoint**: Local LM Studio server URL
- **Model**: Local model identifier
- **Test Connection**: Verify local service

### **📧 Email/SMTP Configuration**
- **SMTP Host**: Email server hostname
- **SMTP Port**: Server port (default: 587)
- **Username**: Email account username
- **Password**: Email account password/app password
- **Test Connection**: Send test email

## **💾 How Configuration Saving Works**

### **Backend Process**:
1. **Form Submission**: Admin fills out configuration forms
2. **Data Processing**: Server receives and validates form data
3. **Environment Update**: Configuration mapped to environment variables
4. **File Writing**: `.env` file updated with new values
5. **Validation**: System validates new configuration
6. **Confirmation**: Success/error feedback provided

### **Environment Variables Updated**:
```bash
# Atera Configuration
ATERA_API_KEY=your_actual_api_key
ATERA_API_URL=https://app.atera.com/api/v3

# OpenAI Configuration
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-3.5-turbo

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_azure_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-35-turbo

# LM Studio Configuration
LMSTUDIO_URL=http://127.0.0.1:1234/v1
LMSTUDIO_MODEL=phi-3-mini-4k-instruct

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-email-password
```

## **🛡️ Security Features**

### **✅ Secure Handling**
- **Password Fields**: Sensitive data masked in forms
- **Input Validation**: Server-side validation of all inputs
- **File Permissions**: Secure .env file handling
- **Error Handling**: Graceful error management

### **✅ Configuration Validation**
- **Required Fields**: Automatic detection of missing required settings
- **Format Validation**: URL and email format checking
- **Connection Testing**: API connectivity verification
- **Status Indicators**: Visual feedback on configuration health

## **📊 Admin Interface Tabs**

### **1. API Configuration**
- Complete form interface for all API providers
- Real-time validation and status indicators
- Save/Reset functionality
- Connection testing buttons

### **2. Client Management**
- Overview of configured MSP clients
- Client-specific settings (coming soon)
- Billing and SLA configuration (planned)

### **3. System Status**
- Environment file information
- Total variables count
- Last update timestamps
- System health indicators

## **🔄 Usage Workflow**

### **Initial Setup**:
1. **Access admin panel** via dashboard
2. **Configure required APIs** (at minimum: Atera API key)
3. **Test connections** to verify setup
4. **Save configuration** to persist settings
5. **Monitor status** for any issues

### **Ongoing Management**:
1. **Update API keys** when they expire
2. **Add new providers** as needed
3. **Test connections** periodically
4. **Monitor configuration health**

## **🚨 Troubleshooting**

### **Common Issues**:

**❌ Configuration Not Saving**
- Check file permissions on `.env` file
- Verify server has write access to directory
- Check browser console for JavaScript errors

**❌ API Connection Tests Failing**
- Verify API keys are valid and active
- Check network connectivity
- Confirm endpoint URLs are correct

**❌ Admin Panel Not Loading**
- Ensure MSP system is running
- Check http://localhost:8080 is accessible
- Verify no port conflicts

### **Debug Steps**:
1. **Check logs** in `ticketzero_msp.log`
2. **Verify .env file** contains updated values
3. **Test API endpoints** manually
4. **Restart MSP system** after major changes

## **📈 Advanced Features**

### **Coming Soon**:
- **Client Self-Service Portal**: Individual client configuration access
- **Role-Based Access Control**: Different admin permission levels
- **Configuration Backup/Restore**: Save and restore config snapshots
- **API Usage Analytics**: Track API calls and costs
- **Automated Health Checks**: Scheduled connection testing

## **💡 Best Practices**

### **✅ Configuration Management**:
- **Test before saving**: Always test connections before saving
- **Backup configurations**: Keep backup of working `.env` files
- **Monitor regularly**: Check admin panel for configuration issues
- **Use strong credentials**: Ensure API keys and passwords are secure

### **✅ Security**:
- **Limit admin access**: Control who can access admin panel
- **Regular key rotation**: Update API keys periodically
- **Monitor logs**: Watch for authentication failures
- **Secure environment**: Protect `.env` file with proper permissions

---

## **🎉 Admin Panel Ready!**

The TicketZero AI admin panel is now **fully functional** with:

✅ **Complete API configuration management**
✅ **Real-time .env file updates**
✅ **Professional web interface**
✅ **Security validation and testing**
✅ **Multi-provider support**

**Access it now**: Start the MSP system and click "Admin Panel" in the dashboard!