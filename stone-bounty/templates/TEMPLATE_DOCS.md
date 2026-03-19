# 📚 Documentation Template

## Issue Analysis
- **Issue Type**: Documentation
- **Complexity**: Low
- **Success Probability**: High (>80%)
- **Required Skills**: Technical writing, API understanding

## Quality Checklist ✅
- [ ] Content addresses specific issue requirements
- [ ] Uses exact field names from actual API responses  
- [ ] Includes real-world examples with curl commands
- [ ] Provides error handling and common mistakes
- [ ] Follows project documentation style
- [ ] Adds SPDX license identifier
- [ ] No placeholder content

## PR Structure
```
docs: Add [specific] documentation for issue #[number]

This PR provides comprehensive documentation that addresses the specific requirements outlined in #[number].

Key features:
- Complete coverage of [specific topic]
- Real-world examples with actual responses
- Error handling and troubleshooting guidance
- Follows existing documentation conventions

Fixes #[number]
```

## File Requirements
- Location: `docs/` directory
- Format: Markdown with proper headers
- License: `# SPDX-License-Identifier: MIT` at top
- Validation: Test all examples against live API