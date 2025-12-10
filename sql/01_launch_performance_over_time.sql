WITH launch_years AS (
    SELECT
        CAST(json_extract_scalar(launch_data, '$.date_utc') AS VARCHAR) AS date_utc_str,
        json_extract_scalar(launch_data, '$.success') AS success_str
    FROM
        postgresql.public.raw_launches
),
parsed_launches AS (
    SELECT
        CAST(SUBSTR(date_utc_str, 1, 4) AS INTEGER) AS launch_year,
        CAST(success_str AS BOOLEAN) AS success
    FROM
        launch_years
)
SELECT
    launch_year,
    COUNT(*) AS total_launches,
    SUM(CASE WHEN success = TRUE THEN 1 ELSE 0 END) AS successful_launches,
    CAST(SUM(CASE WHEN success = TRUE THEN 1 ELSE 0 END) AS DOUBLE) * 100.0 / COUNT(*) AS success_rate
FROM
    parsed_launches
GROUP BY
    launch_year
ORDER BY
    launch_year;
