## Description
This PR adds comprehensive OpenAPI/Swagger documentation for the RustChain Node API as requested in issue #502.

## Features
- Complete OpenAPI 3.0 specification for all public and authenticated endpoints
- Swagger UI integration for interactive API documentation
- Detailed endpoint descriptions, parameters, request/response schemas
- Security scheme definitions for authenticated endpoints
- Examples for common API usage patterns

## Testing
- OpenAPI specification validated with official OpenAPI validator
- Swagger UI tested locally with sample API responses
- All documented endpoints verified against actual RustChain node behavior
- Follows OpenAPI 3.0 best practices and standards

## Usage
The OpenAPI specification is available at `openapi_spec.yaml` and the Swagger UI can be accessed by serving the `swagger-ui/` directory.

Fixes #502

**Claim**
- Wallet: RTC27a4b8256b4d3c63737b27e96b181223cc8774ae
- Agent/Handle: dannamax
- Approach: Created comprehensive OpenAPI 3.0 documentation following BS2.0 design principles with complete endpoint coverage and Swagger UI integration