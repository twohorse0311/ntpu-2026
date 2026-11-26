## Purpose

The room list API provides authenticated clients with paginated, searchable room data for the current owner. It enables the room list interface to update without a full document reload while preserving room ownership boundaries.

## ADDED Requirements

### Requirement: Authenticated room list data endpoint

The system SHALL provide `GET /majon/rooms/data/` as a JSON endpoint for room-list data. An authenticated request SHALL receive only rooms owned by the requesting user, ordered by newest creation time first. An unauthenticated request SHALL receive a JSON response with HTTP 401 and SHALL NOT receive an HTML login document.

#### Scenario: An owner requests room data

- **WHEN** an authenticated user requests the room-list data endpoint
- **THEN** every returned item belongs to that user and is ordered from newest to oldest

#### Scenario: An unauthenticated client requests room data

- **WHEN** an unauthenticated client requests the room-list data endpoint
- **THEN** the endpoint returns HTTP 401 with a JSON response

### Requirement: Room list search and pagination

The endpoint SHALL trim the optional `q` parameter and use a non-empty value to match room names case-insensitively. The endpoint SHALL return 10 items per page and SHALL normalize a missing, non-integer, or value below 1 `page` parameter to page 1. A page above the final available page SHALL return the final page.

#### Scenario: A client searches room names

- **WHEN** a client requests the endpoint with `q` equal to a non-empty room-name fragment
- **THEN** the response contains only the requesting user's rooms whose names contain that fragment without case sensitivity

#### Scenario: A client requests boundary pages

- **WHEN** a client requests a missing, invalid, below-one, or beyond-final page number
- **THEN** the endpoint returns page 1 for the first three cases and the final page for the beyond-final case

##### Example: page normalization

| Requested `page` | Returned page | Condition |
| --- | --- | --- |
| omitted | 1 | default page |
| `abc` | 1 | non-integer value |
| `0` | 1 | below-one value |
| `99` | final page | list has fewer than 99 pages |

### Requirement: Room list response shape

Each successful room-list response SHALL contain `items`, `page`, `page_size`, `total_count`, `total_pages`, `has_previous`, and `has_next`. Each item SHALL contain `id`, `name`, `code`, `owner_display_name`, and `detail_url`, where `detail_url` addresses that room's detail page and `owner_display_name` uses the owner's display name or username when no display name exists.

#### Scenario: A client receives a populated page

- **WHEN** the endpoint returns one or more rooms
- **THEN** the response includes the required pagination fields and every item includes the required room display and detail-link fields

#### Scenario: A room owner has no display name

- **WHEN** a returned room owner's profile has no display name
- **THEN** the item's `owner_display_name` equals the owner's username
