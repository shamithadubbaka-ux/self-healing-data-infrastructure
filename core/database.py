import sqlite3

import pandas as pd

from config.settings import DATABASE_PATH


def get_connection():

    return sqlite3.connect(DATABASE_PATH)


def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS pipeline_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT,
            start_time TEXT,
            end_time TEXT,
            status TEXT,
            rows_processed INTEGER,
            rows_failed INTEGER,
            healing_actions INTEGER,
            message TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS quality_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT,
            metric_name TEXT,
            metric_value REAL,
            status TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS healing_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT,
            timestamp TEXT,
            issue_type TEXT,
            action TEXT,
            status TEXT,
            details TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS lineage_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT,
            timestamp TEXT,
            source TEXT,
            transformation TEXT,
            destination TEXT
        )
        """
    )

    connection.commit()
    connection.close()


def save_pipeline_run(
    run_id,
    start_time,
    end_time,
    status,
    rows_processed,
    rows_failed,
    healing_actions,
    message,
):

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO pipeline_runs (
            run_id,
            start_time,
            end_time,
            status,
            rows_processed,
            rows_failed,
            healing_actions,
            message
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            run_id,
            start_time,
            end_time,
            status,
            rows_processed,
            rows_failed,
            healing_actions,
            message,
        ),
    )

    connection.commit()
    connection.close()


def save_quality_metric(
    run_id,
    metric_name,
    metric_value,
    status,
):

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO quality_metrics (
            run_id,
            metric_name,
            metric_value,
            status
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            run_id,
            metric_name,
            metric_value,
            status,
        ),
    )

    connection.commit()
    connection.close()


def save_healing_event(
    run_id,
    timestamp,
    issue_type,
    action,
    status,
    details,
):

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO healing_events (
            run_id,
            timestamp,
            issue_type,
            action,
            status,
            details
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            run_id,
            timestamp,
            issue_type,
            action,
            status,
            details,
        ),
    )

    connection.commit()
    connection.close()


def save_lineage_event(
    run_id,
    timestamp,
    source,
    transformation,
    destination,
):

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO lineage_events (
            run_id,
            timestamp,
            source,
            transformation,
            destination
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            run_id,
            timestamp,
            source,
            transformation,
            destination,
        ),
    )

    connection.commit()
    connection.close()


def read_table(table_name):

    connection = get_connection()

    dataframe = pd.read_sql_query(
        f"SELECT * FROM {table_name}",
        connection,
    )

    connection.close()

    return dataframe