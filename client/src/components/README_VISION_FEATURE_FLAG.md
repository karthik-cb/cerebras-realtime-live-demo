# Voice-Only Application Feature Flags

## Overview

Feature flags have been implemented to disable camera/vision settings and conversation mode settings for voice-only applications, ensuring consistency with the Cerebras voice-based demo.

## Feature Flags

### 1. Vision/Camera Feature Flag
- **Name**: `VITE_DISABLE_VISION`
- **Values**: 
  - `"1"` - Disable vision/camera features (voice-only mode)
  - `undefined` or any other value - Enable vision features (default)

### 2. Conversation Mode Feature Flag
- **Name**: `VITE_DISABLE_CONVERSATION_MODES`
- **Values**: 
  - `"1"` - Disable conversation mode and interaction mode settings (voice-only mode)
  - `undefined` or any other value - Enable conversation mode settings (default)

### Usage
```bash
# Disable vision for voice-only application
VITE_DISABLE_VISION=1

# Disable conversation modes for voice-only application
VITE_DISABLE_CONVERSATION_MODES=1

# Enable all features (default behavior)
# VITE_DISABLE_VISION=1  # Comment out or remove
# VITE_DISABLE_CONVERSATION_MODES=1  # Comment out or remove
```

## Implementation Details

### 1. **ClientPage Component** (`ClientPage.tsx`)
- **Vision Detection**: `const visionEnabled = conversationType === "text-voice" && import.meta.env.VITE_DISABLE_VISION !== "1"`
- **Settings Component**: `<Settings vision={visionEnabled} />`
- **RTVIClient Configuration**: Uses `visionEnabled` for bot profile selection

### 2. **Settings Component** (`Settings.tsx`)
- **Vision Settings**: Camera settings only shown when `vision={true}`
- **Conversation Mode**: Hidden when `VITE_DISABLE_CONVERSATION_MODES=1`
- **Interaction Mode**: Hidden when `VITE_DISABLE_CONVERSATION_MODES=1`
- **Comments Added**: Clear indication that settings are conditionally rendered

### 3. **Environment Configuration**
- **env.example**: Added documentation for the feature flag
- **Build Process**: Feature flag is evaluated at build time

## Behavior

### When `VITE_DISABLE_VISION=1` and `VITE_DISABLE_CONVERSATION_MODES=1` (Voice-Only Mode)
- ✅ **Camera settings hidden** in Settings panel
- ✅ **Conversation mode dropdown hidden**
- ✅ **Interaction mode dropdown hidden**
- ✅ **No camera permissions requested**
- ✅ **Bot profile set to "voice-to-voice"** regardless of conversation type
- ✅ **Clean voice-only interface**

### When feature flags are not set (Default)
- ✅ **Camera settings shown** for text-voice conversations
- ✅ **Conversation mode dropdown available**
- ✅ **Interaction mode dropdown available**
- ✅ **Camera permissions requested** when needed
- ✅ **Bot profile respects conversation type**
- ✅ **Full multi-modal capabilities**

## Benefits

- ✅ **Consistency**: Voice-only application without confusing camera options
- ✅ **User Experience**: Cleaner settings interface for voice demos
- ✅ **Flexibility**: Easy to enable/disable vision features
- ✅ **Build-time Configuration**: No runtime overhead
- ✅ **Backward Compatibility**: Default behavior unchanged

## Configuration for Cerebras Demo

For the Cerebras voice-based demo, set:
```bash
VITE_DISABLE_VISION=1
VITE_DISABLE_CONVERSATION_MODES=1
```

This ensures:
- No camera settings in the Settings panel
- No conversation mode or interaction mode dropdowns
- Focus on voice interaction capabilities
- Clean, consistent user interface
- Proper showcase of Cerebras voice platform

## Technical Notes

- Feature flag is evaluated at build time using Vite's environment variable system
- No runtime performance impact
- Maintains all existing functionality when disabled
- Easy to toggle for different deployment scenarios
