import * as vscode from 'vscode';

export class StatusBarManager {
    private statusBarItem: vscode.StatusBarItem;

    constructor() {
        this.statusBarItem = vscode.window.createStatusBarItem(
            vscode.StatusBarAlignment.Left,
            100
        );
        this.statusBarItem.command = 'docman.toggleActivation';
        this.statusBarItem.show();
        this.updateStatus('Initializing...');
    }

    updateStatus(status: string): void {
        const config = vscode.workspace.getConfiguration('docman');
        const enableStatusBar = config.get<boolean>('enableStatusBar', true);

        if (!enableStatusBar) {
            this.statusBarItem.hide();
            return;
        }

        this.statusBarItem.text = `$(book) DocMan: ${status}`;
        this.statusBarItem.tooltip = `DocMan Status: ${status}\nClick to toggle activation`;
        this.statusBarItem.show();
    }

    setError(message: string): void {
        this.statusBarItem.text = `$(error) DocMan: ${message}`;
        this.statusBarItem.tooltip = `DocMan Error: ${message}`;
        this.statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
    }

    setWarning(message: string): void {
        this.statusBarItem.text = `$(warning) DocMan: ${message}`;
        this.statusBarItem.tooltip = `DocMan Warning: ${message}`;
        this.statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
    }

    clearBackground(): void {
        this.statusBarItem.backgroundColor = undefined;
    }

    dispose(): void {
        this.statusBarItem.dispose();
    }
}
