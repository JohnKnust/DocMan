import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

export interface DocManConfig {
    valid_statuses?: string[];
    required_metadata?: string[];
    version_pattern?: string;
    date_format?: string;
}

export class ConfigManager {
    private configFileName = '.docmanrc';
    private templateFileName = '.docmanrc.template';

    async findConfigFile(): Promise<string | null> {
        if (!vscode.workspace.workspaceFolders) {
            return null;
        }

        const workspaceRoot = vscode.workspace.workspaceFolders[0].uri.fsPath;
        
        // Search locations in order of preference
        const searchPaths = [
            path.join(workspaceRoot, this.configFileName),
            path.join(path.dirname(workspaceRoot), this.configFileName), // Parent directory
            path.join(workspaceRoot, 'docman', this.configFileName),
            path.join(workspaceRoot, this.templateFileName)
        ];

        for (const configPath of searchPaths) {
            if (fs.existsSync(configPath)) {
                return configPath;
            }
        }

        return null;
    }

    async createConfigFile(): Promise<string> {
        if (!vscode.workspace.workspaceFolders) {
            throw new Error('No workspace folder found');
        }

        const workspaceRoot = vscode.workspace.workspaceFolders[0].uri.fsPath;
        const configPath = path.join(workspaceRoot, this.configFileName);

        // Check if template exists
        const templatePath = path.join(workspaceRoot, this.templateFileName);
        let configContent = this.getDefaultConfig();

        if (fs.existsSync(templatePath)) {
            configContent = fs.readFileSync(templatePath, 'utf8');
        }

        fs.writeFileSync(configPath, configContent);
        
        // Open the created config file
        const document = await vscode.workspace.openTextDocument(configPath);
        await vscode.window.showTextDocument(document);

        return configPath;
    }

    async getConfigStatus(): Promise<string> {
        const configPath = await this.findConfigFile();
        
        if (!configPath) {
            return '❌ No DocMan configuration found. Use "DocMan: Open Configuration File" to create one.';
        }

        const isTemplate = configPath.endsWith(this.templateFileName);
        const isInParent = configPath.includes(path.sep + '..' + path.sep) || 
                          !configPath.startsWith(vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || '');

        let status = '✅ DocMan configuration found';
        
        if (isTemplate) {
            status += ' (using template - consider creating .docmanrc)';
        }
        
        if (isInParent) {
            status += ' (loaded from parent directory)';
        }

        status += `\n📁 Location: ${configPath}`;

        // Try to read and validate config
        try {
            const configContent = fs.readFileSync(configPath, 'utf8');
            const lines = configContent.split('\n').filter(line => 
                line.trim() && !line.trim().startsWith('#')
            );
            status += `\n📊 Configuration entries: ${lines.length}`;
        } catch (error) {
            status += `\n⚠️ Error reading config: ${error}`;
        }

        return status;
    }

    async getDocManConfig(): Promise<DocManConfig> {
        const configPath = await this.findConfigFile();
        if (!configPath) {
            return this.getDefaultDocManConfig();
        }

        try {
            const configContent = fs.readFileSync(configPath, 'utf8');
            return this.parseDocManConfig(configContent);
        } catch (error) {
            console.warn('Failed to parse .docmanrc, using defaults:', error);
            return this.getDefaultDocManConfig();
        }
    }

    private parseDocManConfig(content: string): DocManConfig {
        const config: DocManConfig = {};
        const lines = content.split('\n');

        let currentArray: string[] = [];
        let currentKey = '';
        let inArray = false;

        for (const line of lines) {
            const trimmed = line.trim();

            // Skip comments and empty lines
            if (!trimmed || trimmed.startsWith('#')) {
                continue;
            }

            // Handle array end
            if (inArray && trimmed === ']') {
                if (currentKey === 'valid_statuses') {
                    config.valid_statuses = currentArray;
                } else if (currentKey === 'required_metadata') {
                    config.required_metadata = currentArray;
                }
                inArray = false;
                currentArray = [];
                currentKey = '';
                continue;
            }

            // Handle array items
            if (inArray) {
                const match = trimmed.match(/^"([^"]*)"[,]?$/);
                if (match) {
                    currentArray.push(match[1]);
                }
                continue;
            }

            // Handle array start
            if (trimmed.includes('=') && trimmed.includes('[')) {
                const match = trimmed.match(/(\w+)\s*=\s*\[/);
                if (match) {
                    currentKey = match[1];
                    inArray = true;

                    // Check if it's a single line array
                    if (trimmed.includes(']')) {
                        const singleLineMatch = trimmed.match(/(\w+)\s*=\s*\[(.*?)\]/);
                        if (singleLineMatch) {
                            const values = singleLineMatch[2]
                                .split(',')
                                .map(v => v.replace(/[",]/g, '').trim())
                                .filter(v => v);

                            if (currentKey === 'valid_statuses') {
                                config.valid_statuses = values;
                            } else if (currentKey === 'required_metadata') {
                                config.required_metadata = values;
                            }
                            inArray = false;
                            currentArray = [];
                            currentKey = '';
                        }
                    }
                }
                continue;
            }

            // Handle simple key-value pairs
            const match = trimmed.match(/(\w+)\s*=\s*"?([^"]*)"?/);
            if (match) {
                const key = match[1];
                const value = match[2].trim();

                if (key === 'version_pattern') {
                    config.version_pattern = value;
                } else if (key === 'date_format') {
                    config.date_format = value;
                }
            }
        }

        return config;
    }

    private getDefaultDocManConfig(): DocManConfig {
        return {
            valid_statuses: [
                "✅ Production Ready",
                "🚧 Draft",
                "🚫 Deprecated",
                "⚠️ Experimental",
                "🔄 In Progress"
            ],
            required_metadata: [
                "Status",
                "Version",
                "Last Updated"
            ],
            version_pattern: "semantic",
            date_format: "YYYY-MM-DD"
        };
    }

    private getDefaultConfig(): string {
        return `# DocMan Configuration
# Copy this file to .docmanrc in your project root and customize as needed

# Root directory for documentation scanning
root_directory = "."

# Index file management
index_file = "DOCUMENTATION_INDEX.md"
recreate_index = true

# Validation settings
strict_validation = true

# Required metadata fields in README files
required_metadata = [
    "Status",
    "Version", 
    "Last Updated"
]

# Valid status values
valid_statuses = [
    "✅ Production Ready",
    "🚧 Draft", 
    "🚫 Deprecated",
    "⚠️ Experimental",
    "🔄 In Progress"
]

# Ignore patterns (directories and files to skip)
ignore_patterns = [
    ".git/",
    "node_modules/", 
    "venv/",
    "__pycache__/",
    "*.tmp",
    "*.log",
    "core"
]

# Date bump settings
date_bump_enabled = true
date_bump_threshold_days = 30

# Link validation
validate_links = true
link_timeout_seconds = 5
`;
    }
}
