---
name: Django REST Framework Master Rules
description: Advanced enterprise-level architecture rules for Django REST Framework (DRF) projects, including custom base classes, responses, security, and performance.
---

# Advanced Django REST Framework Master Rules
# ---------------------------------------------------------
# INSTRUCTIONS FOR AI ASSISTANT:
# You are an Expert-Level Enterprise Backend Engineer.
# When initiating a new Django project or adding code to an existing one, 
# you MUST abide by this architecture template. Do not write "tutorial-level" 
# vanilla DRF code. Build the project using these enterprise abstractions.

## 1. Project Scaffolding & Core Architecture
- NEVER use standard DRF `APIView`, `ModelViewSet`, or `ModelSerializer` directly in feature apps.
- ALL projects must start with a `common` or `core` app that houses Custom Base Classes.
- Every feature app MUST inherit from your custom base classes.

## 2. The Custom Base View Layer
You must immediately generate a module (e.g., `core/views/generic.py`) containing wrappers for DRF generic views:
- `AppAPIView` (wraps `APIView` for custom endpoints)
- `AppModelListAPIViewSet` (wraps `ListModelMixin, GenericViewSet` + Pagination + Filters)
- `AppModelCUDAPIViewSet` (wraps `CreateModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet`)
- `AppModelRetrieveAPIViewSet` (wraps `RetrieveModelMixin, GenericViewSet`)

## 3. The Custom Base Serializer Layer
You must immediately generate a module (e.g., `core/serializers/base.py`) containing wrapped serializers:
- `AppModelSerializer` (wraps `serializers.ModelSerializer`)
- `AppReadOnlyModelSerializer` (Overrides `to_representation` or fields for GET performance)
- `AppWriteOnlyModelSerializer` (Optimized for POST/PUT/PATCH validation)

## 4. API Response Wrapping (The Mixin)
- NEVER return a raw `Response({"data": ...})` from a view.
- Create an `AppViewMixin` class that all `App*` views inherit from.
- `AppViewMixin` must contain standardization functions:
  - `def send_response(self, data, status=200, message="Success"):`
  - `def send_error_response(self, data, status=400, message="Error"):`
- ALL JSON responses from the server must follow exactly one unified structure mapped by these functions.

## 5. Security & RBAC (Role-Based Access Control)
- DO NOT rely solely on `IsAuthenticated` or `IsAdminUser`.
- Create a `Feature` model (list of all API modules) and a `UserRole` model.
- Create generic Permission Classes (e.g., `AllowAdminOnly`) that read the user's Token, lookup their `UserRole`, and verify if they have Create/Retrieve/Update/Delete access to the View's declared `feature = "X"` string.
- Apply these custom Permission Classes globally or per-view.

## 6. Audit Logging (System Trails)
- Production apps must record WHO changed WHAT and WHEN.
- Create an `AuditLog` database model and a `LoggingMixin`.
- When manually overriding `create()`, `update()`, or `destroy()` in your `AppWriteOnlyModelSerializer`s, you MUST trigger the logger:
  - e.g., `LoggingMixin.log_update(self, old_instance, new_instance)`
- This ensures any hacker or rogue admin is permanently tracked.

## 7. Bulk Operations (Performance)
- When building APIs representing bulk data (e.g., uploading 100 products), DO NOT force the frontend to call the API 100 times.
- Override `get_serializer()` in the view: inject `kwargs["many"] = True` if the incoming payload is a JSON Array instead of an Object.
- Build a custom `serializers.ListSerializer` to catch the array, validate items, and execute a high-speed Postgres `bulk_create` or `bulk_update` query.
- NOTE: If Audit Logging or Django Signals are required for the models involved, manually loop and save objects inside the `ListSerializer` rather than using `bulk_create`. 

## 8. Dynamic File Upload APIs
- File uploads require repetitive logic for file-size validation, format checking, and S3 uploading.
- Create a Factory Function (e.g. `def get_upload_api_view(meta_model, max_size_mb=3):`) that dynamically generates and returns a complete File Upload API View class for whatever database Model is passed to it.

## 9. Error Handling
- Intercept 500 Server Errors gracefully using a Custom Exception Handler in `settings.py`.
- Translate database errors (like `IntegrityError` or `UniqueViolation`) into user-friendly JSON messages that pass through the `send_error_response` wrapper.

## 10. Database Query Optimization (The N+1 Problem)
- NEVER allow N+1 queries in List Views.
- When overriding `get_queryset()` in your `AppModelListAPIViewSet`, you MUST aggressively use `select_related()` for ForeignKeys and `prefetch_related()` for ManyToMany/Reverse relations.
- If a Serializer contains a `SerializerMethodField` that hits the database, rewrite the view's query to use Django's `annotate()` instead, pushing the math down to Postgres.
- Use `only()` and `defer()` if a table has massive text/JSON fields that are not needed in a list response (e.g., pulling a list of blog titles without pulling the HTML body).

## 11. Caching Strategies
- Implement Redis for caching.
- Cache heavily-read, rarely-written endpoints (e.g., Homepage Banners, Base Product Categories) using Django's `@method_decorator(cache_page(...))` or custom manual caching inside the view.
- When an Admin updates a cached entity (e.g., via `AppModelCUDAPIViewSet.update`), you MUST automatically invalidate the associated Redis cache keys in the `update()` or `create()` method.
- Store complex calculations (like a user's total wallet balance or unread notification count) in the cache, and invalidate the cache when a transaction occurs.

## 12. Asynchronous Processing (Celery)
- NEVER put long-running tasks inside the main HTTP Request/Response cycle.
- If an API triggers emails, SMS, push notifications, heavy Excel exports, or third-party payment verifications, immediately offload the task to a Celery worker using `.delay()`.
- Return an instant HTTP 200/202 to the user, and let Celery handle the heavy lifting in the background.

## 13. Soft Deletes (Never Lose Data)
- In production, NEVER use Django's default `Model.delete()` which permanently destroys data.
- Create a `BaseModel` abstract class with: `is_deleted = BooleanField(default=False)`, `deleted_at = DateTimeField(null=True)`, `deleted_by = ForeignKey(User, null=True)`.
- ALL project models must inherit from this `BaseModel`.
- Override the default Django `Manager` with a custom `SoftDeleteManager` that automatically filters out `is_deleted=True` rows from every query (`get_queryset().filter(is_deleted=False)`).
- When the `DestroyModelMixin` (inside `AppModelCUDAPIViewSet`) runs, override `perform_destroy()` to set `is_deleted=True` and `deleted_at=timezone.now()` instead of calling `.delete()`.
- Create a separate Admin-only "Trash" endpoint to list and restore soft-deleted items if needed.

## 14. API Documentation (Swagger / OpenAPI)
- Install `drf-spectacular` and configure it in `settings.py` under `REST_FRAMEWORK.DEFAULT_SCHEMA_CLASS`.
- Every ViewSet MUST have a docstring explaining its purpose.
- Use `@extend_schema(tags=["Module Name"])` on every action/method to group endpoints logically in the Swagger UI.
- Use `@extend_schema(request=..., responses=...)` to explicitly document non-obvious request/response bodies.
- Generate the Swagger UI at `/api/docs/` and the raw OpenAPI JSON at `/api/schema/` so the frontend team can auto-generate TypeScript types from it.

## 15. Rate Limiting / Throttling
- Configure DRF's built-in throttle classes in `settings.py` under `REST_FRAMEWORK.DEFAULT_THROTTLE_CLASSES` and `DEFAULT_THROTTLE_RATES`.
- Set sensible defaults: e.g., `"anon": "20/minute"` for unauthenticated users, `"user": "100/minute"` for authenticated users.
- For sensitive endpoints (Login, OTP, Password Reset, Payment), apply stricter per-view throttles using `throttle_classes = [ScopedRateThrottle]` with custom scopes like `"login": "5/minute"`.
- This prevents brute-force attacks, API abuse, and accidental DDoS from buggy frontend code.

## 16. Database Transactions (Atomic Operations)
- Any API endpoint that writes to MORE THAN ONE table in a single request MUST be wrapped inside `from django.db import transaction` → `with transaction.atomic():`.
- This guarantees that if the second table write fails (e.g., creating an `OrderItem` after an `Order`), the first table write is automatically rolled back and the database stays clean.
- NEVER leave multi-table writes unprotected. A server crash mid-write without `atomic()` will leave the database in a corrupted half-finished state.
- For Celery tasks that involve multi-step database writes, use `transaction.on_commit()` to ensure the Celery task only fires AFTER the database transaction has fully committed.

## 17. Real-Time Communication (WebSockets / Django Channels)
- For features requiring instant updates (order notifications, live chat, dashboards), use Django Channels with WebSocket Consumers. NEVER use HTTP polling (setInterval).
- Configure ASGI (`asgi.py`) with `ProtocolTypeRouter` to route HTTP traffic to Django and WebSocket traffic to Channels.
- Create a `WebSocketAuthMiddleware` that reads the JWT token from the WebSocket handshake query string and authenticates the user before allowing the connection.
- Use Channel Layer Groups (backed by Redis) for broadcasting messages to multiple connected clients (e.g., `group_send("kitchen_order_group", {...})`).
- Use `async_to_sync()` to send WebSocket messages from synchronous Django code (like serializers or helper functions).

## 18. Testing Standards
- Every new feature MUST ship with tests. No exceptions.
- **Unit Tests (Serializers):** Test validation logic, custom `create()`, and `update()` methods in isolation using `APITestCase`. Verify that invalid data raises `ValidationError` and valid data saves correctly.
- **Integration Tests (Views):** Use DRF's `APIClient` to send actual HTTP requests (`client.post(...)`, `client.get(...)`) and assert status codes, response structure, and database state.
- **Permission Tests:** For every endpoint, write at least one test proving that an unauthorized user (wrong role, no token) receives a `403 Forbidden`.
- **Edge Case Tests:** Test empty payloads, duplicate entries, boundary values (e.g., `discount = 101%`), and concurrent requests where applicable.
- Use `factory_boy` or `model_bakery` to generate test data instead of manually creating fixtures.

## 19. Environment Configuration & Secrets
- NEVER hardcode database passwords, API keys, secret keys, or third-party credentials anywhere in the codebase.
- Use `django-environ` to load all sensitive values from a `.env` file: `env = environ.Env()` → `SECRET_KEY = env("SECRET_KEY")`.
- Maintain separate settings files for different environments: `settings/base.py` (shared), `settings/local.py` (development), `settings/production.py` (live server).
- The `.env` file MUST be listed in `.gitignore`. Provide a `.env.example` with placeholder values so new developers know which keys are required.
- For production deployments, inject secrets via environment variables from the hosting platform (Docker, AWS, etc.) instead of `.env` files.

## 20. Idempotency (Payment & Order Safety)
- For any endpoint that creates resources with side effects (Payments, Orders, Wallet Transactions), require an `Idempotency-Key` header from the frontend.
- Before processing the request, check Redis/DB for that key. If the key already exists, return the cached response immediately without re-executing the logic.
- After successfully processing the request, store the key + response in Redis with a TTL (e.g., 24 hours).
- This prevents duplicate orders when the user's internet drops mid-request and the frontend automatically retries.

## 21. Optimistic Locking (Concurrency Control)
- For models that can be edited by multiple admins simultaneously (Products, Orders, Inventory), add a `version = PositiveIntegerField(default=1)` field.
- The frontend must send the current `version` number with every update request.
- In the serializer's `update()` method, compare the incoming `version` against the database version. If they don't match, another user edited the record first — raise a `ValidationError("This record was modified by another user. Please refresh and try again.")`.
- On successful update, increment the `version` field by 1.

## 22. API Versioning (Future-Proofing)
- Configure URL-based versioning in `settings.py`: `DEFAULT_VERSIONING_CLASS = "rest_framework.versioning.URLPathVersioning"`.
- Structure all API URLs as `/api/v1/...`. When breaking changes are needed, create `/api/v2/...` routes pointing to new ViewSets while keeping `v1` alive for older app versions.
- NEVER remove or rename existing response fields in an active version. Only add new fields. If a field must be removed, do it in the next version.
- Document which API version each mobile app release uses, so the backend team knows when it is safe to deprecate old versions.

## 23. Database-Level Validation (Constraints)
- Serializer validation runs in Python. It can be bypassed by Celery tasks, management commands, or Django shell. The database is the LAST line of defense.
- Use `unique=True`, `unique_together`, and `UniqueConstraint` to prevent duplicate data at the database level.
- Use `CheckConstraint` for business rules that must NEVER be violated: e.g., `models.CheckConstraint(check=Q(discount__gte=0) & Q(discount__lte=100), name="valid_discount_range")`.
- Use `models.PositiveIntegerField()` instead of `IntegerField()` for values that should never be negative (price, quantity, stock).
- Always define `on_delete` behavior explicitly on ForeignKeys (`CASCADE`, `SET_NULL`, `PROTECT`) based on business logic.

## 24. Celery Hardening (Background Job Reliability)
- Every Celery task MUST have a `time_limit` and `soft_time_limit` to prevent zombie tasks from hanging forever.
- Use automatic retries with exponential backoff for tasks that call external APIs: `@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)`.
- Log task failures with full context (task name, arguments, exception traceback) so they can be debugged from Grafana/Sentry.
- Use `transaction.on_commit(lambda: my_task.delay(id))` to ensure Celery tasks only fire AFTER the database transaction commits. Without this, Celery may try to read a row that hasn't been saved yet.

## 25. Security Hardening
- **JWT Tokens:** Implement short-lived access tokens (15-30 minutes) with long-lived refresh tokens. Maintain a blacklist of revoked refresh tokens in Redis.
- **CORS:** Configure `django-cors-headers` with an explicit whitelist of allowed origins. NEVER use `CORS_ALLOW_ALL_ORIGINS = True` in production.
- **File Uploads:** Validate file MIME types server-side (not just extensions). Reject executables, scripts, and suspicious file types. Enforce strict size limits.
- **Raw SQL:** NEVER use raw SQL queries (`cursor.execute(...)`) unless absolutely necessary. Always use Django ORM to prevent SQL injection. If raw SQL is unavoidable, use parameterized queries exclusively.
- **Sensitive Data:** Never return passwords, tokens, or internal IDs in API responses. Use `write_only=True` on serializer fields for sensitive inputs.

## 26. Timezone & Localization
- ALWAYS set `USE_TZ = True` in `settings.py`. This forces Django to store all `DateTimeField` values in UTC in the database.
- NEVER use `datetime.now()`. ALWAYS use `django.utils.timezone.now()` which automatically returns timezone-aware UTC datetimes.
- The frontend is responsible for converting UTC timestamps to the user's local timezone for display. The backend must NEVER store local times.
- For date-based filtering (e.g., "orders placed today"), convert the user's local date boundaries to UTC before querying the database.

## 27. Health Checks & Readiness Probes
- Create lightweight endpoints for infrastructure monitoring (required for Docker, Kubernetes, and load balancers):
  - `/health/live/` — Returns `200 OK` if the Django process is running (no DB check needed).
  - `/health/ready/` — Returns `200 OK` only if the database, Redis, and Celery are all reachable. Returns `503` if any dependency is down.
- These endpoints must be excluded from authentication, throttling, and audit logging.

## 28. Large File Handling (Pre-Signed URLs)
- For files larger than 5MB (videos, high-res images, CSV exports), DO NOT pass the file through Django.
- Instead, generate a pre-signed S3 upload URL from the backend and return it to the frontend. The frontend uploads directly to S3, bypassing the Django server entirely.
- After the upload completes, the frontend sends the S3 object key back to Django to save in the database.
- This prevents Django from running out of memory and dramatically reduces server bandwidth costs.

## 29. Observability (Structured Logging & Tracing)
- Use structured JSON logging (not plain text) so logs can be parsed by Loki, ELK, or CloudWatch: `logger.info("order_created", extra={"user_id": user.id, "order_id": order.id, "amount": total})`.
- Add a custom middleware that generates a unique `trace_id` (UUID) for every incoming HTTP request and attaches it to all log entries during that request's lifecycle. This allows you to trace every log line from a single user action.
- Integrate error tracking (Sentry or similar) to automatically capture and alert on 500 errors in production.
- Monitor slow queries using Django's database logging: `settings.LOGGING` → log any query taking longer than 200ms.

# ---------------------------------------------------------
# ENFORCEMENT
# When asked to scaffold a new feature, automatically generate the ViewSets and Serializers
# by inheriting from these Base Classes, ensuring all routing is:
# ✅ Tightly controlled (custom views, not raw DRF)
# ✅ Fully audited (LoggingMixin on every mutation)
# ✅ Strictly permissioned (RBAC + custom permission classes)
# ✅ Aggressively optimized (select_related, prefetch_related, caching)
# ✅ Fully tested (unit, integration, and permission tests)
# ✅ Production-hardened (idempotency, transactions, retries, health checks)
