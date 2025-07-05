import * as vscode from 'vscode';
import { ValidationResult, ValidationIssue } from './docmanProvider';

export class DecorationsManager {
    private errorDecorationType!: vscode.TextEditorDecorationType;
    private warningDecorationType!: vscode.TextEditorDecorationType;
    private infoDecorationType!: vscode.TextEditorDecorationType;

    constructor() {
        this.createDecorationTypes();
    }

    private createDecorationTypes(): void {
        // Error decoration (red)
        this.errorDecorationType = vscode.window.createTextEditorDecorationType({
            backgroundColor: new vscode.ThemeColor('errorBackground'),
            border: '1px solid',
            borderColor: new vscode.ThemeColor('errorBorder'),
            borderRadius: '3px',
            after: {
                contentText: ' ❌',
                color: new vscode.ThemeColor('errorForeground'),
                fontWeight: 'bold'
            },
            overviewRulerColor: new vscode.ThemeColor('errorForeground'),
            overviewRulerLane: vscode.OverviewRulerLane.Right
        });

        // Warning decoration (yellow)
        this.warningDecorationType = vscode.window.createTextEditorDecorationType({
            backgroundColor: new vscode.ThemeColor('warningBackground'),
            border: '1px solid',
            borderColor: new vscode.ThemeColor('warningBorder'),
            borderRadius: '3px',
            after: {
                contentText: ' ⚠️',
                color: new vscode.ThemeColor('warningForeground'),
                fontWeight: 'bold'
            },
            overviewRulerColor: new vscode.ThemeColor('warningForeground'),
            overviewRulerLane: vscode.OverviewRulerLane.Right
        });

        // Info decoration (blue)
        this.infoDecorationType = vscode.window.createTextEditorDecorationType({
            backgroundColor: new vscode.ThemeColor('infoBackground'),
            border: '1px solid',
            borderColor: new vscode.ThemeColor('infoBorder'),
            borderRadius: '3px',
            after: {
                contentText: ' ℹ️',
                color: new vscode.ThemeColor('infoForeground')
            },
            overviewRulerColor: new vscode.ThemeColor('infoForeground'),
            overviewRulerLane: vscode.OverviewRulerLane.Right
        });
    }

    async updateDecorations(editor: vscode.TextEditor, result: ValidationResult): Promise<void> {
        const config = vscode.workspace.getConfiguration('docman');
        const showDecorations = config.get<boolean>('showInlineDecorations', true);

        if (!showDecorations) {
            this.clearDecorations(editor);
            return;
        }

        const errorDecorations: vscode.DecorationOptions[] = [];
        const warningDecorations: vscode.DecorationOptions[] = [];
        const infoDecorations: vscode.DecorationOptions[] = [];

        for (const issue of result.issues) {
            const decoration = this.createDecoration(editor, issue);
            if (decoration) {
                switch (issue.severity) {
                    case 'error':
                        errorDecorations.push(decoration);
                        break;
                    case 'warning':
                        warningDecorations.push(decoration);
                        break;
                    case 'info':
                        infoDecorations.push(decoration);
                        break;
                }
            }
        }

        // Apply decorations
        editor.setDecorations(this.errorDecorationType, errorDecorations);
        editor.setDecorations(this.warningDecorationType, warningDecorations);
        editor.setDecorations(this.infoDecorationType, infoDecorations);
    }

    clearDecorations(editor: vscode.TextEditor): void {
        editor.setDecorations(this.errorDecorationType, []);
        editor.setDecorations(this.warningDecorationType, []);
        editor.setDecorations(this.infoDecorationType, []);
    }

    private createDecoration(editor: vscode.TextEditor, issue: ValidationIssue): vscode.DecorationOptions | null {
        let range: vscode.Range;

        if (issue.line !== undefined) {
            // Use specific line if provided
            const line = Math.max(0, issue.line - 1); // Convert to 0-based
            const column = issue.column || 0;
            range = new vscode.Range(line, column, line, column + 10);
        } else {
            // Try to find relevant content in the document
            range = this.findRelevantRange(editor, issue);
        }

        const hoverMessage = new vscode.MarkdownString();
        hoverMessage.appendMarkdown(`**DocMan ${issue.severity.toUpperCase()}**\n\n`);
        hoverMessage.appendMarkdown(`${issue.message}\n\n`);
        hoverMessage.appendMarkdown(`*Issue type: ${issue.type}*`);

        return {
            range,
            hoverMessage
        };
    }

    private findRelevantRange(editor: vscode.TextEditor, issue: ValidationIssue): vscode.Range {
        const document = editor.document;
        const text = document.getText();

        // Try to find relevant content based on issue type
        switch (issue.type) {
            case 'missing_readme':
                // Highlight the first line
                return new vscode.Range(0, 0, 0, Math.min(50, document.lineAt(0).text.length));

            case 'metadata_violation':
                // Look for metadata section or first few lines
                const metadataMatch = text.match(/\*\*Status\*\*|\*\*Version\*\*|\*\*Last Updated\*\*/);
                if (metadataMatch && metadataMatch.index !== undefined) {
                    const position = document.positionAt(metadataMatch.index);
                    return new vscode.Range(position, position.translate(0, 20));
                }
                // Default to first few lines
                return new vscode.Range(0, 0, Math.min(5, document.lineCount - 1), 0);

            case 'broken_link':
                // Look for markdown links
                const linkMatch = text.match(/\[.*?\]\(.*?\)/);
                if (linkMatch && linkMatch.index !== undefined) {
                    const startPos = document.positionAt(linkMatch.index);
                    const endPos = document.positionAt(linkMatch.index + linkMatch[0].length);
                    return new vscode.Range(startPos, endPos);
                }
                break;

            case 'date_bump':
                // Look for Last Updated field
                const dateMatch = text.match(/\*\*Last Updated\*\*:?\s*([^\n]*)/);
                if (dateMatch && dateMatch.index !== undefined) {
                    const startPos = document.positionAt(dateMatch.index);
                    const endPos = document.positionAt(dateMatch.index + dateMatch[0].length);
                    return new vscode.Range(startPos, endPos);
                }
                break;
        }

        // Default: highlight first line
        return new vscode.Range(0, 0, 0, Math.min(50, document.lineAt(0).text.length));
    }

    dispose(): void {
        this.errorDecorationType.dispose();
        this.warningDecorationType.dispose();
        this.infoDecorationType.dispose();
    }
}
