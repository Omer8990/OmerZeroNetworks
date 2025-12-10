-- This script creates the launch_aggregates table if it does not already exist.
-- This table stores aggregated metrics calculated from the raw_launches table.

CREATE TABLE IF NOT EXISTS launch_aggregates (
    id INT PRIMARY KEY,
    total_launches BIGINT,
    successful_launches BIGINT,
    average_payload_mass_kg DOUBLE PRECISION,
    last_updated_utc TIMESTAMP WITH TIME ZONE
);
