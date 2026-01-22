// Electron launcher script that clears ELECTRON_RUN_AS_NODE
const { spawn } = require('child_process');
const path = require('path');

// Get electron binary path
const electronPath = require('electron');

// Create environment without ELECTRON_RUN_AS_NODE
const env = { ...process.env };
delete env.ELECTRON_RUN_AS_NODE;

// Get the app path (current directory or specified argument)
const appPath = process.argv[2] || '.';

// Spawn electron with clean environment
const child = spawn(electronPath, [appPath], {
  env,
  stdio: 'inherit',
  shell: false
});

child.on('close', (code) => {
  process.exit(code);
});
