from database.connection import SCHEMA_VERSION, database_connection, initialize_database


def test_initialize_database_applies_schema_once(tmp_path):
    database_path = tmp_path / "scamshield.db"

    initialize_database(database_path)
    initialize_database(database_path)

    with database_connection(database_path) as connection:
        version = connection.execute(
            "SELECT MAX(version) AS version FROM schema_migrations"
        ).fetchone()["version"]
        tables = {
            row["name"]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }

    assert version == SCHEMA_VERSION
    assert "schema_migrations" in tables
    assert "app_settings" in tables


def test_connection_enforces_foreign_keys(tmp_path):
    database_path = tmp_path / "foreign_keys.db"
    initialize_database(database_path)

    with database_connection(database_path) as connection:
        enabled = connection.execute("PRAGMA foreign_keys").fetchone()[0]

    assert enabled == 1


def test_database_path_directory_is_created(tmp_path):
    database_path = tmp_path / "nested" / "folder" / "app.db"
    initialize_database(database_path)
    assert database_path.exists()


def test_reinitialization_preserves_existing_settings(tmp_path):
    database_path = tmp_path / "preserve.db"
    initialize_database(database_path)

    with database_connection(database_path) as connection:
        connection.execute(
            "INSERT INTO app_settings(setting_key, setting_value) VALUES (?, ?)",
            ("test-key", "keep-me"),
        )

    initialize_database(database_path)

    with database_connection(database_path) as connection:
        row = connection.execute(
            "SELECT setting_value FROM app_settings WHERE setting_key = ?",
            ("test-key",),
        ).fetchone()

    assert row["setting_value"] == "keep-me"


def test_migration_four_creates_case_tables_and_preserves_prior_data(tmp_path):
    database_path = tmp_path / "upgrade.db"
    initialize_database(database_path)
    with database_connection(database_path) as connection:
        connection.execute(
            "INSERT INTO app_settings(setting_key, setting_value) VALUES (?, ?)",
            ("existing", "preserve"),
        )
    initialize_database(database_path)
    with database_connection(database_path) as connection:
        setting = connection.execute(
            "SELECT setting_value FROM app_settings WHERE setting_key='existing'"
        ).fetchone()["setting_value"]
        tables = {
            row["name"] for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
    assert setting == "preserve"
    assert {"investigation_cases", "case_evidence", "case_events"}.issubset(tables)
