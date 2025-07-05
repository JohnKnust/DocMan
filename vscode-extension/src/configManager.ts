import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

export interface DocManConfig {
    valid_statuses: string[];
    required_metadata: string[];
    version_pattern: string;
    date_format: string;
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

    async getDocManConfig(): Promise<DocManConfig> {
        const configPath = await this.findConfigFile();

        if (!configPath) {
            return this.getDefaultDocManConfig();
        }

        try {
            const configContent = fs.readFileSync(configPath, 'utf8');
            return this.parseDocManConfig(configContent);
        } catch (error) {
            console.warn('Failed to parse DocMan config, using defaults:', error);
            return this.getDefaultDocManConfig();
        }
    }

    private parseDocManConfig(content: string): DocManConfig {
        const config = this.getDefaultDocManConfig();
        const lines = content.split('\n');

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();

            // Skip comments and empty lines
            if (!line || line.startsWith('#')) {
                continue;
            }

            // Handle multiline arrays
            if (line.includes('[') && !line.includes(']')) {
                const key = line.split('=')[0].trim();
                const items: string[] = [];

                // Extract first item if present
                const firstItem = line.split('[')[1]?.trim();
                if (firstItem && firstItem !== '') {
                    items.push(firstItem.replace(/[",]/g, '').trim());
                }

                // Continue reading until closing bracket
                i++;
                while (i < lines.length && !lines[i].includes(']')) {
                    const item = lines[i].trim().replace(/[",]/g, '').trim();
                    if (item && !item.startsWith('#')) {
                        items.push(item);
                    }
                    i++;
                }

                // Handle last item with closing bracket
                if (i < lines.length && lines[i].includes(']')) {
                    const lastItem = lines[i].split(']')[0].trim().replace(/[",]/g, '').trim();
                    if (lastItem) {
                        items.push(lastItem);
                    }
                }

                if (key === 'valid_statuses') {
                    config.valid_statuses = items.filter(item => item.length > 0);
                } else if (key === 'required_metadata') {
                    config.required_metadata = items.filter(item => item.length > 0);
                }
                continue;
            }

            // Handle simple key-value pairs
            const match = line.match(/(\w+)\s*=\s*"?([^"]*)"?/);
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
}
