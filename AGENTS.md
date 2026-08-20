# NIRNAYA — Agent Rules (AGENTS.md)

## Architecture Rules
1. Modular monolith: frontend/ (Next.js) + backend/ (FastAPI). No microservices.
2. All business logic in backend/app/services/. No business logic in route handlers.
3. All data types defined as Pydantic models in backend/app/schemas/.
4. All database models use SQLAlchemy in backend/app/models/.
5. API routes in backend/app/api/. Thin handlers that delegate to services.

## AI Rules
1. LLMs may: extract, classify intent, select tools, retrieve, reason over evidence, explain.
2. LLMs must NOT: decide fraud independently, calculate finances, invent evidence, invent regulatory claims.
3. Every LLM call goes through the LLMRouter abstraction.
4. Every LLM response is validated against a Pydantic schema.
5. If LLM fails, deterministic fallback must exist.
6. Never log full LLM prompts containing user financial data in production.

## Dependency Rules
1. Every external service has a local/deterministic fallback.
2. No paid API is a hard dependency. App must start without API keys.
3. Do not add: MongoDB, Redis, Neo4j, Pinecone, Kafka, Kubernetes, CrewAI.
4. New dependencies require justification.

## Coding Conventions
1. Python: type hints on all functions. Pydantic for data validation.
2. TypeScript: strict mode. Zod for runtime validation.
3. No `Any` types in critical paths.
4. Async by default for I/O operations.
5. Use structured logging, not print().

## Testing Rules
1. Every service has unit tests.
2. Every API endpoint has integration tests.
3. Every ML model has evaluation metrics.
4. No fabricated test data or metrics.
5. Tests must pass before merging.

## Security Rules
1. API keys in environment variables only.
2. No secrets in frontend code.
3. Input validation on all endpoints.
4. File upload: size limits + MIME type validation.
5. SQL injection protection via ORM.
6. Hash shared fraud entities for privacy.

## Definition of Done
A feature is done when:
- [ ] Implementation exists
- [ ] Pydantic schemas defined
- [ ] Unit tests pass
- [ ] API endpoint works
- [ ] UI works (if applicable)
- [ ] Error handling exists
- [ ] Fallback works (if applicable)
