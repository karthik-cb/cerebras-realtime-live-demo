# SSL Certificate Fix for macOS

## Problem
When running the TTS-LLM-STT pipeline on macOS, you may encounter SSL certificate verification errors:

```
WebSocketException in AbstractAsyncWebSocketClient.start: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1000)
AsyncListenWebSocketClient.start failed
ERROR | pipecat.services.deepgram.stt:_connect:236 - DeepgramSTTService#0: unable to connect to Deepgram
```

## Root Cause
macOS doesn't automatically provide SSL certificates to Python applications, causing SSL verification to fail when connecting to external services like Deepgram.

## Solution

### Step 1: Extract System Certificates
Run these commands to extract certificates from macOS keychains:

```bash
# Extract certificates from system keychains
security find-certificate -a -p /System/Library/Keychains/SystemRootCertificates.keychain > cacerts.pem
security find-certificate -a -p /Library/Keychains/System.keychain >> cacerts.pem
```

### Step 2: Move Certificate File
Move the generated certificate file to your home directory:

```bash
mv cacerts.pem ~/Library/cacerts.pem
```

### Step 3: Set Environment Variables
Export the environment variables to point Python to use these certificates:

```bash
export REQUESTS_CA_BUNDLE="$HOME/Library/cacerts.pem"
export SSL_CERT_FILE="$HOME/Library/cacerts.pem"
```

### Step 4: Make Environment Variables Persistent
Add these lines to your shell profile (e.g., `~/.zshrc` or `~/.bash_profile`):

```bash
# SSL Certificate configuration for Python
export REQUESTS_CA_BUNDLE="$HOME/Library/cacerts.pem"
export SSL_CERT_FILE="$HOME/Library/cacerts.pem"
```

Then reload your shell:
```bash
source ~/.zshrc  # or source ~/.bash_profile
```

## Alternative: Disable SSL Verification (Development Only)

If you're in a development environment and want to disable SSL verification entirely, you can set these environment variables:

```bash
export PYTHONHTTPSVERIFY=0
export CURL_CA_BUNDLE=""
export SSL_VERIFY=0
```

**⚠️ Warning: Only use this approach in development environments. Never disable SSL verification in production.**

## Verification

After applying the fix, restart your server and test the voice chat. You should see:

1. No more SSL certificate errors in the logs
2. Successful Deepgram STT connection
3. Complete TTS-LLM-STT pipeline working end-to-end

## Files Modified

- `server/bots/webrtc/bot_pipeline.py` - Updated to use proper SSL configuration
- Environment variables set for SSL certificate verification

## Related Issues

- [Pipecat Issue #869](https://github.com/pipecat-ai/pipecat/pull/869) - Language enum fix for Deepgram STT
- [Pipecat Issue #868](https://github.com/pipecat-ai/pipecat/issues/868) - Deepgram WebSocket connection failure

## References

- [Python SSL Certificate Verification](https://docs.python.org/3/library/ssl.html)
- [macOS Security Framework](https://developer.apple.com/documentation/security)
- [Deepgram WebSocket API](https://developers.deepgram.com/reference/streaming-api)
