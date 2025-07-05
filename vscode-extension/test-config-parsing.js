#!/usr/bin/env node

// Simple test to verify config parsing works
const fs = require('fs');
const path = require('path');

// Test the parsing logic directly without VS Code dependencies
function parseDocManConfig(content) {
    const config = {};
    const lines = content.split('\n');

    let currentArray = [];
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

async function testConfigParsing() {
    console.log('🧪 Testing DocMan Config Parsing...\n');

    try {
        // Find config file
        const configPath = path.join('..', '..', '.docmanrc');

        if (!fs.existsSync(configPath)) {
            console.log('❌ No config file found at:', configPath);
            return;
        }

        console.log(`📁 Config file found: ${configPath}`);

        // Read and parse config
        const configContent = fs.readFileSync(configPath, 'utf8');
        const config = parseDocManConfig(configContent);

        console.log('\n📋 Parsed Configuration:');
        console.log('Valid Statuses:', config.valid_statuses);
        console.log('Required Metadata:', config.required_metadata);
        console.log('Version Pattern:', config.version_pattern);
        console.log('Date Format:', config.date_format);

        // Test the specific issue - count valid statuses
        const statusCount = config.valid_statuses ? config.valid_statuses.length : 0;
        console.log(`\n🔢 Number of valid statuses: ${statusCount}`);

        if (statusCount === 5) {
            console.log('✅ Config parsing is working correctly!');
        } else {
            console.log('❌ Config parsing issue - expected 5 statuses');
        }

    } catch (error) {
        console.error('❌ Error testing config:', error);
    }
}

testConfigParsing();
