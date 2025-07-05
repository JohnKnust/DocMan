import * as vscode from 'vscode';
import { DocManProvider } from './docmanProvider';
import { DiagnosticsManager } from './diagnostics';
import { DecorationsManager } from './decorations';

export class FileWatcher {
    private docmanProvider: DocManProvider;
    private diagnosticsManager: DiagnosticsManager;
    private decorationsManager: DecorationsManager;
    private fileWatcher?: vscode.FileSystemWatcher;
    private validationTimeouts: Map<string, NodeJS.Timeout> = new Map();

    constructor(
        docmanProvider: DocManProvider,
        diagnosticsManager: DiagnosticsManager,
        decorationsManager: DecorationsManager
    ) {
        this.docmanProvider = docmanProvider;
        this.diagnosticsManager = diagnosticsManager;
        this.decorationsManager = decorationsManager;
    }

    initialize(context: vscode.ExtensionContext): void {
        // Watch for markdown file changes
        this.fileWatcher = vscode.workspace.createFileSystemWatcher('**/*.md');
        
        this.fileWatcher.onDidChange(this.onFileChanged.bind(this));
        this.fileWatcher.onDidCreate(this.onFileCreated.bind(this));
        this.fileWatcher.onDidDelete(this.onFileDeleted.bind(this));

        // Watch for document saves
        const saveListener = vscode.workspace.onDidSaveTextDocument(this.onDocumentSaved.bind(this));

        // Watch for active editor changes
        const editorChangeListener = vscode.window.onDidChangeActiveTextEditor(this.onActiveEditorChanged.bind(this));

        // Watch for configuration changes
        const configChangeListener = vscode.workspace.onDidChangeConfiguration(this.onConfigurationChanged.bind(this));

        context.subscriptions.push(
            this.fileWatcher,
            saveListener,
            editorChangeListener,
            configChangeListener
        );
    }

    private async onFileChanged(uri: vscode.Uri): Promise<void> {
        if (!this.shouldValidateFile(uri)) {
            return;
        }

        const config = vscode.workspace.getConfiguration('docman');
        const delay = config.get<number>('validationDelay', 500);

        // Debounce validation
        const filePath = uri.fsPath;
        const existingTimeout = this.validationTimeouts.get(filePath);
        if (existingTimeout) {
            clearTimeout(existingTimeout);
        }

        const timeout = setTimeout(async () => {
            await this.validateFile(uri);
            this.validationTimeouts.delete(filePath);
        }, delay);

        this.validationTimeouts.set(filePath, timeout);
    }

    private async onFileCreated(uri: vscode.Uri): Promise<void> {
        if (this.shouldValidateFile(uri)) {
            // Small delay to ensure file is fully written
            setTimeout(() => this.validateFile(uri), 100);
        }
    }

    private async onFileDeleted(uri: vscode.Uri): Promise<void> {
        // Clear diagnostics for deleted file
        this.diagnosticsManager.clearDiagnostics(uri);
        
        // Clear any pending validation
        const filePath = uri.fsPath;
        const existingTimeout = this.validationTimeouts.get(filePath);
        if (existingTimeout) {
            clearTimeout(existingTimeout);
            this.validationTimeouts.delete(filePath);
        }
    }

    private async onDocumentSaved(document: vscode.TextDocument): Promise<void> {
        const config = vscode.workspace.getConfiguration('docman');
        const autoValidateOnSave = config.get<boolean>('autoValidateOnSave', true);

        if (!autoValidateOnSave || !this.shouldValidateFile(document.uri) || document.languageId !== 'markdown') {
            return;
        }

        // Clear diagnostics for this specific file first
        this.diagnosticsManager.clearDiagnostics(document.uri);
        await this.validateFile(document.uri);
    }

    private async onActiveEditorChanged(editor: vscode.TextEditor | undefined): Promise<void> {
        if (!editor || !this.shouldValidateFile(editor.document.uri)) {
            return;
        }

        // Validate the newly opened file
        await this.validateFile(editor.document.uri);
    }

    private async onConfigurationChanged(event: vscode.ConfigurationChangeEvent): Promise<void> {
        if (event.affectsConfiguration('docman')) {
            // Re-validate all open markdown files when configuration changes
            const editors = vscode.window.visibleTextEditors;
            for (const editor of editors) {
                if (this.shouldValidateFile(editor.document.uri)) {
                    await this.validateFile(editor.document.uri);
                }
            }
        }
    }

    private shouldValidateFile(uri: vscode.Uri): boolean {
        // Only validate markdown files
        if (!uri.fsPath.endsWith('.md')) {
            return false;
        }

        // Skip files in ignored directories
        const ignoredPatterns = [
            'node_modules',
            '.git',
            '.vscode',
            '__pycache__',
            'venv',
            '.pytest_cache'
        ];

        const filePath = uri.fsPath.toLowerCase();
        return !ignoredPatterns.some(pattern => filePath.includes(pattern));
    }

    private async validateFile(uri: vscode.Uri): Promise<void> {
        try {
            const result = await this.docmanProvider.validateFile(uri.fsPath);
            
            // Update diagnostics
            await this.diagnosticsManager.updateDiagnostics(uri, result);

            // Update decorations for active editor
            const activeEditor = vscode.window.activeTextEditor;
            if (activeEditor && activeEditor.document.uri.fsPath === uri.fsPath) {
                await this.decorationsManager.updateDecorations(activeEditor, result);
            }
        } catch (error) {
            console.error(`Failed to validate file ${uri.fsPath}:`, error);
        }
    }

    dispose(): void {
        // Clear all pending timeouts
        for (const timeout of this.validationTimeouts.values()) {
            clearTimeout(timeout);
        }
        this.validationTimeouts.clear();

        if (this.fileWatcher) {
            this.fileWatcher.dispose();
        }
    }
}
