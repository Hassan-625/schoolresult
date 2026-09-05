# SchoolCloud Laravel migration

This directory is the parallel Laravel 12 replacement for the live Django application. It is intentionally isolated so production remains available while parity is built and tested.

## Phase 1 completed

- Multi-tenant schema and tenant resolution
- Proprietor, Headmaster, Accountant and Teacher authorization foundation
- Small, Mid-Tier and Premium server-side entitlement configuration
- Student, subject and result schema with automatic grading
- Subscription/payment/offline-upgrade schema
- Interactive Alpine.js + Tailwind dashboard, result modal and subscription UI

The original Excel masters remain in `schoolresults/templates/excel/` until the PhpSpreadsheet exporter is verified byte-for-byte against them.
