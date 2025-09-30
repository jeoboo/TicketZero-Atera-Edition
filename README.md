# TicketZero AI - Atera Edition
### AI-Powered Automated Support Ticket Resolution

> **📋 Portfolio Project** | This repository showcases the architecture and capabilities of TicketZero AI.
>
> **🔒 Commercial Product** | Full production version available for licensing. Contact us for enterprise deployment.

## Overview
TicketZero AI is an intelligent automated support ticket resolution system that integrates with the Atera RMM platform. Using advanced AI/LLM technology, it autonomously processes, analyzes, and resolves common IT support tickets, dramatically reducing response times and operational costs for MSPs and IT teams.

## Core Components

### Main Applications
- `apps/main/ticketzero_atera_workflow.py` - Standard Atera workflow implementation
- `src/production/msp_ticketzero_optimized.py` - MSP optimized version for multi-tenant use
- `src/production/msp_dashboard.py` - Real-time monitoring dashboard

### Integration Connectors
- `src/production/azure_graph_integration.py` - Azure AD enterprise integration (users, devices, security, compliance)
- `src/production/remote_support_connector.py` - TeamViewer/AnyDesk integration
- `src/production/goto_admin_connector.py` - GoTo Admin integration
- `src/production/goto_voip_connector.py` - GoTo VoIP integration
- `src/production/opera_pms_connector.py` - Opera PMS integration
- `src/production/universal_ticketzero_system.py` - Universal system handler

### Demo & Examples
- `demo/demo_live_ticket_resolution.py` - Live ticket resolution demonstration
- `demo/test_azure_graph.py` - Azure Graph API enterprise integration test

### Utilities & Testing
- `src/utils/api_validator.py` - API response validation and error handling
- `src/production/health_monitor.py` - System health monitoring
- `src/tests/test_admin_panel.py` - Admin panel functionality tests
- `src/tests/test_license_system.py` - License system validation tests
- `src/tests/test_api_validation.py` - Comprehensive API validation test suite

## Quick Start

### Standard Workflow
```bash
# Set your Atera API key
export ATERA_API_KEY=your_atera_api_key_here

# Run the main workflow
python apps/main/ticketzero_atera_workflow.py
```

### MSP Multi-Tenant Setup
```bash
# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run MSP system
python src/production/msp_ticketzero_optimized.py
```

### Docker Deployment
```bash
# Build and run
docker-compose up -d
```

## Configuration

### Environment Variables
- `ATERA_API_KEY` - Your Atera API key
- `AZURE_OPENAI_API_KEY` - Azure OpenAI API key (optional)
- `OPENAI_API_KEY` - OpenAI API key (optional)
- `LMSTUDIO_URL` - Local LM Studio URL (default: http://127.0.0.1:1234/v1)

### Testing Configuration
- `.env.testing` - Clean testing environment with working Atera API key and optional integrations commented out

### MSP Client Configuration
Configure multiple clients via environment variables or the web dashboard admin panel.

## Features
- Automated ticket processing with AI
- Multi-LLM provider support (LM Studio, Azure OpenAI, OpenAI)
- Real-time dashboard and monitoring
- Multi-tenant MSP support
- Integration with remote support tools
- Health monitoring and alerting

## Testing

### Run Tests
```bash
# Test admin panel functionality
python src/tests/test_admin_panel.py

# Test license system
python src/tests/test_license_system.py

# Test API validation and error handling
python src/tests/test_api_validation.py
```

### Run Demo
```bash
# Copy testing environment
cp .env.testing .env

# Run live ticket resolution demo
python demo/demo_live_ticket_resolution.py

# Test Azure Graph API enterprise integration
python demo/test_azure_graph.py
```

## Requirements
- Python 3.8+
- requests>=2.31.0
- aiohttp>=3.8.0 (for MSP version)
- python-dotenv>=1.0.0
- reportlab>=4.0.0 (for PDF generation)
- fpdf2>=2.7.0 (for advanced PDF features)

---

## 🚀 Commercial Licensing & Deployment

This repository contains a **demonstration version** showcasing the architecture and capabilities of TicketZero AI.

### Production Features (Commercial Version)
- ✅ Full multi-tenant MSP support
- ✅ Enterprise-grade security and compliance
- ✅ Priority support and SLA guarantees
- ✅ Custom integration development
- ✅ White-label options available
- ✅ Dedicated deployment assistance
- ✅ Ongoing updates and maintenance

### Contact for Licensing
**Turtles AI Lab**
📧 Email: jgreenia@jandraisolutions.com
🌐 GitHub: [Turtles-AI-Lab](https://github.com/Turtles-AI-Lab)

### Demo Request
Interested in seeing TicketZero AI in action? Contact us to schedule a live demonstration with your Atera environment.

---

## 📄 License
This code is provided for **portfolio and evaluation purposes only**. Commercial use requires a valid license agreement.

© 2025 Turtles AI Lab. All rights reserved.