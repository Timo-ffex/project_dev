-- import raw_listings
WITH tripdata AS (
        SELECT * FROM {{ source('staging', 'yellow') }}
)
SELECT 
   *
FROM tripdata
LIMIT 100;
