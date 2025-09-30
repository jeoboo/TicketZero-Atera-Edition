# Changelog

All notable changes to TicketZero AI - Atera Edition will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-01-30

### Added
- **3-Day Trial License System** - Free trial for evaluation
  - Hardware-locked trials using machine fingerprinting
  - Encrypted trial data storage in multiple locations
  - Tamper detection with checksums
  - Clock manipulation prevention
  - Auto-expiration after 3 days
  - Interactive trial activation flow
  - Clear purchase options after trial expires
- New example script: `apps/main/ticketzero_with_trial.py` showing trial integration
- Trial license module with comprehensive documentation
- `trial_license/` package with all trial management code

### Security Features (Trial System)
- CPU, disk, and MAC address fingerprinting
- AES encryption for trial data
- Multi-location redundant storage (3 hidden locations)
- Prevents common bypass attempts (file deletion, clock changes, reinstalling)
- No hosting infrastructure required - fully local

### Documentation
- Added trial system README with usage examples
- Updated main README with trial information
- Added trial requirements (cryptography package)

## [1.0.0] - 2025-01-30

### Added
- Initial portfolio release of TicketZero AI - Atera Edition
- Automated support ticket resolution for Atera RMM
- Multi-LLM provider support (Azure OpenAI, OpenAI, LM Studio)
- Multi-tenant MSP support
- Real-time monitoring dashboard
- Enterprise integrations:
  - Azure Graph API for Microsoft 365 operations
  - TeamViewer/AnyDesk remote support
  - GoTo Admin integration
  - GoTo VoIP integration
  - Opera PMS connector
- Health monitoring and alerting
- Comprehensive test suite
- Docker deployment support
- Example workflows and demos
- License management system
- API validation and error handling
- Cost tracking and analytics
- SLA monitoring capabilities

### Core Components
- `apps/main/ticketzero_atera_workflow.py` - Standard workflow
- `src/production/msp_ticketzero_optimized.py` - MSP multi-tenant version
- `src/production/msp_dashboard.py` - Real-time dashboard
- Multiple enterprise connectors
- Comprehensive utilities and testing modules

### Documentation
- Complete README with quick start guide
- Architecture documentation
- Integration examples
- Configuration guides
- Testing instructions

### License
- Portfolio demonstration version
- Commercial use requires licensing
- Contact: jgreenia@jandraisolutions.com

[1.1.0]: https://github.com/Turtles-AI-Lab/TicketZero-Atera-Edition/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/Turtles-AI-Lab/TicketZero-Atera-Edition/releases/tag/v1.0.0
