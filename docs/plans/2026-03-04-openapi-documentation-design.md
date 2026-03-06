# OpenAPI/Swagger Documentation for RustChain Node API - Design Document

## Overview
This document outlines the design and implementation plan for creating OpenAPI 3.0 documentation for the RustChain Node API as requested in bounty issue #502.

## Requirements Analysis

### Core Requirements
1. **OpenAPI 3.0 Specification**: Complete API specification in OpenAPI 3.0 format
2. **Swagger UI Integration**: Interactive documentation interface
3. **Comprehensive Coverage**: All public and authenticated endpoints
4. **Developer-Friendly**: Clear examples, schemas, and usage instructions

### Known Endpoints to Document

#### Public Endpoints (No Authentication Required)
- `GET /health` - Node health check
- `GET /ready` - Readiness probe  
- `GET /api/miners` - Active miners list
- `GET /api/epoch` - Current epoch information
- `GET /api/ledger` - Rewards ledger

#### Authenticated Endpoints
- `POST /attest/submit` - Submit hardware attestation
- `GET /api/balance?miner_id={id}` - Query miner balance
- `POST /api/transfer` - Signed token transfer

## Implementation Strategy

### Phase 1: API Discovery and Analysis
- Analyze existing RustChain node source code to identify all endpoints
- Document request/response schemas for each endpoint
- Identify authentication requirements and security schemes
- Map out API structure and relationships

### Phase 2: OpenAPI Specification Creation
- Create `openapi.yaml` file with complete OpenAPI 3.0 specification
- Define components (schemas, parameters, responses, security schemes)
- Document all paths with proper HTTP methods and operations
- Include example requests and responses

### Phase 3: Swagger UI Integration
- Create `docs/swagger-ui/` directory structure
- Integrate Swagger UI static files
- Configure Swagger UI to load the OpenAPI specification
- Add navigation and styling consistent with RustChain branding

### Phase 4: Testing and Validation
- Validate OpenAPI specification using online validators
- Test Swagger UI locally to ensure proper functionality
- Verify all documented endpoints match actual API behavior
- Ensure cross-browser compatibility

## File Structure

```
rustchain/
├── docs/
│   └── swagger-ui/
│       ├── index.html
│       ├── openapi.yaml
│       └── swagger-ui-bundle.js (and other static assets)
└── README.md (update with API documentation link)
```

## Technical Specifications

### OpenAPI Components

#### Info Object
```yaml
info:
  title: RustChain Node API
  description: REST API for RustChain Proof-of-Antiquity blockchain node
  version: 2.2.1
  contact:
    name: RustChain Team
    url: https://rustchain.org
```

#### Servers
```yaml
servers:
  - url: https://50.28.86.131
    description: Production RustChain Node
```

#### Security Schemes
```yaml
components:
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
```

### Path Examples

#### Health Check
```yaml
/health:
  get:
    summary: Node health check
    description: Returns node health status
    responses:
      '200':
        description: Node is healthy
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: "ok"
```

#### Miners List
```yaml
/api/miners:
  get:
    summary: Get active miners list
    description: Returns list of currently active miners
    responses:
      '200':
        description: Successful response
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/Miner'
```

## Success Criteria

- [ ] OpenAPI 3.0 specification validates successfully
- [ ] All known endpoints are documented with proper schemas
- [ ] Swagger UI loads and displays documentation correctly
- [ ] Authentication requirements are properly documented
- [ ] Examples are provided for key endpoints
- [ ] Documentation is linked from main README.md
- [ ] PR follows BS2.0 non-destructive integration principles

## Risk Assessment

### Low Risk Factors
- Pure documentation task (no code changes to core functionality)
- Well-defined requirements and scope
- Existing API endpoints are stable
- OpenAPI 3.0 is a standard format with good tooling

### Potential Challenges
- Some API endpoints may not be fully documented in source code
- Authentication flow details may need clarification
- Response schemas may vary between different API versions

## Mitigation Strategies

1. **API Exploration**: Use curl/wget to test actual API responses
2. **Conservative Documentation**: Only document confirmed behavior
3. **Version Compatibility**: Note API version in documentation
4. **Maintainer Feedback**: Be prepared to iterate based on review feedback

## Timeline

- **Phase 1 (15 min)**: API discovery and analysis
- **Phase 2 (30 min)**: OpenAPI specification creation  
- **Phase 3 (10 min)**: Swagger UI integration
- **Phase 4 (5 min)**: Testing and validation
- **Total**: ~60 minutes (matches bounty time estimate)

## Approval Request

This design document outlines a comprehensive approach to implementing the OpenAPI/Swagger documentation for RustChain Node API. The plan follows BS2.0 principles of non-destructive integration and focuses on developer experience.

**Recommended Action**: Proceed with implementation as outlined.

---
*Created by BS2.0 Automated Bounty System*
*Bounty Issue: #502*
*Date: 2026-03-04*