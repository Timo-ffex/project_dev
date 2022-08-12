-- Create external table

CREATE OR REPLACE EXTERNAL TABLE `dit-dev-project.trips_data_all.external_yellow_tripdata`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://dit_nyc_trip_data_lake/raw/yellow_tripdata/*.parquet']
);



CREATE OR REPLACE EXTERNAL TABLE `dit-dev-project.trips_data_all.external_yellow_tripdata_v2`(
  VendorID BIGINT, 
	tpep_pickup_datetime TIMESTAMP, 
	tpep_dropoff_datetime TIMESTAMP, 
	passenger_count FLOAT64, 
	trip_distance FLOAT64, 
	RatecodeID FLOAT64, 
	store_and_fwd_flag STRING, 
	PULocationID BIGINT, 
	DOLocationID BIGINT, 
	payment_type BIGINT, 
	fare_amount FLOAT64, 
	extra FLOAT64, 
	mta_tax FLOAT64, 
	tip_amount FLOAT64, 
	tolls_amount FLOAT64, 
	improvement_surcharge FLOAT64, 
	total_amount FLOAT64, 
	congestion_surcharge FLOAT64, 
	airport_fee FLOAT64
)
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://dit_nyc_trip_data_lake/raw/yellow_tripdata/*.parquet']
);


SELECT * FROM dit-dev-project.trips_data_all.external_yellow_tripdata limit 10;


-- Create a non partitioned table from external table
CREATE OR REPLACE TABLE dit-dev-project.trips_data_all.yellow_tripdata_non_partitoned AS
SELECT * FROM dit-dev-project.trips_data_all.external_yellow_tripdata;


-- Check yello trip data
SELECT * FROM dit-dev-project.trips_data_all.external_yellow_tripdata limit 10;

-- Create a non partitioned table from external table
CREATE OR REPLACE TABLE dit-dev-project.trips_data_all.yellow_tripdata_non_partitoned AS
SELECT * FROM dit-dev-project.trips_data_all.external_yellow_tripdata;


-- Create a partitioned table from external table
CREATE OR REPLACE TABLE dit-dev-project.trips_data_all.yellow_tripdata_partitoned
PARTITION BY
  DATE(tpep_pickup_datetime) AS
SELECT * FROM dit-dev-project.trips_data_all.external_yellow_tripdata;

-- Impact of partition
-- Scanning 1.6GB of data
SELECT DISTINCT(VendorID)
FROM dit-dev-project.trips_data_all.yellow_tripdata_non_partitoned
WHERE DATE(tpep_pickup_datetime) BETWEEN '2019-06-01' AND '2019-06-30';

-- Scanning ~106 MB of DATA
SELECT DISTINCT(VendorID)
FROM dit-dev-project.trips_data_all.yellow_tripdata_partitoned
WHERE DATE(tpep_pickup_datetime) BETWEEN '2019-06-01' AND '2019-06-30';

-- Let's look into the partitons
SELECT table_name, partition_id, total_rows
FROM `trips_data_all.INFORMATION_SCHEMA.PARTITIONS`
WHERE table_name = 'yellow_tripdata_partitoned'
ORDER BY total_rows DESC;

-- Creating a partition and cluster table
CREATE OR REPLACE TABLE dit-dev-project.trips_data_all.yellow_tripdata_partitoned_clustered
PARTITION BY DATE(tpep_pickup_datetime)
CLUSTER BY VendorID AS
SELECT * FROM dit-dev-project.trips_data_all.external_yellow_tripdata;

-- Query scans 1.1 GB
SELECT count(*) as trips
FROM dit-dev-project.trips_data_all.yellow_tripdata_partitoned
WHERE DATE(tpep_pickup_datetime) BETWEEN '2019-06-01' AND '2020-12-31'
  AND VendorID=1;

-- Query scans 864.5 MB
SELECT count(*) as trips
FROM dit-dev-project.trips_data_all.yellow_tripdata_partitoned_clustered
WHERE DATE(tpep_pickup_datetime) BETWEEN '2019-06-01' AND '2020-12-31'
  AND VendorID=1;

  My Mic Password, for now