# Expense Manager API

Initial Flask backend foundation for an authenticated expense manager. The domain
starts with users and the expense `Resource` records they own.

## Setup

The project targets Python 3.8.13 as declared in the `Pipfile`.

```bash
pipenv install
pipenv run flask --app server.app db upgrade
pipenv run flask --app server.app seed
pipenv run flask --app server.app run --debug
```

The API health check is available at `GET /`.

## Data model

- `User`: `id`, `username`, `email`, `password_hash`, `created_at`
- `Resource`: `id`, `title`, `amount`, `category`, `expense_date`, `notes`,
  `created_at`, `user_id`

Each resource belongs to exactly one user through `resources.user_id`. A user
has many resources through `users.resources`; deleting a user deletes their
resources as well.

## Database workflow

The checked-in initial migration is already available. After another contributor
changes a model, create and apply a new migration:

```bash
pipenv run flask --app server.app db migrate -m "describe the change"
pipenv run flask --app server.app db upgrade
```

`flask --app server.app seed` is idempotent and adds one demo user plus three
sample resources only when they do not already exist.

## Marshmallow Schemas, Validation & Testing

### Marshmallow Schema

Expense data is handled using Marshmallow through `server/schemas.py`.

The `ExpenseSchema` is responsible for validating incoming expense data, deserializing JSON data into Python data types, and serializing expense records into JSON responses.

The schema includes the following fields:

| Field          | Type     | Validation / Access            |
| -------------- | -------- | ------------------------------ |
| `id`           | Integer  | Read-only                      |
| `title`        | String   | Required, 1–120 characters     |
| `amount`       | Float    | Required, must be 0 or greater |
| `category`     | String   | Required, 1–80 characters      |
| `expense_date` | Date     | Required, valid date           |
| `notes`        | String   | Optional and nullable          |
| `created_at`   | DateTime | Read-only                      |
| `user_id`      | Integer  | Read-only                      |

The `id`, `created_at`, and `user_id` fields use `dump_only=True` so that clients cannot provide or modify these values through expense requests.

### Serialization and Deserialization

Incoming JSON data is deserialized and validated using Marshmallow:

```python
schema.load(data)
```

This converts values such as an ISO-formatted expense date into the appropriate Python data type before the data is stored in the database.

Expense records are serialized for API responses using:

```python
schema.dump(expense)
```

This converts database values into JSON-compatible response data.

### Validation

The API validates expense data before saving it to the database.

Validation rules include:

* Title is required and must contain between 1 and 120 characters.
* Amount is required and cannot be negative.
* Category is required and must contain between 1 and 80 characters.
* Expense date is required and must be a valid date.
* Notes are optional.

Invalid requests return `400 Bad Request` together with the relevant validation errors.

For example, submitting an empty title, negative amount, empty category, and invalid date returned validation errors for all four fields.

### Partial Updates

The PATCH endpoint uses Marshmallow with `partial=True`:

```python
schema.load(data, partial=True)
```

This allows a user to update only the fields they provide without being required to resend all required expense fields.

For example:

```json
{
  "amount": 750,
  "notes": "Updated campus lunch"
}
```

successfully updated only the amount and notes while leaving the other expense fields unchanged.

## API Endpoint Documentation

### Authentication Endpoints

| Method | Endpoint         | Description                       | Success |
| ------ | ---------------- | --------------------------------- | ------: |
| POST   | `/signup`        | Create a user and start a session |     201 |
| POST   | `/login`         | Authenticate a user               |     200 |
| GET    | `/check_session` | Check the current session         |     200 |
| DELETE | `/logout`        | End the current session           |     204 |

### Expense Endpoints

| Method | Endpoint                 | Description                                | Success |
| ------ | ------------------------ | ------------------------------------------ | ------: |
| GET    | `/expenses`              | Retrieve the authenticated user's expenses |     200 |
| POST   | `/expenses`              | Create a new expense                       |     201 |
| PATCH  | `/expenses/<expense_id>` | Partially update an expense                |     200 |
| DELETE | `/expenses/<expense_id>` | Delete an expense                          |     204 |

Expense endpoints require an authenticated session.

### Pagination

The `GET /expenses` endpoint supports pagination using:

```text
/expenses?page=1&per_page=10
```

The response includes:

* `expenses`
* `page`
* `per_page`
* `total`
* `pages`

This allows clients to retrieve expenses in manageable pages.

## API Testing

The API was tested locally using authenticated `curl` requests.

| Test                   | Expected Status | Result |
| ---------------------- | --------------: | ------ |
| User signup            |     201 Created | Passed |
| Create valid expense   |     201 Created | Passed |
| Retrieve expenses      |          200 OK | Passed |
| Create invalid expense | 400 Bad Request | Passed |
| Partial expense update |          200 OK | Passed |
| Invalid partial update | 400 Bad Request | Passed |
| Delete expense         |  204 No Content | Passed |
| Verify deleted expense |          200 OK | Passed |

### Validation Test

An invalid expense containing an empty title, negative amount, empty category, and invalid date was submitted.

The API returned:

```text
400 Bad Request
```

with validation errors for:

* `title`
* `amount`
* `category`
* `expense_date`

### Successful Expense Test

A valid expense was created with:

```json
{
  "title": "Lunch",
  "amount": 500,
  "category": "Food",
  "expense_date": "2026-09-10",
  "notes": "Campus lunch"
}
```

The API returned:

```text
201 Created
```

and serialized the expense correctly as JSON.

### PATCH Test

A partial update changed the amount from `500` to `750` and updated the notes.

The API returned:

```text
200 OK
```

The remaining expense fields were preserved.

An invalid PATCH request containing a negative amount returned:

```text
400 Bad Request
```

with the appropriate Marshmallow validation error.

### DELETE Test

The expense was successfully deleted using:

```text
DELETE /expenses/1
```

The API returned:

```text
204 No Content
```

A subsequent `GET /expenses` request returned an empty expense list with `total: 0`, confirming that the resource had been deleted successfully.

### Postman Testing

The API endpoints can be tested using Postman.

Recommended testing order:

1. `POST /signup`
2. `POST /login`
3. `GET /check_session`
4. `POST /expenses`
5. `GET /expenses`
6. `PATCH /expenses/<expense_id>`
7. `DELETE /expenses/<expense_id>`
8. `GET /expenses` to verify deletion

For authenticated requests, the session cookie from signup or login must be retained and sent with subsequent requests.
