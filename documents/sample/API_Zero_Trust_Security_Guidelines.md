# API ZERO-TRUST ARCHITECTURE GUIDELINES

## 1. Principles of Zero-Trust
Every internal microservice request must be explicitly authenticated, authorized, and cryptographically verified regardless of network perimeter or origin IP.

## 2. Token Standards
- Short-lived asymmetric RSA-256 / Ed25519 signed JWT tokens with 1-hour expiration.
- Tenant ID, Department scope, and Role claims must be validated at API gateway boundaries.

## 3. Mutual TLS (mTLS)
All inter-service gRPC and REST communications must enforce SPIFFE/SPIRE-issued x509 certificates with automated 24-hour rotation.