import * as assert from 'assert';
import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';
import { DocManProvider } from '../../docmanProvider';
import { ConfigManager } from '../../configManager';

suite('DocManProvider Test Suite', () => {
    let docmanProvider: DocManProvider;
    let configManager: ConfigManager;
    let tempDir: string;

    setup(() => {
        configManager = new ConfigManager();
        docmanProvider = new DocManProvider(configManager);
        tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'docman-test-'));
    });

    teardown(() => {
        // Clean up temp directory
        if (fs.existsSync(tempDir)) {
            fs.rmSync(tempDir, { recursive: true, force: true });
        }
    });

    test('Should handle validation result parsing', async () => {
        // Create a test markdown file
        const testFile = path.join(tempDir, 'test.md');
        fs.writeFileSync(testFile, '# Test\n\nSome content');

        // Mock the CLI execution to return a known output
        const originalSpawn = require('child_process').spawn;
        require('child_process').spawn = () => {
            const mockProcess = {
                stdout: {
                    on: (event: string, callback: Function) => {
                        if (event === 'data') {
                            callback('Missing README in directory\nInvalid metadata in file\n');
                        }
                    }
                },
                stderr: {
                    on: (event: string, callback: Function) => {
                        // No stderr
                    }
                },
                on: (event: string, callback: Function) => {
                    if (event === 'close') {
                        callback(1); // Exit code 1 (issues found)
                    }
                }
            };
            return mockProcess;
        };

        try {
            const result = await docmanProvider.validateFile(testFile);
            
            assert.ok(result);
            assert.strictEqual(result.success, false);
            assert.ok(result.issues.length > 0);
            
            // Check that issues were parsed correctly
            const hasReadmeIssue = result.issues.some(issue => 
                issue.type === 'missing_readme'
            );
            const hasMetadataIssue = result.issues.some(issue => 
                issue.type === 'metadata_violation'
            );
            
            assert.ok(hasReadmeIssue || hasMetadataIssue);
        } finally {
            // Restore original spawn
            require('child_process').spawn = originalSpawn;
        }
    });

    test('Should handle CLI errors gracefully', async () => {
        const testFile = path.join(tempDir, 'test.md');
        fs.writeFileSync(testFile, '# Test');

        // Mock spawn to simulate CLI error
        const originalSpawn = require('child_process').spawn;
        require('child_process').spawn = () => {
            const mockProcess = {
                stdout: {
                    on: (event: string, callback: Function) => {
                        // No stdout
                    }
                },
                stderr: {
                    on: (event: string, callback: Function) => {
                        if (event === 'data') {
                            callback('CLI Error occurred');
                        }
                    }
                },
                on: (event: string, callback: Function) => {
                    if (event === 'close') {
                        callback(2); // Exit code 2 (error)
                    }
                }
            };
            return mockProcess;
        };

        try {
            const result = await docmanProvider.validateFile(testFile);
            
            assert.ok(result);
            assert.strictEqual(result.success, false);
            assert.ok(result.issues.length > 0);
            assert.strictEqual(result.issues[0].severity, 'error');
        } finally {
            // Restore original spawn
            require('child_process').spawn = originalSpawn;
        }
    });

    test('Should parse successful validation', async () => {
        const testFile = path.join(tempDir, 'test.md');
        fs.writeFileSync(testFile, '# Test\n\n**Status**: ✅ Production Ready\n**Version**: 1.0.0\n**Last Updated**: 2025-07-02');

        // Mock successful CLI execution
        const originalSpawn = require('child_process').spawn;
        require('child_process').spawn = () => {
            const mockProcess = {
                stdout: {
                    on: (event: string, callback: Function) => {
                        if (event === 'data') {
                            callback('All documentation checks passed!\n');
                        }
                    }
                },
                stderr: {
                    on: (event: string, callback: Function) => {
                        // No stderr
                    }
                },
                on: (event: string, callback: Function) => {
                    if (event === 'close') {
                        callback(0); // Exit code 0 (success)
                    }
                }
            };
            return mockProcess;
        };

        try {
            const result = await docmanProvider.validateFile(testFile);
            
            assert.ok(result);
            assert.strictEqual(result.success, true);
            assert.strictEqual(result.issues.length, 0);
        } finally {
            // Restore original spawn
            require('child_process').spawn = originalSpawn;
        }
    });
});
