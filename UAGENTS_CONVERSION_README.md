# UAgents Conversion - Healthcare System

This document describes the conversion of the healthcare agent system from a custom implementation to the uagents framework.

## Overview

The healthcare system has been completely converted to use the uagents library, which provides:
- Decentralized agent architecture
- Built-in message passing and communication
- Agent identity management
- Secure wallet operations
- Network connectivity

## Architecture Changes

### Before (Custom Implementation)
- Custom agent classes with manual message handling
- Custom wallet management with cryptography
- Manual agent coordination
- Custom communication protocols

### After (UAgents Framework)
- uagents Agent classes with built-in message handling
- uagents identity and wallet management
- Automatic agent coordination
- Standardized message protocols using Pydantic models

## New File Structure

```
agents/
├── protocols.py              # Message protocols using Pydantic models
├── uagents_master.py         # Master agent using uagents
├── uagents_healthcare.py     # Healthcare agent using uagents
├── uagents_sub.py           # Sub-agent implementation using uagents
├── uagents_wallet.py        # Wallet management for uagents
└── (legacy files remain for reference)

uagents_main.py              # Main entry point for uagents system
uagents_webhook.py           # Webhook server for uagents
uagents_demo.py              # Comprehensive demo script
test_uagents_conversion.py   # Test script for conversion
```

## Key Components

### 1. Message Protocols (`agents/protocols.py`)
Defines all communication messages using Pydantic models:
- `DoctorQuery` - Doctor query messages
- `VoiceData` - Voice data from webhooks
- `PatientRecord` - Patient information
- `ParsedCriteria` - Parsed query criteria
- `CommunicationResult` - Communication outcomes
- Various status and response messages

### 2. Master Agent (`agents/uagents_master.py`)
- Handles doctor queries
- Parses queries using LLM
- Queries database for patient data
- Creates and manages sub-agents
- Coordinates overall system workflow

### 3. Healthcare Agent (`agents/uagents_healthcare.py`)
- Processes voice data from webhooks
- Extracts patient information from transcripts
- Generates recommendations
- Handles real-time voice processing

### 4. Sub-Agents (`agents/uagents_sub.py`)
- Dynamic sub-agent creation for each patient
- Handles patient-specific communication
- Integrates with LiveKit for voice communication
- Makes intelligent decisions using Claude AI

### 5. Wallet Management (`agents/uagents_wallet.py`)
- Creates and manages agent identities
- Handles seed phrases and addresses
- Provides agent coordination utilities

## Usage

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Tests
```bash
python test_uagents_conversion.py
```

### 3. Run Demo
```bash
python uagents_demo.py
```

### 4. Start Full System
```bash
python uagents_main.py
```

### 5. Start Webhook Server
```bash
python uagents_webhook.py
```

## Configuration

The system uses the same configuration file (`config/agent_config.py`) but with additional uagents-specific settings:

```python
# uAgents settings
UAGENTS_SEED = os.getenv("UAGENTS_SEED", None)
UAGENTS_ENDPOINT = os.getenv("UAGENTS_ENDPOINT", None)
UAGENTS_MAILBOX_KEY = os.getenv("UAGENTS_MAILBOX_KEY", None)

# Agent addresses (generated automatically)
MASTER_AGENT_ADDRESS = os.getenv("MASTER_AGENT_ADDRESS", None)
HEALTHCARE_AGENT_ADDRESS = os.getenv("HEALTHCARE_AGENT_ADDRESS", None)
```

## Message Flow

1. **Doctor Query Flow**:
   ```
   Doctor → Master Agent → LLM Parsing → Database Query → Sub-Agent Creation → Patient Processing
   ```

2. **Voice Data Flow**:
   ```
   Webhook → Healthcare Agent → Transcript Analysis → Patient Lookup → Recommendation Generation
   ```

3. **Sub-Agent Communication**:
   ```
   Master Agent → Sub-Agent → LiveKit Session → Patient Communication → Decision Making → Result
   ```

## Benefits of UAgents Conversion

1. **Standardization**: Uses industry-standard agent framework
2. **Scalability**: Built-in support for distributed agents
3. **Security**: Integrated wallet and identity management
4. **Maintainability**: Cleaner code with better separation of concerns
5. **Extensibility**: Easy to add new agents and message types
6. **Network Ready**: Built-in support for agent-to-agent communication

## Migration Notes

### Breaking Changes
- Agent initialization now uses uagents Agent class
- Message handling uses Pydantic models instead of custom classes
- Wallet management uses uagents identity system
- Agent addresses are generated automatically

### Backward Compatibility
- Legacy agent files are preserved for reference
- Configuration structure remains mostly the same
- Database and service integrations unchanged

## Testing

The conversion includes comprehensive testing:

1. **Unit Tests**: Test individual components
2. **Integration Tests**: Test agent communication
3. **Demo Script**: Full system demonstration
4. **Webhook Tests**: Test external API integration

## Troubleshooting

### Common Issues

1. **Agent Creation Fails**: Check uagents seed and endpoint configuration
2. **Message Passing Errors**: Verify Pydantic model definitions
3. **Wallet Issues**: Ensure proper seed phrase configuration
4. **Network Connectivity**: Check uagents endpoint and mailbox settings

### Debug Mode

Enable debug logging:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

1. **Multi-Network Support**: Connect to different uagents networks
2. **Advanced Routing**: Implement sophisticated message routing
3. **Agent Discovery**: Add agent discovery and registration
4. **Load Balancing**: Distribute load across multiple agent instances
5. **Monitoring**: Add comprehensive agent monitoring and metrics

## Support

For issues related to the uagents conversion:
1. Check the test script output
2. Review the demo script for expected behavior
3. Check agent logs for error messages
4. Verify configuration settings

The conversion maintains all original functionality while providing a more robust and scalable foundation for the healthcare agent system.
