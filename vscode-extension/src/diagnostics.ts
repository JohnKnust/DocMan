import * as vscode from 'vscode';
import { ValidationResult, ValidationIssue, WorkspaceValidationResult } from './docmanProvider';

export class DiagnosticsManager {
    private diagnosticCollection: vscode.DiagnosticCollection;

    constructor() {
        this.diagnosticCollection = vscode.languages.createDiagnosticCollection('docman');
    }

    async updateDiagnostics(uri: vscode.Uri, result: ValidationResult): Promise<void> {
        const diagnostics: vscode.Diagnostic[] = [];

        for (const issue of result.issues) {
            const diagnostic = this.createDiagnostic(issue);
            diagnostics.push(diagnostic);
        }

        this.diagnosticCollection.set(uri, diagnostics);
    }

    async updateWorkspaceDiagnostics(result: WorkspaceValidationResult): Promise<void> {
        // Clear existing diagnostics
        this.diagnosticCollection.clear();

        // Update diagnostics for each file
        for (const [filePath, fileResult] of Object.entries(result.files)) {
            const uri = vscode.Uri.file(filePath);

            // Remove duplicates by creating a Set based on message content
            const uniqueIssues = fileResult.issues.filter((issue, index, self) =>
                index === self.findIndex(i => i.message === issue.message && i.type === issue.type)
            );

            const cleanResult = {
                ...fileResult,
                issues: uniqueIssues
            };

            await this.updateDiagnostics(uri, cleanResult);
        }
    }

    clearDiagnostics(uri?: vscode.Uri): void {
        if (uri) {
            this.diagnosticCollection.delete(uri);
        } else {
            this.diagnosticCollection.clear();
        }
    }

    private createDiagnostic(issue: ValidationIssue): vscode.Diagnostic {
        // Default range - start of file if no specific location
        let range = new vscode.Range(0, 0, 0, 0);

        // If line/column specified, use that
        if (issue.line !== undefined) {
            const line = Math.max(0, issue.line - 1); // Convert to 0-based
            const column = issue.column || 0;
            range = new vscode.Range(line, column, line, column + 10);
        }

        const diagnostic = new vscode.Diagnostic(
            range,
            issue.message,
            this.getSeverity(issue.severity)
        );

        diagnostic.source = 'DocMan';
        diagnostic.code = issue.type;

        // Add related information based on issue type
        switch (issue.type) {
            case 'missing_readme':
                diagnostic.relatedInformation = [
                    new vscode.DiagnosticRelatedInformation(
                        new vscode.Location(vscode.Uri.file(issue.file), range),
                        'Create a README.md file with proper metadata'
                    )
                ];
                break;
            case 'metadata_violation':
                diagnostic.relatedInformation = [
                    new vscode.DiagnosticRelatedInformation(
                        new vscode.Location(vscode.Uri.file(issue.file), range),
                        'Add required metadata: Status, Version, Last Updated'
                    )
                ];
                break;
            case 'broken_link':
                diagnostic.relatedInformation = [
                    new vscode.DiagnosticRelatedInformation(
                        new vscode.Location(vscode.Uri.file(issue.file), range),
                        'Fix or remove the broken link'
                    )
                ];
                break;
            case 'date_bump':
                diagnostic.relatedInformation = [
                    new vscode.DiagnosticRelatedInformation(
                        new vscode.Location(vscode.Uri.file(issue.file), range),
                        'Update the "Last Updated" date to reflect recent changes'
                    )
                ];
                break;
        }

        return diagnostic;
    }

    private getSeverity(severity: string): vscode.DiagnosticSeverity {
        switch (severity) {
            case 'error':
                return vscode.DiagnosticSeverity.Error;
            case 'warning':
                return vscode.DiagnosticSeverity.Warning;
            case 'info':
                return vscode.DiagnosticSeverity.Information;
            default:
                return vscode.DiagnosticSeverity.Warning;
        }
    }

    dispose(): void {
        this.diagnosticCollection.dispose();
    }
}
