# Security Guidelines for Electron

## Mandatory Security Checks

Before ANY commit:
- [ ] No hardcoded secrets (API keys, passwords, tokens)
- [ ] All user inputs validated
- [ ] contextIsolation: true
- [ ] nodeIntegration: false (or properly sandboxed)
- [ ] No remote module usage
- [ ] IPC channels validated
- [ ] File paths sanitized
- [ ] Error messages don't leak sensitive data

## Electron Security Best Practices

### BrowserWindow Configuration
```typescript
// ALWAYS use these settings
const win = new BrowserWindow({
  webPreferences: {
    contextIsolation: true,      // REQUIRED
    nodeIntegration: false,      // REQUIRED
    sandbox: true,               // RECOMMENDED
    webSecurity: true,           // REQUIRED
    allowRunningInsecureContent: false
  }
})
```

### IPC Security
```typescript
// ALWAYS validate IPC input
ipcMain.handle('channel', async (event, data) => {
  // Validate data before processing
  if (!isValidInput(data)) {
    throw new Error('Invalid input')
  }
  // Process validated data
})
```

### Secret Management
```typescript
// NEVER: Hardcoded secrets
const apiKey = "sk-proj-xxxxx"

// ALWAYS: Environment variables
const apiKey = process.env.API_KEY

if (!apiKey) {
  throw new Error('API_KEY not configured')
}
```

## Security Response Protocol

If security issue found:
1. STOP immediately
2. Use **code-reviewer** agent
3. Fix CRITICAL issues before continuing
4. Rotate any exposed secrets
5. Review entire codebase for similar issues
