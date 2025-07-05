import * as vscode from 'vscode';
import { DocManProvider } from './docmanProvider';

export class CodeActionProvider implements vscode.CodeActionProvider {
    private docmanProvider: DocManProvider;

    constructor(docmanProvider: DocManProvider) {
        this.docmanProvider = docmanProvider;
    }

    async provideCodeActions(
        document: vscode.TextDocument,
        range: vscode.Range | vscode.Selection,
        context: vscode.CodeActionContext,
        token: vscode.CancellationToken
    ): Promise<vscode.CodeAction[]> {
        const actions: vscode.CodeAction[] = [];

        // Only provide actions for DocMan diagnostics
        const docmanDiagnostics = context.diagnostics.filter(
            diagnostic => diagnostic.source === 'DocMan'
        );

        if (docmanDiagnostics.length === 0) {
            return actions;
        }

        for (const diagnostic of docmanDiagnostics) {
            const codeActions = await this.createCodeActionsForDiagnostic(document, diagnostic);
            actions.push(...codeActions);
        }

        return actions;
    }

    private async createCodeActionsForDiagnostic(
        document: vscode.TextDocument,
        diagnostic: vscode.Diagnostic
    ): Promise<vscode.CodeAction[]> {
        const actions: vscode.CodeAction[] = [];

        switch (diagnostic.code) {
            case 'missing_readme':
                const readmeAction = await this.createDynamicReadmeAction(document);
                actions.push(readmeAction);
                break;
            case 'metadata_violation':
                // Create dynamic metadata action based on configuration
                const metadataAction = await this.createDynamicMetadataAction(document, diagnostic);
                actions.push(metadataAction);
                break;
            case 'date_bump':
                actions.push(this.createDateUpdateAction(document, diagnostic));
                break;
            case 'broken_link':
                actions.push(this.createLinkFixAction(document, diagnostic));
                break;
        }

        return actions;
    }

    private createReadmeAction(document: vscode.TextDocument): vscode.CodeAction {
        const action = new vscode.CodeAction(
            'Create README.md with DocMan metadata',
            vscode.CodeActionKind.QuickFix
        );

        const readmeTemplate = `# ${this.getDirectoryName(document.uri.fsPath)}

**Status**: 🚧 Draft  
**Version**: 0.1.0  
**Last Updated**: ${new Date().toISOString().split('T')[0]}

## Description

Add your description here.

## Usage

Add usage instructions here.
`;

        action.edit = new vscode.WorkspaceEdit();
        const readmeUri = vscode.Uri.file(document.uri.fsPath.replace(/[^/\\]*$/, 'README.md'));
        action.edit.createFile(readmeUri, { ignoreIfExists: true });
        action.edit.insert(readmeUri, new vscode.Position(0, 0), readmeTemplate);

        action.diagnostics = []; // Will fix the diagnostic
        return action;
    }

    private async createDynamicReadmeAction(document: vscode.TextDocument): Promise<vscode.CodeAction> {
        // Import ConfigManager dynamically to avoid circular dependencies
        const { ConfigManager } = await import('./configManager');
        const configManager = new ConfigManager();
        const config = await configManager.getDocManConfig();

        const action = new vscode.CodeAction(
            'Create README.md with dynamic DocMan metadata',
            vscode.CodeActionKind.QuickFix
        );

        const requiredFields = config.required_metadata || ['Status', 'Version', 'Last Updated'];
        const validStatuses = config.valid_statuses || ['🚧 Draft'];
        const defaultStatus = validStatuses[0] || '🚧 Draft';

        // Build dynamic metadata section
        let metadataSection = '';
        for (const field of requiredFields) {
            if (field === 'Status') {
                metadataSection += `**${field}**: ${defaultStatus}  \n`;
            } else if (field === 'Version') {
                metadataSection += `**${field}**: 0.1.0  \n`;
            } else if (field === 'Last Updated') {
                metadataSection += `**${field}**: ${new Date().toISOString().split('T')[0]}  \n`;
            } else {
                // For custom fields, leave empty for user to fill
                metadataSection += `**${field}**:   \n`;
            }
        }

        const readmeTemplate = `# ${this.getDirectoryName(document.uri.fsPath)}

${metadataSection}
## Description

Add your description here.

## Usage

Add usage instructions here.
`;

        action.edit = new vscode.WorkspaceEdit();
        const readmeUri = vscode.Uri.file(document.uri.fsPath.replace(/[^/\\]*$/, 'README.md'));
        action.edit.createFile(readmeUri, { ignoreIfExists: true });
        action.edit.insert(readmeUri, new vscode.Position(0, 0), readmeTemplate);

        action.diagnostics = []; // Will fix the diagnostic
        return action;
    }

    private createMetadataAction(document: vscode.TextDocument, diagnostic: vscode.Diagnostic): vscode.CodeAction {
        const action = new vscode.CodeAction(
            'Add missing DocMan metadata',
            vscode.CodeActionKind.QuickFix
        );

        const text = document.getText();
        const lines = text.split('\n');
        
        // Find the first heading
        let insertLine = 0;
        for (let i = 0; i < lines.length; i++) {
            if (lines[i].startsWith('#')) {
                insertLine = i + 1;
                break;
            }
        }

        const metadata = `
**Status**: 🚧 Draft  
**Version**: 0.1.0  
**Last Updated**: ${new Date().toISOString().split('T')[0]}
`;

        action.edit = new vscode.WorkspaceEdit();
        action.edit.insert(document.uri, new vscode.Position(insertLine, 0), metadata);
        action.diagnostics = [diagnostic];

        return action;
    }

    private async createDynamicMetadataAction(document: vscode.TextDocument, diagnostic: vscode.Diagnostic): Promise<vscode.CodeAction> {
        // Import ConfigManager dynamically to avoid circular dependencies
        const { ConfigManager } = await import('./configManager');
        const configManager = new ConfigManager();
        const config = await configManager.getDocManConfig();

        // Determine what type of metadata issue this is
        const message = diagnostic.message.toLowerCase();

        if (message.includes('missing')) {
            // Handle missing metadata fields
            const action = new vscode.CodeAction(
                'Add missing metadata fields',
                vscode.CodeActionKind.QuickFix
            );

            const requiredFields = config.required_metadata || ['Status', 'Version', 'Last Updated'];
            const validStatuses = config.valid_statuses || ['🚧 Draft'];
            const defaultStatus = validStatuses[0] || '🚧 Draft';

            // Build dynamic metadata template
            let metadataTemplate = '\n';

            if (requiredFields.includes('Status')) {
                metadataTemplate += `**Status**: ${defaultStatus}  \n`;
            }
            if (requiredFields.includes('Version')) {
                metadataTemplate += `**Version**: 0.1.0  \n`;
            }
            if (requiredFields.includes('Last Updated')) {
                metadataTemplate += `**Last Updated**: ${new Date().toISOString().split('T')[0]}  \n`;
            }

            // Add any other required fields
            for (const field of requiredFields) {
                if (!['Status', 'Version', 'Last Updated'].includes(field)) {
                    metadataTemplate += `**${field}**: TODO  \n`;
                }
            }

            metadataTemplate += '\n';

            action.edit = new vscode.WorkspaceEdit();

            // Find insertion point after title
            const text = document.getText();
            const lines = text.split('\n');
            let insertLine = 1;
            for (let i = 0; i < lines.length; i++) {
                if (lines[i].startsWith('#')) {
                    insertLine = i + 1;
                    break;
                }
            }

            action.edit.insert(document.uri, new vscode.Position(insertLine, 0), metadataTemplate);
            action.diagnostics = [diagnostic];
            return action;

        } else if (message.includes('invalid status')) {
            // Handle invalid status values
            const action = new vscode.CodeAction(
                `Fix status value (valid options: ${config.valid_statuses?.join(', ') || 'see .docmanrc'})`,
                vscode.CodeActionKind.QuickFix
            );

            // Find and replace invalid status
            const text = document.getText();
            const statusMatch = text.match(/\*\*Status\*\*:\s*(.+)/);
            if (statusMatch && config.valid_statuses && config.valid_statuses.length > 0) {
                const range = document.getWordRangeAtPosition(
                    document.positionAt(text.indexOf(statusMatch[1])),
                    /[^\n\r]+/
                );
                if (range) {
                    action.edit = new vscode.WorkspaceEdit();
                    action.edit.replace(document.uri, range, config.valid_statuses[0]);
                }
            }

            action.diagnostics = [diagnostic];
            return action;

        } else {
            // Fallback to original action
            return this.createMetadataAction(document, diagnostic);
        }
    }

    private createDateUpdateAction(document: vscode.TextDocument, diagnostic: vscode.Diagnostic): vscode.CodeAction {
        const action = new vscode.CodeAction(
            'Update "Last Updated" date to today',
            vscode.CodeActionKind.QuickFix
        );

        const text = document.getText();
        const dateRegex = /(\*\*Last Updated\*\*:?\s*)([^\n]*)/;
        const match = text.match(dateRegex);

        if (match) {
            const newDate = new Date().toISOString().split('T')[0];
            const startPos = document.positionAt(text.indexOf(match[0]) + match[1].length);
            const endPos = document.positionAt(text.indexOf(match[0]) + match[0].length);

            action.edit = new vscode.WorkspaceEdit();
            action.edit.replace(document.uri, new vscode.Range(startPos, endPos), newDate);
            action.diagnostics = [diagnostic];
        }

        return action;
    }

    private createLinkFixAction(document: vscode.TextDocument, diagnostic: vscode.Diagnostic): vscode.CodeAction {
        const action = new vscode.CodeAction(
            'Remove broken link',
            vscode.CodeActionKind.QuickFix
        );

        // This is a simple implementation - in practice, you'd want to be more sophisticated
        action.edit = new vscode.WorkspaceEdit();
        action.edit.replace(document.uri, diagnostic.range, '[Link removed - was broken]');
        action.diagnostics = [diagnostic];

        return action;
    }

    private getDirectoryName(filePath: string): string {
        const parts = filePath.split(/[/\\]/);
        return parts[parts.length - 2] || 'Project';
    }
}
