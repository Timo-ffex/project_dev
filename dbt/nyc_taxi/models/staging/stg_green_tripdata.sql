{# -- import raw_listings
WITH raw_listings AS (
        SELECT * FROM {{ source('staging', 'yellow') }}
)
SELECT 
   *
FROM raw_listings
LIMIT 5 #}
