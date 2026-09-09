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
