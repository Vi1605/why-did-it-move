"""Load the CSV into a DuckDB database so we can query it with SQL."""
import duckdb


def main():
    con = duckdb.connect("data/renewals.duckdb")
    con.execute(
        "CREATE OR REPLACE TABLE renewals AS "
        "SELECT * FROM read_csv_auto('data/renewals.csv')"
    )
    n = con.execute("SELECT COUNT(*) FROM renewals").fetchone()[0]
    print(f"Loaded {n:,} rows into data/renewals.duckdb")
    con.close()


if __name__ == "__main__":
    main()

