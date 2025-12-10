WITH launch_times AS (
    SELECT
        CAST(json_extract_scalar(launch_data, '$.static_fire_date_utc') AS VARCHAR) AS static_fire_date_utc,
        CAST(json_extract_scalar(launch_data, '$.date_utc') AS VARCHAR) AS date_utc
    FROM
        postgresql.public.raw_launches
),
time_diffs AS (
    SELECT
        EXTRACT(YEAR FROM from_iso8601_timestamp(date_utc)) AS launch_year,
        date_diff('hour', from_iso8601_timestamp(static_fire_date_utc), from_iso8601_timestamp(date_utc)) AS delay_hours
    FROM
        launch_times
    WHERE
        static_fire_date_utc IS NOT NULL
        AND from_iso8601_timestamp(date_utc) > from_iso8601_timestamp(static_fire_date_utc)
)
SELECT
    launch_year,
    AVG(delay_hours) AS average_delay_hours,
    MAX(delay_hours) AS max_delay_hours
FROM
    time_diffs
WHERE
    delay_hours >= 0
GROUP BY
    launch_year
ORDER BY
    launch_year;