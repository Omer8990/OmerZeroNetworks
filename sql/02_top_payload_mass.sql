WITH launch_payloads AS (
    SELECT
        json_extract_scalar(launch_data, '$.id') AS launch_id, -- Use ID for uniqueness
        json_extract_scalar(launch_data, '$.name') AS launch_name,
        CAST(json_extract(launch_data, '$.payloads') AS ARRAY(JSON)) AS payloads_array
    FROM
        postgresql.public.raw_launches
),
payload_masses AS (
    SELECT
        launch_id,
        launch_name,
        CAST(json_extract_scalar(payload, '$.mass_kg') AS DOUBLE) AS payload_mass_kg
    FROM
        launch_payloads
    CROSS JOIN
        UNNEST(payloads_array) AS t(payload)
    WHERE json_extract_scalar(payload, '$.mass_kg') IS NOT NULL
)
SELECT
    launch_name,
    launch_id,
    SUM(payload_mass_kg) AS total_payload_mass_kg
FROM
    payload_masses
GROUP BY
    launch_id, launch_name -- Group by both ID and name
ORDER BY
    total_payload_mass_kg DESC
LIMIT 5;
