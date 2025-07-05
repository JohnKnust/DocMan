import * as vscode from 'vscode';
import { DocManProvider } from './docmanProvider';

export class HoverProvider implements vscode.HoverProvider {
    private docmanProvider: DocManProvider;

    constructor(docmanProvider: DocManProvider) {
        this.docmanProvider = docmanProvider;
    }

    async provideHover(
        document: vscode.TextDocument,
        position: vscode.Position,
        token: vscode.CancellationToken
    ): Promise<vscode.Hover | null> {
        const config = vscode.workspace.getConfiguration('docman');
        const enableHoverTooltips = config.get<boolean>('enableHoverTooltips', true);

        if (!enableHoverTooltips || document.languageId !== 'markdown') {
            return null;
        }

        const line = document.lineAt(position);
        const lineText = line.text;

        // Check if hovering over metadata
        if (this.isMetadataLine(lineText)) {
            return this.createMetadataHover(lineText);
        }

        // Check if hovering over a link
        const linkMatch = this.getLinkAtPosition(lineText, position.character);
        if (linkMatch) {
            return this.createLinkHover(linkMatch);
        }

        // Check if hovering over status indicators
        const statusMatch = this.getStatusAtPosition(lineText, position.character);
        if (statusMatch) {
            return this.createStatusHover(statusMatch);
        }

        return null;
    }

    private isMetadataLine(lineText: string): boolean {
        return /\*\*(Status|Version|Last Updated)\*\*/.test(lineText);
    }

    private createMetadataHover(lineText: string): vscode.Hover {
        const hover = new vscode.MarkdownString();
        hover.isTrusted = true;

        if (lineText.includes('**Status**')) {
            hover.appendMarkdown('**DocMan Metadata: Status**\n\n');
            hover.appendMarkdown('Valid status values:\n');
            hover.appendMarkdown('- ✅ Production Ready\n');
            hover.appendMarkdown('- 🚧 Draft\n');
            hover.appendMarkdown('- 🚫 Deprecated\n');
            hover.appendMarkdown('- ⚠️ Experimental\n');
            hover.appendMarkdown('- 🔄 In Progress\n');
        } else if (lineText.includes('**Version**')) {
            hover.appendMarkdown('**DocMan Metadata: Version**\n\n');
            hover.appendMarkdown('Use semantic versioning (x.y.z)\n');
            hover.appendMarkdown('Examples: `1.0.0`, `2.1.3`, `0.1.0`');
        } else if (lineText.includes('**Last Updated**')) {
            hover.appendMarkdown('**DocMan Metadata: Last Updated**\n\n');
            hover.appendMarkdown('Use ISO date format (YYYY-MM-DD)\n');
            hover.appendMarkdown(`Example: \`${new Date().toISOString().split('T')[0]}\``);
        }

        return new vscode.Hover(hover);
    }

    private getLinkAtPosition(lineText: string, character: number): RegExpMatchArray | null {
        const linkRegex = /\[([^\]]*)\]\(([^)]*)\)/g;
        let match;

        while ((match = linkRegex.exec(lineText)) !== null) {
            const startPos = match.index!;
            const endPos = startPos + match[0].length;

            if (character >= startPos && character <= endPos) {
                return match;
            }
        }

        return null;
    }

    private createLinkHover(linkMatch: RegExpMatchArray): vscode.Hover {
        const linkText = linkMatch[1];
        const linkUrl = linkMatch[2];

        const hover = new vscode.MarkdownString();
        hover.isTrusted = true;
        hover.appendMarkdown('**DocMan Link Validation**\n\n');
        hover.appendMarkdown(`**Text:** ${linkText}\n`);
        hover.appendMarkdown(`**URL:** \`${linkUrl}\`\n\n`);

        if (linkUrl.startsWith('http')) {
            hover.appendMarkdown('🌐 External link - will be validated for accessibility');
        } else if (linkUrl.startsWith('./') || linkUrl.startsWith('../')) {
            hover.appendMarkdown('📁 Relative link - will be validated for file existence');
        } else if (linkUrl.startsWith('/')) {
            hover.appendMarkdown('📂 Absolute link - will be validated for file existence');
        } else {
            hover.appendMarkdown('🔗 Link will be validated by DocMan');
        }

        return new vscode.Hover(hover);
    }

    private getStatusAtPosition(lineText: string, character: number): string | null {
        const statusRegex = /(✅|🚧|🚫|⚠️|🔄)/g;
        let match;

        while ((match = statusRegex.exec(lineText)) !== null) {
            const startPos = match.index!;
            const endPos = startPos + match[0].length;

            if (character >= startPos && character <= endPos) {
                return match[1];
            }
        }

        return null;
    }

    private createStatusHover(status: string): vscode.Hover {
        const hover = new vscode.MarkdownString();
        hover.isTrusted = true;
        hover.appendMarkdown('**DocMan Status Indicator**\n\n');

        switch (status) {
            case '✅':
                hover.appendMarkdown('**Production Ready** - Stable and ready for use');
                break;
            case '🚧':
                hover.appendMarkdown('**Draft** - Work in progress, not ready for production');
                break;
            case '🚫':
                hover.appendMarkdown('**Deprecated** - No longer maintained, use alternatives');
                break;
            case '⚠️':
                hover.appendMarkdown('**Experimental** - Unstable, use with caution');
                break;
            case '🔄':
                hover.appendMarkdown('**In Progress** - Currently being developed or updated');
                break;
            default:
                hover.appendMarkdown('Status indicator recognized by DocMan');
        }

        return new vscode.Hover(hover);
    }
}
