# Persona Configuration Guide

## Overview
The AI Voice Assistant now supports configurable personas! You can customize the AI's personality and response style by setting the `AGENT_PERSONA` environment variable.

## Available Personas

### Default Persona
- **Description**: Helpful AI assistant (default behavior)
- **Configuration**: Leave `AGENT_PERSONA` unset or set to empty

### Pirate Persona
- **Description**: Responds like a classic pirate with nautical terms and pirate slang
- **Configuration**: `AGENT_PERSONA="a friendly pirate who speaks with nautical terms and pirate slang like 'Arrr', 'matey', 'shiver me timbers', and 'yo ho ho'"`

### Cowboy Persona
- **Description**: Responds like an old west cowboy with western slang
- **Configuration**: `AGENT_PERSONA="an old west cowboy who speaks with western slang like 'howdy partner', 'yeehaw', 'varmint', and 'rootin' tootin'"`

### Robot Persona
- **Description**: Responds like a logical robot with technical precision
- **Configuration**: `AGENT_PERSONA="a logical robot who speaks with technical precision, uses binary references, and says 'beep boop' occasionally"`

### Custom Personas
You can create your own personas by setting `AGENT_PERSONA` to any descriptive text:
```bash
AGENT_PERSONA="a Shakespearean actor who speaks in iambic pentameter"
AGENT_PERSONA="a wise old wizard who speaks in riddles and mystical terms"
AGENT_PERSONA="a cheerful kindergarten teacher who explains things simply"
```

## Configuration

### Environment Variable
Add this to your `.env` file:
```bash
# Optional: Set the AI persona (default: helpful AI assistant)
AGENT_PERSONA="your_persona_description_here"
```

### Examples
```bash
# Pirate persona
AGENT_PERSONA="a friendly pirate who speaks with nautical terms and pirate slang"

# Cowboy persona  
AGENT_PERSONA="an old west cowboy who speaks with western slang"

# Robot persona
AGENT_PERSONA="a logical robot who speaks with technical precision"

# Custom persona
AGENT_PERSONA="a Shakespearean actor who speaks in iambic pentameter"
```

## Backward Compatibility
- If `AGENT_PERSONA` is not set, the AI defaults to "helpful AI assistant" behavior
- All existing functionality remains unchanged
- Persona configuration only affects the LLM's response style, not other services

## Testing
After setting the persona, restart the application and test with questions like:
- "What's the weather like today?"
- "Tell me a story"
- "How does this work?"

The AI should respond in the chosen persona's style while maintaining helpfulness and accuracy.
