## ADDED Requirements

### Requirement: Owner-scoped cached room-list responses

The room-list data endpoint SHALL cache only successful JSON payloads using a cache namespace that includes the authenticated owner's identity, the normalized search query, the normalized requested page, and that owner's room-list cache version. The endpoint SHALL use the configured default cache timeout for cached payloads. A cached payload for one owner SHALL NOT be returned to another owner. The endpoint SHALL preserve the existing response shape, ordering, search, and pagination behavior whether a payload is cached or freshly generated.

#### Scenario: An owner repeats the same list request

- **WHEN** an authenticated owner sends the same normalized search and page request after a successful response has been cached
- **THEN** the endpoint returns the cached payload without rebuilding that owner's room-list payload

#### Scenario: Different owners request the same search and page

- **WHEN** two authenticated owners request identical search and page parameters
- **THEN** each owner receives a payload containing only that owner's rooms

##### Example: owner-isolated keys

| Owner | Query | Page | Required result |
| --- | --- | --- | --- |
| user 10 | `fri` | 1 | only rooms owned by user 10 |
| user 11 | `fri` | 1 | only rooms owned by user 11 |

### Requirement: Commit-time room-list cache invalidation

The system SHALL invalidate an owner's cached room-list payloads by advancing that owner's room-list cache version after a Room create, save, owner transfer, or delete transaction commits successfully. A Room owner transfer SHALL invalidate both the previous and current owners. A transaction rollback SHALL NOT advance any room-list cache version. The system SHALL use Room model lifecycle signals so invalidation covers supported writes outside the room creation view.

#### Scenario: A room is created

- **WHEN** a transaction that creates a Room commits successfully
- **THEN** the new owner's next room-list request does not return a payload cached before the creation

#### Scenario: A room is deleted

- **WHEN** a transaction that deletes a Room commits successfully
- **THEN** the former owner's next room-list request does not return a payload cached before the deletion

#### Scenario: A room changes owners

- **WHEN** a transaction changes a Room owner and commits successfully
- **THEN** the next list request for both the previous owner and the current owner does not return a payload cached before the transfer

#### Scenario: A room transaction rolls back

- **WHEN** a transaction that creates, updates, or deletes a Room rolls back
- **THEN** the affected owners' room-list cache versions remain unchanged

### Requirement: Cache outage fallback

The system SHALL treat Redis errors during room-list cache reads, writes, version lookups, and invalidation as cache misses. A Redis error SHALL NOT change the JSON response contract, prevent a Room transaction from committing, or prevent a Room list response from being produced from the database.

#### Scenario: Redis is unavailable during a list request

- **WHEN** the room-list data endpoint encounters a Redis error while reading or writing a cached payload
- **THEN** it returns the correctly generated JSON payload from the database

#### Scenario: Redis is unavailable during room creation

- **WHEN** Redis reports an error while the post-commit invalidation for a Room creation runs
- **THEN** the Room creation remains committed and the caller receives the normal creation outcome
