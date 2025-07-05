import * as assert from 'assert';
import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';
import { ConfigManager } from '../../configManager';

suite('ConfigManager Test Suite', () => {
    let configManager: ConfigManager;
    let tempDir: string;

    setup(() => {
        configManager = new ConfigManager();
        tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'docman-test-'));
    });

    teardown(() => {
        // Clean up temp directory
        if (fs.existsSync(tempDir)) {
            fs.rmSync(tempDir, { recursive: true, force: true });
        }
    });

    test('Should find config file in workspace root', async () => {
        // Create a mock workspace
        const configPath = path.join(tempDir, '.docmanrc');
        fs.writeFileSync(configPath, 'root_directory = "."');

        // Mock workspace folders
        const originalWorkspaceFolders = vscode.workspace.workspaceFolders;
        Object.defineProperty(vscode.workspace, 'workspaceFolders', {
            value: [{ uri: vscode.Uri.file(tempDir) }],
            configurable: true
        });

        try {
            const foundPath = await configManager.findConfigFile();
            assert.strictEqual(foundPath, configPath);
        } finally {
            // Restore original workspace folders
            Object.defineProperty(vscode.workspace, 'workspaceFolders', {
                value: originalWorkspaceFolders,
                configurable: true
            });
        }
    });

    test('Should find template file when no config exists', async () => {
        // Create a template file
        const templatePath = path.join(tempDir, '.docmanrc.template');
        fs.writeFileSync(templatePath, '# Template config');

        // Mock workspace folders
        const originalWorkspaceFolders = vscode.workspace.workspaceFolders;
        Object.defineProperty(vscode.workspace, 'workspaceFolders', {
            value: [{ uri: vscode.Uri.file(tempDir) }],
            configurable: true
        });

        try {
            const foundPath = await configManager.findConfigFile();
            assert.strictEqual(foundPath, templatePath);
        } finally {
            // Restore original workspace folders
            Object.defineProperty(vscode.workspace, 'workspaceFolders', {
                value: originalWorkspaceFolders,
                configurable: true
            });
        }
    });

    test('Should return null when no config found', async () => {
        // Mock workspace folders with empty directory
        const originalWorkspaceFolders = vscode.workspace.workspaceFolders;
        Object.defineProperty(vscode.workspace, 'workspaceFolders', {
            value: [{ uri: vscode.Uri.file(tempDir) }],
            configurable: true
        });

        try {
            const foundPath = await configManager.findConfigFile();
            assert.strictEqual(foundPath, null);
        } finally {
            // Restore original workspace folders
            Object.defineProperty(vscode.workspace, 'workspaceFolders', {
                value: originalWorkspaceFolders,
                configurable: true
            });
        }
    });

    test('Should create config file with default content', async () => {
        // Mock workspace folders
        const originalWorkspaceFolders = vscode.workspace.workspaceFolders;
        Object.defineProperty(vscode.workspace, 'workspaceFolders', {
            value: [{ uri: vscode.Uri.file(tempDir) }],
            configurable: true
        });

        try {
            const createdPath = await configManager.createConfigFile();
            const expectedPath = path.join(tempDir, '.docmanrc');
            
            assert.strictEqual(createdPath, expectedPath);
            assert.ok(fs.existsSync(expectedPath));
            
            const content = fs.readFileSync(expectedPath, 'utf8');
            assert.ok(content.includes('root_directory = "."'));
            assert.ok(content.includes('DocMan Configuration'));
        } finally {
            // Restore original workspace folders
            Object.defineProperty(vscode.workspace, 'workspaceFolders', {
                value: originalWorkspaceFolders,
                configurable: true
            });
        }
    });

    test('Should provide config status', async () => {
        // Create a config file
        const configPath = path.join(tempDir, '.docmanrc');
        fs.writeFileSync(configPath, 'root_directory = "."');

        // Mock workspace folders
        const originalWorkspaceFolders = vscode.workspace.workspaceFolders;
        Object.defineProperty(vscode.workspace, 'workspaceFolders', {
            value: [{ uri: vscode.Uri.file(tempDir) }],
            configurable: true
        });

        try {
            const status = await configManager.getConfigStatus();
            assert.ok(status.includes('✅ DocMan configuration found'));
            assert.ok(status.includes(configPath));
        } finally {
            // Restore original workspace folders
            Object.defineProperty(vscode.workspace, 'workspaceFolders', {
                value: originalWorkspaceFolders,
                configurable: true
            });
        }
    });
});
