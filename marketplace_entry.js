// JavaScript format for GPT Researcher MCP marketplace entry
marketplaceMCPs = [
    {
        id: 'gpt-researcher',
        name: 'GPT Researcher',
        description: 'Comprehensive AI research assistant with web search, document analysis, and automated report generation',
        author: 'ianimash',
        icon: 'fas fa-search',
        category: 'research',
        tags: ['research', 'web-search', 'ai', 'reports', 'analysis', 'investigation'],
        version: '1.0.1',
        created: '2025-09-18',
        tools: [
            { name: 'quick-research', description: 'Perform focused research on specific topics with web search' },
            { name: 'comprehensive-research', description: 'Conduct in-depth research with detailed analysis and citations' },
            { name: 'get-research-progress', description: 'Monitor real-time progress of ongoing research tasks' },
            { name: 'get-research-result', description: 'Retrieve completed research reports and findings' }
        ],
        features: [
            'Real-time web search integration',
            'Automated report generation with citations',
            'Progress tracking with live updates',
            'Comprehensive research methodology',
            'Free web search capabilities (no API keys required)',
            'Detailed source analysis and verification',
            'Multiple research depth levels',
            'Professional report formatting'
        ],
        requirements: {
            apiKey: 'ExpertGPT Personal API Key',
            apiKeyUrl: 'https://expertgpt.apps1-ir-int.icloud.intel.com/personal_api_keys',
            setupInstructions: {
                windows: [
                    'Get your ExpertGPT Personal API Key from: https://expertgpt.apps1-ir-int.icloud.intel.com/personal_api_keys',
                    'Open System Properties: Win+R → sysdm.cpl → Advanced → Environment Variables',
                    'Under "User variables", click "New"',
                    'Variable name: EGPT_API_KEY',
                    'Variable value: [Your ExpertGPT API Key]',
                    'Click OK and restart DataAgent',
                    'Alternative: Set via Command Prompt → setx EGPT_API_KEY "your-api-key-here"'
                ]
            }
        }
    }
]