WITH launch_details AS (
    SELECT
        json_extract_scalar(launch_data, '$.id') AS launch_id,
        json_extract_scalar(launch_data, '$.launchpad') AS launchpad_id,
        CAST(json_extract(launch_data, '$.payloads') AS ARRAY(JSON)) as payloads
    FROM
        postgresql.public.raw_launches
),
launch_total_mass AS (
    SELECT
        ld.launch_id,
        ld.launchpad_id,
        SUM(CAST(json_extract_scalar(p.payload, '$.mass_kg') AS DOUBLE)) as total_mass
    FROM
        launch_details ld
    LEFT JOIN
        UNNEST(ld.payloads) AS p(payload) ON true
    GROUP BY
        ld.launch_id, ld.launchpad_id
)
SELECT
    launchpad_id,
    COUNT(launch_id) AS total_launches,
    AVG(COALESCE(total_mass, 0)) AS average_payload_mass_kg
FROM
    launch_total_mass
GROUP BY
    launchpad_id
ORDER BY
    total_launches DESC;
