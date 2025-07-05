import * as assert from 'assert';
import * as vscode from 'vscode';

suite('Extension Test Suite', () => {
    vscode.window.showInformationMessage('Start all tests.');

    test('Extension should be present', () => {
        assert.ok(vscode.extensions.getExtension('docman.docman-vscode'));
    });

    test('Extension should activate', async () => {
        const extension = vscode.extensions.getExtension('docman.docman-vscode');
        assert.ok(extension);
        
        if (!extension!.isActive) {
            await extension!.activate();
        }
        
        assert.ok(extension!.isActive);
    });

    test('Commands should be registered', async () => {
        const commands = await vscode.commands.getCommands(true);
        
        const expectedCommands = [
            'docman.validateCurrentFile',
            'docman.validateWorkspace',
            'docman.updateIndex',
            'docman.toggleAutoValidation',
            'docman.openConfig',
            'docman.showConfigStatus'
        ];

        for (const command of expectedCommands) {
            assert.ok(
                commands.includes(command),
                `Command ${command} should be registered`
            );
        }
    });

    test('Configuration should have default values', () => {
        const config = vscode.workspace.getConfiguration('docman');
        
        assert.strictEqual(config.get('autoValidateOnSave'), true);
        assert.strictEqual(config.get('pythonPath'), 'python');
        assert.strictEqual(config.get('cliPath'), './docman/cli.py');
        assert.strictEqual(config.get('showInlineDecorations'), true);
        assert.strictEqual(config.get('validationDelay'), 500);
        assert.strictEqual(config.get('enableStatusBar'), true);
        assert.strictEqual(config.get('enableHoverTooltips'), true);
    });
});
