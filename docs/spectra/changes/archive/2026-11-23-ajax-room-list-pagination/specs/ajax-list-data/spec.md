## Purpose

Dynamic data lists retrieve changing collections through AJAX instead of embedding the collection in the initial HTML document. This capability establishes consistent pagination and visible request states for future list interfaces.

## ADDED Requirements

### Requirement: Dynamic list data retrieval

The system SHALL retrieve every dynamic data list through an AJAX data endpoint after the list page has loaded. A dynamic data list is a collection whose contents vary with persisted data, the authenticated user, or user-supplied query parameters. Static navigation, fixed form options, and content that does not vary by a data source SHALL NOT be treated as dynamic data lists.

#### Scenario: A list page loads dynamic data

- **WHEN** an authenticated user opens a page containing a dynamic data list
- **THEN** the document provides the list interface and the browser retrieves the list items from an AJAX data endpoint

#### Scenario: A static navigation menu is rendered

- **WHEN** a page renders a fixed navigation menu
- **THEN** the menu is not required to use an AJAX data endpoint

### Requirement: Dynamic list pagination contract

The system SHALL paginate dynamic data lists on the server. Each successful list-data response SHALL identify the current page, page size, total item count, total page count, and whether a previous or next page exists.

#### Scenario: A list has more items than its page size

- **WHEN** a client requests a page from a dynamic list with more matching items than one page contains
- **THEN** the response contains only the requested page items and includes enough pagination metadata for the client to request adjacent pages

### Requirement: Dynamic list request states

The system SHALL present distinct states for initial loading, updating an already rendered list, successful empty results, and request failure. A later request failure SHALL retain the last successfully rendered list and provide an explicit retry action. A cancelled obsolete request SHALL NOT present an error state.

#### Scenario: Initial list request is pending

- **WHEN** the first AJAX request for a list is in progress
- **THEN** the interface indicates that list data is loading and does not represent the pending state as an empty result

#### Scenario: A search returns no matching items

- **WHEN** a successful list-data response has no items
- **THEN** the interface displays an empty-result state rather than a request-failure state

#### Scenario: A later page request fails

- **WHEN** a request made after a successful list render fails
- **THEN** the interface retains the successful list, communicates the failure, and provides a retry action

#### Scenario: A superseded request is cancelled

- **WHEN** a newer list request replaces an in-flight request
- **THEN** cancellation of the older request does not display a request-failure state
