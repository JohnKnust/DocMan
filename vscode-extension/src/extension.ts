import * as vscode from 'vscode';
import { DocManProvider } from './docmanProvider';
import { DiagnosticsManager } from './diagnostics';
import { DecorationsManager } from './decorations';
import { StatusBarManager } from './statusBar';
import { ConfigManager } from './configManager';
import { HoverProvider } from './hoverProvider';
import { CodeActionProvider } from './codeActionProvider';
import { FileWatcher } from './fileWatcher';

let docmanProvider: DocManProvider;
let diagnosticsManager: DiagnosticsManager;
let decorationsManager: DecorationsManager;
let statusBarManager: StatusBarManager;
let configManager: ConfigManager;
let hoverProvider: HoverProvider;
let codeActionProvider: CodeActionProvider;
let fileWatcher: FileWatcher;
let isDocManEnabled = false;

export async function activate(context: vscode.ExtensionContext) {
    console.log('DocMan extension is now active!');

    // Initialize managers
    configManager = new ConfigManager();
    docmanProvider = new DocManProvider(configManager);
    diagnosticsManager = new DiagnosticsManager();
    decorationsManager = new DecorationsManager();
    statusBarManager = new StatusBarManager();
    hoverProvider = new HoverProvider(docmanProvider);
    codeActionProvider = new CodeActionProvider(docmanProvider);
    fileWatcher = new FileWatcher(docmanProvider, diagnosticsManager, decorationsManager);

    // Check if DocMan should be enabled for this workspace
    const isEnabled = await checkAndPromptForActivation(context, configManager, statusBarManager);

    // Always register commands (including enable/disable)
    registerCommands(context, isEnabled);

    if (isEnabled) {
        // Register providers only if enabled
        registerProviders(context);

        // Initialize file watcher
        fileWatcher.initialize(context);

        statusBarManager.updateStatus('Ready');
    } else {
        statusBarManager.updateStatus('Disabled (click to enable)');
    }
}

function registerCommands(context: vscode.ExtensionContext, isEnabled: boolean) {
    // Validate Current File
    const validateCurrentFileCommand = vscode.commands.registerCommand('docman.validateCurrentFile', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('No active editor found');
            return;
        }

        // Check if current file is markdown
        if (editor.document.languageId !== 'markdown') {
            vscode.window.showWarningMessage('DocMan validation only works on Markdown files');
            return;
        }

        statusBarManager.updateStatus('Validating...');
        try {
            // Clear diagnostics for all files first to prevent cross-contamination
            diagnosticsManager.clearDiagnostics();

            const result = await docmanProvider.validateFile(editor.document.uri.fsPath);
            await diagnosticsManager.updateDiagnostics(editor.document.uri, result);
            await decorationsManager.updateDecorations(editor, result);

            const issueCount = result.issues?.length || 0;
            if (issueCount === 0) {
                vscode.window.showInformationMessage('✅ No documentation issues found');
                statusBarManager.updateStatus('✅ Valid');
            } else {
                vscode.window.showWarningMessage(`⚠️ Found ${issueCount} documentation issue(s)`);
                statusBarManager.updateStatus(`⚠️ ${issueCount} issues`);
            }
        } catch (error) {
            vscode.window.showErrorMessage(`DocMan validation failed: ${error}`);
            statusBarManager.updateStatus('❌ Error');
        }
    });

    // Validate Workspace
    const validateWorkspaceCommand = vscode.commands.registerCommand('docman.validateWorkspace', async () => {
        if (!vscode.workspace.workspaceFolders) {
            vscode.window.showWarningMessage('No workspace folder found');
            return;
        }

        statusBarManager.updateStatus('Validating workspace...');
        try {
            // Clear all existing diagnostics first
            diagnosticsManager.clearDiagnostics();

            const workspaceRoot = vscode.workspace.workspaceFolders[0].uri.fsPath;
            const result = await docmanProvider.validateWorkspace(workspaceRoot);

            // Update diagnostics for all files
            await diagnosticsManager.updateWorkspaceDiagnostics(result);

            const totalIssues = result.totalIssues || 0;
            const fileCount = Object.keys(result.files).length;

            if (totalIssues === 0) {
                vscode.window.showInformationMessage('✅ No documentation issues found in workspace');
                statusBarManager.updateStatus('✅ Workspace valid');
            } else {
                vscode.window.showWarningMessage(`⚠️ Found ${totalIssues} documentation issue(s) in ${fileCount} file(s)`);
                statusBarManager.updateStatus(`⚠️ ${totalIssues} workspace issues`);
            }
        } catch (error) {
            vscode.window.showErrorMessage(`DocMan workspace validation failed: ${error}`);
            statusBarManager.updateStatus('❌ Workspace error');
        }
    });

    // Update Index
    const updateIndexCommand = vscode.commands.registerCommand('docman.updateIndex', async () => {
        if (!vscode.workspace.workspaceFolders) {
            vscode.window.showWarningMessage('No workspace folder found');
            return;
        }

        statusBarManager.updateStatus('Updating index...');
        try {
            const workspaceRoot = vscode.workspace.workspaceFolders[0].uri.fsPath;
            await docmanProvider.updateIndex(workspaceRoot);
            vscode.window.showInformationMessage('✅ Documentation index updated successfully');
            statusBarManager.updateStatus('✅ Index updated');
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to update index: ${error}`);
            statusBarManager.updateStatus('❌ Index error');
        }
    });

    // Toggle Auto-validation
    const toggleAutoValidationCommand = vscode.commands.registerCommand('docman.toggleAutoValidation', async () => {
        const config = vscode.workspace.getConfiguration('docman');
        const currentValue = config.get<boolean>('autoValidateOnSave', true);
        await config.update('autoValidateOnSave', !currentValue, vscode.ConfigurationTarget.Workspace);
        
        const status = !currentValue ? 'enabled' : 'disabled';
        vscode.window.showInformationMessage(`Auto-validation ${status}`);
        statusBarManager.updateStatus(`Auto-validation ${status}`);
    });

    // Open Configuration
    const openConfigCommand = vscode.commands.registerCommand('docman.openConfig', async () => {
        try {
            const configPath = await configManager.findConfigFile();
            if (configPath) {
                const document = await vscode.workspace.openTextDocument(configPath);
                await vscode.window.showTextDocument(document);
            } else {
                const createConfig = await vscode.window.showInformationMessage(
                    'No .docmanrc configuration file found. Create one?',
                    'Create Config',
                    'Cancel'
                );
                if (createConfig === 'Create Config') {
                    await configManager.createConfigFile();
                }
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to open configuration: ${error}`);
        }
    });

    // Show Configuration Status
    const showConfigStatusCommand = vscode.commands.registerCommand('docman.showConfigStatus', async () => {
        const status = await configManager.getConfigStatus();
        vscode.window.showInformationMessage(status);
    });

    // Toggle DocMan Activation
    const toggleActivationCommand = vscode.commands.registerCommand('docman.toggleActivation', async () => {
        await toggleDocManActivation(context);
    });

    // Register all commands
    context.subscriptions.push(
        validateCurrentFileCommand,
        validateWorkspaceCommand,
        updateIndexCommand,
        toggleAutoValidationCommand,
        openConfigCommand,
        showConfigStatusCommand,
        toggleActivationCommand
    );
}

function registerProviders(context: vscode.ExtensionContext) {
    // Register hover provider for markdown files
    const hoverProviderDisposable = vscode.languages.registerHoverProvider(
        { scheme: 'file', language: 'markdown' },
        hoverProvider
    );

    // Register code action provider for markdown files
    const codeActionProviderDisposable = vscode.languages.registerCodeActionsProvider(
        { scheme: 'file', language: 'markdown' },
        codeActionProvider,
        {
            providedCodeActionKinds: [vscode.CodeActionKind.QuickFix]
        }
    );

    context.subscriptions.push(hoverProviderDisposable, codeActionProviderDisposable);
}

export function deactivate() {
    console.log('DocMan extension is now deactivated');

    // Clean up resources
    if (diagnosticsManager) {
        diagnosticsManager.dispose();
    }
    if (decorationsManager) {
        decorationsManager.dispose();
    }
    if (statusBarManager) {
        statusBarManager.dispose();
    }
    if (fileWatcher) {
        fileWatcher.dispose();
    }
}

async function checkAndPromptForActivation(
    context: vscode.ExtensionContext,
    configManager: ConfigManager,
    statusBarManager: StatusBarManager
): Promise<boolean> {
    if (!vscode.workspace.workspaceFolders) {
        return false;
    }

    const workspaceUri = vscode.workspace.workspaceFolders[0].uri;
    const workspaceState = context.workspaceState;

    // Check if user has already made a decision for this workspace
    const userDecision = workspaceState.get<string>(`docman.enabled.${workspaceUri.fsPath}`);
    if (userDecision === 'enabled') {
        isDocManEnabled = true;
        return true;
    } else if (userDecision === 'disabled') {
        isDocManEnabled = false;
        return false;
    }

    // Check if .docmanrc exists in workspace or parent directories
    const configPath = await configManager.findConfigFile();
    if (!configPath) {
        // No config found, offer to create one
        const choice = await vscode.window.showInformationMessage(
            'DocMan extension is installed but no configuration found. Would you like to create a .docmanrc configuration?',
            { modal: false },
            'Create Config',
            'Not now',
            'Never for this workspace'
        );

        switch (choice) {
            case 'Create Config':
                try {
                    await configManager.createConfigFile();
                    await workspaceState.update(`docman.enabled.${workspaceUri.fsPath}`, 'enabled');
                    isDocManEnabled = true;
                    vscode.window.showInformationMessage('✅ DocMan configuration created and enabled!');
                    return true;
                } catch (error) {
                    vscode.window.showErrorMessage(`Failed to create configuration: ${error}`);
                    isDocManEnabled = false;
                    return false;
                }
            case 'Never for this workspace':
                await workspaceState.update(`docman.enabled.${workspaceUri.fsPath}`, 'disabled');
                isDocManEnabled = false;
                return false;
            default: // 'Not now' or dismissed
                isDocManEnabled = false;
                return false;
        }
    }

    // Config found, prompt user to enable
    const choice = await vscode.window.showInformationMessage(
        'DocMan configuration detected. Enable documentation validation for this workspace?',
        { modal: false },
        'Enable',
        'Not now',
        'Never for this workspace'
    );

    switch (choice) {
        case 'Enable':
            await workspaceState.update(`docman.enabled.${workspaceUri.fsPath}`, 'enabled');
            isDocManEnabled = true;
            return true;
        case 'Never for this workspace':
            await workspaceState.update(`docman.enabled.${workspaceUri.fsPath}`, 'disabled');
            isDocManEnabled = false;
            return false;
        default: // 'Not now' or dismissed
            isDocManEnabled = false;
            return false;
    }
}

async function toggleDocManActivation(context: vscode.ExtensionContext): Promise<void> {
    if (!vscode.workspace.workspaceFolders) {
        vscode.window.showWarningMessage('No workspace folder found');
        return;
    }

    const workspaceUri = vscode.workspace.workspaceFolders[0].uri;
    const workspaceState = context.workspaceState;

    isDocManEnabled = !isDocManEnabled;

    if (isDocManEnabled) {
        await workspaceState.update(`docman.enabled.${workspaceUri.fsPath}`, 'enabled');

        // Re-register providers
        registerProviders(context);
        fileWatcher.initialize(context);

        statusBarManager.updateStatus('Ready');
        vscode.window.showInformationMessage('✅ DocMan enabled for this workspace');
    } else {
        await workspaceState.update(`docman.enabled.${workspaceUri.fsPath}`, 'disabled');

        // Clear diagnostics and decorations
        diagnosticsManager.clearDiagnostics();
        decorationsManager.dispose();
        fileWatcher.dispose();

        statusBarManager.updateStatus('Disabled (click to enable)');
        vscode.window.showInformationMessage('❌ DocMan disabled for this workspace');
    }
}
