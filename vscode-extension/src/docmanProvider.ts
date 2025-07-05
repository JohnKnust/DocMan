import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { spawn } from 'child_process';
import { ConfigManager, DocManConfig } from './configManager';

export interface ValidationIssue {
    type: 'missing_readme' | 'metadata_violation' | 'broken_link' | 'date_bump' | 'index_entry';
    file: string;
    line?: number;
    column?: number;
    message: string;
    severity: 'error' | 'warning' | 'info';
}

export interface ValidationResult {
    success: boolean;
    issues: ValidationIssue[];
    summary?: string;
}

export interface WorkspaceValidationResult {
    success: boolean;
    files: { [filePath: string]: ValidationResult };
    totalIssues: number;
    summary: string;
}

export class DocManProvider {
    private configManager: ConfigManager;

    constructor(configManager: ConfigManager) {
        this.configManager = configManager;
    }

    async validateFile(filePath: string): Promise<ValidationResult> {
        try {
            const config = vscode.workspace.getConfiguration('docman');
            const pythonPath = config.get<string>('pythonPath', 'python');
            const cliPath = await this.getCliPath();

            // For single file validation, validate the parent directory but filter results
            const parentDir = path.dirname(filePath);
            const result = await this.runDocManCommand(pythonPath, cliPath, [parentDir, '--verbose']);

            // Parse and filter results for this specific file
            const workspaceResult = await this.parseWorkspaceValidationOutput(result, parentDir);

            // Filter issues to only include this specific file
            const fileName = path.basename(filePath);
            const fileIssues = Object.entries(workspaceResult.files)
                .filter(([filePath, _]) => filePath.endsWith(fileName))
                .reduce((issues, [_, fileResult]) => issues.concat(fileResult.issues), [] as any[]);

            return {
                success: fileIssues.length === 0,
                issues: fileIssues
            };
        } catch (error) {
            return {
                success: false,
                issues: [{
                    type: 'metadata_violation',
                    file: filePath,
                    message: `Validation failed: ${error}`,
                    severity: 'error'
                }]
            };
        }
    }

    async validateWorkspace(workspacePath: string): Promise<WorkspaceValidationResult> {
        try {
            const config = vscode.workspace.getConfiguration('docman');
            const pythonPath = config.get<string>('pythonPath', 'python');
            const cliPath = await this.getCliPath();

            const result = await this.runDocManCommand(pythonPath, cliPath, [workspacePath, '--verbose']);
            return await this.parseWorkspaceValidationOutput(result, workspacePath);
        } catch (error) {
            return {
                success: false,
                files: {},
                totalIssues: 1,
                summary: `Workspace validation failed: ${error}`
            };
        }
    }

    async updateIndex(workspacePath: string): Promise<void> {
        const config = vscode.workspace.getConfiguration('docman');
        const pythonPath = config.get<string>('pythonPath', 'python');
        const cliPath = await this.getCliPath();

        await this.runDocManCommand(pythonPath, cliPath, [workspacePath, '--fix']);
    }

    private async getCliPath(): Promise<string> {
        const config = vscode.workspace.getConfiguration('docman');
        let cliPath = config.get<string>('cliPath', './docman/cli.py');

        // If relative path, resolve relative to workspace root
        if (!path.isAbsolute(cliPath) && vscode.workspace.workspaceFolders) {
            const workspaceRoot = vscode.workspace.workspaceFolders[0].uri.fsPath;
            cliPath = path.resolve(workspaceRoot, cliPath);
        }

        // Check if CLI exists, if not try alternative locations
        if (!fs.existsSync(cliPath)) {
            const alternativePaths = await this.findCliAlternatives();
            if (alternativePaths.length > 0) {
                cliPath = alternativePaths[0];
                vscode.window.showInformationMessage(
                    `DocMan CLI found at: ${cliPath}. Consider updating your settings.`
                );
            } else {
                // Offer to help user install CLI
                await this.offerCliInstallation();
                throw new Error('DocMan CLI not found. Please install or configure the CLI path.');
            }
        }

        return cliPath;
    }

    async findCliAlternatives(): Promise<string[]> {
        if (!vscode.workspace.workspaceFolders) {return [];}

        const workspaceRoot = vscode.workspace.workspaceFolders[0].uri.fsPath;
        const alternatives = [
            // Current workspace
            path.join(workspaceRoot, 'docman', 'cli.py'),
            path.join(workspaceRoot, 'DocMan', 'docman', 'cli.py'),

            // Parent directory (submodule setup)
            path.join(path.dirname(workspaceRoot), 'DocMan', 'docman', 'cli.py'),
            path.join(path.dirname(workspaceRoot), 'docman', 'cli.py'),

            // Common installation locations
            path.join(workspaceRoot, 'tools', 'docman', 'cli.py'),
            path.join(workspaceRoot, 'scripts', 'docman', 'cli.py')
        ];

        return alternatives.filter(p => fs.existsSync(p));
    }

    async offerCliInstallation(): Promise<void> {
        const choice = await vscode.window.showErrorMessage(
            'DocMan CLI not found. Would you like help installing it?',
            'Install as Submodule',
            'Download Release',
            'Manual Setup',
            'Cancel'
        );

        switch (choice) {
            case 'Install as Submodule':
                await this.installAsSubmodule();
                break;
            case 'Download Release':
                await this.downloadRelease();
                break;
            case 'Manual Setup':
                await this.showManualSetup();
                break;
        }
    }

    private async installAsSubmodule(): Promise<void> {
        const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceRoot) {return;}

        const choice = await vscode.window.showInformationMessage(
            'Install DocMan as Git submodule? This will run: git submodule add https://github.com/your-repo/DocMan.git',
            'Install',
            'Cancel'
        );

        if (choice === 'Install') {
            const terminal = vscode.window.createTerminal('DocMan Installation');
            terminal.sendText('git submodule add https://github.com/your-repo/DocMan.git DocMan');
            terminal.sendText('git submodule update --init --recursive');
            terminal.show();

            vscode.window.showInformationMessage(
                'Installing DocMan as submodule. Check terminal for progress.'
            );
        }
    }

    private async downloadRelease(): Promise<void> {
        vscode.env.openExternal(vscode.Uri.parse('https://github.com/your-repo/DocMan/releases'));
        vscode.window.showInformationMessage(
            'Opening DocMan releases page. Download and extract to your project.'
        );
    }

    private async showManualSetup(): Promise<void> {
        const message = `Manual DocMan Setup:

1. Clone or download DocMan
2. Place in your project directory
3. Update VS Code setting: "docman.cliPath"
4. Ensure Python 3.11+ is installed

Example paths:
• ./DocMan/docman/cli.py
• ./tools/docman/cli.py
• /absolute/path/to/docman/cli.py`;

        vscode.window.showInformationMessage(message, 'Open Settings').then(choice => {
            if (choice === 'Open Settings') {
                vscode.commands.executeCommand('workbench.action.openSettings', 'docman.cliPath');
            }
        });
    }

    private async enhanceMetadataMessage(cleanMessage: string, originalMessage: string): Promise<string> {
        try {
            const config = await this.configManager.getDocManConfig();

            // Use CLI message as base, enhance with config-specific suggestions
            if (cleanMessage.includes('status') || originalMessage.includes('status')) {
                const validStatuses = config.valid_statuses || [];
                if (validStatuses.length > 0) {
                    return `Invalid status value. Valid options: ${validStatuses.join(', ')}`;
                } else {
                    return `Invalid status value - check .docmanrc for valid_statuses configuration`;
                }
            }

            if (cleanMessage.includes('version') || originalMessage.includes('version')) {
                const pattern = config.version_pattern || 'semantic';
                if (pattern === 'semantic') {
                    return 'Invalid version format - use semantic versioning (x.y.z)';
                } else {
                    return `Invalid version format - check .docmanrc for version requirements (pattern: ${pattern})`;
                }
            }

            if (cleanMessage.includes('date') || originalMessage.includes('date')) {
                const format = config.date_format || 'YYYY-MM-DD';
                return `Invalid date format - use ${format} format`;
            }

            if (cleanMessage.includes('metadata') || originalMessage.includes('metadata')) {
                const requiredFields = config.required_metadata || [];
                if (requiredFields.length > 0) {
                    return `Missing or invalid metadata. Required fields: ${requiredFields.join(', ')}`;
                } else {
                    return 'Missing or invalid metadata fields - check .docmanrc configuration';
                }
            }

            // Fallback: use original CLI message
            return cleanMessage || originalMessage;

        } catch (error) {
            // If config reading fails, use CLI message
            return cleanMessage || originalMessage;
        }
    }

    private runDocManCommand(pythonPath: string, cliPath: string, args: string[]): Promise<string> {
        return new Promise((resolve, reject) => {
            const command = spawn(pythonPath, [cliPath, ...args], {
                cwd: vscode.workspace.workspaceFolders?.[0]?.uri.fsPath
            });

            let stdout = '';
            let stderr = '';

            command.stdout.on('data', (data) => {
                stdout += data.toString();
            });

            command.stderr.on('data', (data) => {
                stderr += data.toString();
            });

            command.on('close', (code) => {
                if (code === 0 || code === 1) { // 0 = success, 1 = issues found
                    resolve(stdout);
                } else {
                    reject(new Error(`DocMan CLI failed with code ${code}: ${stderr}`));
                }
            });

            command.on('error', (error) => {
                reject(new Error(`Failed to spawn DocMan CLI: ${error.message}`));
            });
        });
    }

    private async parseValidationOutput(output: string, filePath: string): Promise<ValidationResult> {
        const issues: ValidationIssue[] = [];
        const lines = output.split('\n');
        let inSummarySection = false;
        let currentSection = '';

        for (const line of lines) {
            // Skip until we reach the summary section
            if (line.includes('DOCUMENTATION VALIDATION SUMMARY')) {
                inSummarySection = true;
                continue;
            }

            if (!inSummarySection) {continue;}

            // Detect sections in summary
            if (line.includes('Missing READMEs (')) {
                currentSection = 'missing_readme';
                continue;
            } else if (line.includes('Metadata violations (')) {
                currentSection = 'metadata_violation';
                continue;
            } else if (line.includes('Broken links (')) {
                currentSection = 'broken_link';
                continue;
            } else if (line.includes('Date inconsistencies (')) {
                currentSection = 'date_bump';
                continue;
            }

            // Parse individual issues (lines starting with •)
            if (line.trim().startsWith('•') && currentSection) {
                let message = line.replace(/^•\s*/, '').trim();
                const fileName = path.basename(filePath);

                // Skip issues that don't relate to this specific file
                if (currentSection === 'missing_readme') {
                    // Parse the missing README message to see if it's about this file's directory
                    const dirMatch = message.match(/Missing README:\s*(.+)/);
                    if (dirMatch) {
                        const dirName = dirMatch[1].trim();
                        // Only show if this file is actually the missing README
                        if (dirName !== '.' && dirName !== '' && fileName.toLowerCase().includes('readme')) {
                            message = `Missing README file in ${dirName} directory`;
                        } else {
                            // This file exists, it's not a "missing README" issue
                            continue;
                        }
                    } else {
                        continue; // Skip malformed missing README entries
                    }
                } else {
                    // For metadata violations, broken links, etc. - check if they mention this file
                    if (message.includes(fileName) || message.includes('in ' + fileName)) {
                        // Store original CLI message for hybrid approach
                        const originalMessage = message;

                        // Clean up the message to remove file reference
                        message = message.replace(/in\s+[^:]+\.md:\s*/, '').replace(/Bad metadata in [^:]+:\s*/, '');

                        // Enhance message with configuration-aware suggestions
                        if (currentSection === 'metadata_violation') {
                            message = await this.enhanceMetadataMessage(message, originalMessage);
                        }
                    } else {
                        continue; // Skip issues not related to this file
                    }
                }

                issues.push({
                    type: currentSection as any,
                    file: filePath,
                    message: message,
                    severity: currentSection === 'date_bump' ? 'info' :
                            currentSection === 'broken_link' ? 'warning' : 'error'
                });
            }
        }

        return {
            success: issues.length === 0,
            issues,
            summary: `Found ${issues.length} issue(s) in ${path.basename(filePath)}`
        };
    }

    private async parseWorkspaceValidationOutput(output: string, workspacePath: string): Promise<WorkspaceValidationResult> {
        const files: { [filePath: string]: ValidationResult } = {};
        const lines = output.split('\n');
        let totalIssues = 0;

        // Parse the structured output from DocMan CLI more precisely
        let currentSection = '';
        let inSummarySection = false;

        for (const line of lines) {
            // Skip until we reach the summary section
            if (line.includes('DOCUMENTATION VALIDATION SUMMARY')) {
                inSummarySection = true;
                continue;
            }

            if (!inSummarySection) {continue;}

            // Detect sections in summary
            if (line.includes('Missing READMEs (')) {
                currentSection = 'missing_readme';
                continue;
            } else if (line.includes('Metadata violations (')) {
                currentSection = 'metadata_violation';
                continue;
            } else if (line.includes('Broken links (')) {
                currentSection = 'broken_link';
                continue;
            } else if (line.includes('Date inconsistencies (')) {
                currentSection = 'date_bump';
                continue;
            }

            // Parse individual issues (lines starting with •)
            if (line.trim().startsWith('•') && currentSection) {
                totalIssues++;

                let fileName = '';
                let message = line.replace(/^•\s*/, '').trim();

                if (currentSection === 'missing_readme') {
                    // Extract directory name from "Missing README: dirname"
                    const dirMatch = message.match(/Missing README:\s*(.+)/);
                    if (dirMatch) {
                        const dirName = dirMatch[1].trim();
                        // Only create issues for actual missing READMEs in subdirectories
                        if (dirName !== '.' && dirName !== '' && !dirName.includes(path.basename(workspacePath))) {
                            fileName = path.join(dirName, 'README.md');
                            message = `Missing README file in ${dirName} directory`;
                        } else {
                            // Skip - this is about the current directory which has files
                            continue;
                        }
                    } else {
                        continue; // Skip malformed missing README entries
                    }
                } else {
                    // Extract filename from "in filename.md:" or "Bad metadata in filename.md:" patterns
                    const fileMatch = message.match(/(?:in|Bad metadata in)\s+([^:]+\.md):/);
                    if (fileMatch) {
                        fileName = fileMatch[1];

                        // Store original for hybrid approach
                        const originalMessage = message;

                        // Clean up the message and enhance with config
                        message = message.replace(/(?:in|Bad metadata in)\s+[^:]+\.md:\s*/, '');

                        if (currentSection === 'metadata_violation') {
                            message = await this.enhanceMetadataMessage(message, originalMessage);
                        }
                    }
                }

                if (fileName) {
                    const fullPath = path.join(workspacePath, fileName);

                    if (!files[fullPath]) {
                        files[fullPath] = {
                            success: false,
                            issues: []
                        };
                    }

                    files[fullPath].issues.push({
                        type: currentSection as any,
                        file: fullPath,
                        message: message,
                        severity: currentSection === 'date_bump' ? 'info' :
                                currentSection === 'broken_link' ? 'warning' : 'error'
                    });
                }
            }
        }

        return {
            success: totalIssues === 0,
            files,
            totalIssues,
            summary: `Workspace validation completed. Found ${totalIssues} issue(s) across ${Object.keys(files).length} file(s).`
        };
    }
}
