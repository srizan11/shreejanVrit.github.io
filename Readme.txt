I designed a Django REST API that can process massive amounts of emails efficiently. The API accepts email lists and responds right away with task IDs, while the heavy checks run in the background on workers. Everything is containerized with Docker, making deployment consistent across environments and simple to scale.

Architecture & approach
The core API is built with Django (>=4.1) and Django REST Framework (>=3.15.0), which provides a structured HTTP layer. The API remains stateless, focusing on receiving jobs and tracking them.
Background tasks are handled by Celery (>=5.2 with Redis), which offloads expensive operations. Tasks are dispatched quickly, leaving the main API responsive.
Messaging is managed with Pika (>=1.3.0), connecting directly to RabbitMQ to ensure durable delivery and reliability.
All validated results are stored in Postgres (>=15) through psycopg2-binary (>=2.9.0), which offers stable and optimized database connections.
Redis (>=7.0) works both as the Celery result backend and a caching layer, storing DNS lookups and temporary rate limits.
Configuration is managed with python-dotenv (>=1.0.0), which helps in loading environment variables cleanly across local and containerized setups.

Validation logic
dnspython (>=2.3.0) performs DNS lookups, including MX and TXT records for SPF and DMARC checks.
SMTP checks are done with smtplib under strict timeouts, ensuring connections don’t hang.
Address parsing is handled with Python’s built-in email.utils.
DKIM probing is attempted best-effort: the system tries with common selectors, and if it can’t confirm, it reports the result as “unknown.”

Considerations
SMTP probing is unstable and may behave differently across servers, so retries should be minimal and timeouts tight. Never send real email content during checks.
DKIM is incomplete by nature, since selectors are not always discoverable; best-effort probing is used, but unknowns are common.
Running everything inside Docker makes it easier to scale horizontally, while Postgres ensures strong persistence and durability for all results.
At scale, it’s important to respect privacy, anti-abuse rules, and per-domain throttling so external mail servers aren’t overloaded.