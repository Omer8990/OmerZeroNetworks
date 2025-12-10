WITH launch_dates AS (
    SELECT
        CAST(json_extract_scalar(launch_data, '$.static_fire_date_utc') AS VARCHAR) AS static_fire_date_utc,
        CAST(json_extract_scalar(launch_data, '$.date_utc') AS VARCHAR) AS date_utc
    FROM
        postgresql.public.raw_launches
    WHERE
        json_extract_scalar(launch_data, '$.static_fire_date_utc') IS NOT NULL
),
time_diff AS (
    SELECT
        CAST(SUBSTR(date_utc, 1, 4) AS INTEGER) AS launch_year,
        date_diff('hour', from_iso8601_timestamp(static_fire_date_utc), from_iso8601_timestamp(date_utc)) AS diff_hours
    FROM
        launch_dates
)
SELECT
    launch_year,
    AVG(diff_hours) AS average_delay_hours,
    MAX(diff_hours) AS max_delay_hours
FROM
    time_diff
GROUP BY
    launch_year
ORDER BY
    launch_year;
