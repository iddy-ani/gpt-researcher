# Python format for GPT Researcher MCP marketplace entry
marketplace_mcps = [
    {
        'id': 'gpt-researcher',
        'name': 'GPT Researcher',
        'description': 'Comprehensive AI research assistant with web search, document analysis, and automated report generation',
        'author': 'ianimash',
        'icon': 'fas fa-search',
        'category': 'research',
        'tags': ['research', 'web-search', 'ai', 'reports', 'analysis', 'investigation'],
        'version': '1.0.1',
        'created': '2025-09-18',
        'tools': [
            {'name': 'quick-research', 'description': 'Perform focused research on specific topics with web search'},
            {'name': 'comprehensive-research', 'description': 'Conduct in-depth research with detailed analysis and citations'},
            {'name': 'get-research-progress', 'description': 'Monitor real-time progress of ongoing research tasks'},
            {'name': 'get-research-result', 'description': 'Retrieve completed research reports and findings'}
        ],
        'features': [
            'Real-time web search integration',
            'Automated report generation with citations',
            'Progress tracking with live updates',
            'Comprehensive research methodology',
            'Free web search capabilities (no API keys required)',
            'Detailed source analysis and verification',
            'Multiple research depth levels',
            'Professional report formatting'
        ],
        'requirements': {
            'api_key': 'ExpertGPT Personal API Key',
            'api_key_url': 'https://expertgpt.apps1-ir-int.icloud.intel.com/personal_api_keys',
            'setup_instructions': {
                'windows': [
                    '1. Get your ExpertGPT Personal API Key from: https://expertgpt.apps1-ir-int.icloud.intel.com/personal_api_keys',
                    '2. Open System Properties: Win+R → sysdm.cpl → Advanced → Environment Variables',
                    '3. Under "User variables", click "New"',
                    '4. Variable name: EGPT_API_KEY',
                    '5. Variable value: [Your ExpertGPT API Key]',
                    '6. Click OK and restart DataAgent',
                    'Alternative: Set via Command Prompt → setx EGPT_API_KEY "your-api-key-here"'
                ]
            }
        }
    }
]