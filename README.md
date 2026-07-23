# HomeDoc Fusion API

A FastAPI + SQLModel backend that models real-estate entities ("HomeDocs" - properties, floors, apartments, rooms) as a self-referential hierarchy and exposes generic filterable/sortable REST APIs over them - a general-purpose information-system layer usable directly by a client application, not merely infrastructure for the ETL pipeline layered on top of it, which ingests rental listings from an external API, matches them against existing records, and writes them back through a batched, transactional pipeline.

This is a personal project built to demonstrate a backend architecture and set of patterns I used professionally - layered repository/service design, a generic dynamic query engine, a composable ETL pipeline abstraction, and a real, measured performance-optimization pass (details below).

**Live API docs (Swagger):** https://homdoc-fusion.onrender.com/docs

## Architecture highlights

- **Layered design - API → Service → Repository.** Each entity (`HomeDoc`, `Residence`) has a thin FastAPI router, a service layer holding validation/business rules, and a repository layer owning all query construction. Repositories are pulled from two small generic base classes (`SingleEntityRepository`, `ExpandedEntityRepository`) so new entities can declare their relationships once and inherit filtering, sorting, pagination, and eager-loading strategy for free.

- **A generic, query-string-driven filter/sort/pagination engine** (`SingleTableFeatures` / `MultiTableFeatures`) that turns request query parameters into SQLAlchemy `WHERE`/`ORDER BY`/`LIMIT` clauses across single or multi-table (joined) queries - supporting operators like `[$gt]`, `[$in]`, `[$ilike]`, date-range filtering, and field selection, all from the URL, without per-endpoint filter code.

- **A composable ETL pipeline abstraction** (`pipeline/`: `Operation`, `Batch`, `Pipeline`) used to build the rental-listing ingestion flow - fetch from an external API → validate/transform → match against existing records → batch-write - as a chain of small, independently testable steps rather than one monolithic function.

- **Declarative relationship configuration** (`RelationshipConfig`) that describes each entity's related tables (one-to-one, one-to-many, many-to-one) and their load strategy (`joined` vs. `selectin`) once, and a shared query builder that assembles the correct SQLAlchemy `join`/`joinedload`/`selectinload`/`contains_eager` calls from that config.

- **A measured performance-optimization pass**, profiled the ingestion pipeline with custom timing instrumentation and reduced processing time for a 100-record batch from ~220s to ~10s. The improvement came from eliminating an N+1 query pattern, fixing unintended lazy loading by adding the missing eager load, and replacing per-record database flushes with a single batched flush, allowing SQLAlchemy to use multi-row INSERT batching. Each run emits a structured timing summary to help identify future bottlenecks.

## Tech stack

- **API:** FastAPI, Pydantic v2, Uvicorn/Gunicorn
- **Data layer:** SQLModel (SQLAlchemy 2.0) over PostgreSQL, via `psycopg` (v3)
- **Migrations:** Alembic
- **Deployment:** Render

## Project structure

```
app.py                     # FastAPI app, routers, request-timing middleware
entities/
  abstracts/                # Generic repository/service base classes, shared query builders
  home_doc/, residence/      # Per-entity models, DTOs, repository, service, API router
  utils/                     # Filter/sort/pagination engines (SingleTableFeatures, MultiTableFeatures)
fusion/rental_listing/      # The ingestion pipeline: fetch, transform, match, batch-write
pipeline/                   # Generic Operation/Batch/Pipeline abstraction used by the ingestion flow
db/                          # Engine/session setup, raw connection helpers
migrations/                  # Alembic migrations
```

## API overview

- `GET/POST/PUT/DELETE /api/home_docs` - generic HomeDoc CRUD with dynamic filtering/sorting/pagination
- `GET /api/home_docs/newest-properties`, `GET /api/home_docs/oldest-properties` - convenience shortcuts over the same query engine, sorted by creation date
- `GET/POST/PUT/DELETE /api/residence` - Residence CRUD (a HomeDoc subtype) with the same query engine, plus nested one-to-one/one-to-many relations (specs, dimensions, listing, listing history, agent/office contacts)
- `GET /api/fuse` - runs the full ingestion pipeline: fetches rental listings, transforms/validates them, matches against existing residences by external ID, and creates/updates them in one batched transaction

Full interactive documentation, request/response schemas, and examples are available at the Swagger link above.

## Running locally

1. `pip install -r requirements.txt`
2. Create a `.env` file with:
   - `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
   - `DEBUG` (`true`/`false`), `CORS_ORIGINS` (JSON list of allowed origins)
   - `RENTCAST_RENTAL_LISTING_API`, `RENTCAST_RENTAL_LISTING_API_KEY` (for the ingestion pipeline)
3. Run migrations: `alembic upgrade head`
4. Start the server: `python app.py` (or `uvicorn app:app --reload`)
