
CREATE OR REPLACE FUNCTION protection_level.api_acp_stats(
	id text DEFAULT NULL::text)
    RETURNS SETOF protection_level.acp_stats
    LANGUAGE 'plpgsql'

    COST 100
    VOLATILE 
    ROWS 1000
    
AS $BODY$
BEGIN
IF $1 is null THEN
      RETURN query SELECT * FROM protection_level.acp_stats;
ELSE
      RETURN query SELECT * FROM protection_level.acp_stats where acp_stats.id=$1;
END IF;
END
$BODY$;

ALTER FUNCTION protection_level.api_acp_stats(text)
    OWNER TO biopama_api_user;

COMMENT ON FUNCTION protection_level.api_acp_stats(text)
    IS 'BIOPAMA Protection Statistics at ACP level. Data is updated every month. Use this API to retrieve ACP data.';

CREATE OR REPLACE FUNCTION protection_level.api_country_list_stats(
	region_acp text DEFAULT NULL::text)
    RETURNS SETOF protection_level.country_stats
    LANGUAGE 'plpgsql'

    COST 100
    VOLATILE 
    ROWS 1000
    
AS $BODY$
BEGIN
IF $1 is null THEN
      RETURN query SELECT * FROM protection_level.country_stats;
ELSE
      RETURN query SELECT * FROM protection_level.country_stats where country_stats.region_acp=$1;
END IF;
END
$BODY$;

ALTER FUNCTION protection_level.api_country_list_stats(text)
    OWNER TO biopama_api_user;

COMMENT ON FUNCTION protection_level.api_country_list_stats(text)
    IS 'BIOPAMA Protection Statistics at country level. It returns a list of countries and related information. Data is updated every month
Use this API to retrieve all data or single country data given the parameter: region_acp';


CREATE OR REPLACE FUNCTION protection_level.api_country_stats(
	iso3 text DEFAULT NULL::text)
    RETURNS SETOF protection_level.country_stats
    LANGUAGE 'plpgsql'

    COST 100
    VOLATILE 
    ROWS 1000
    
AS $BODY$
BEGIN
IF $1 is null THEN
      RETURN query SELECT * FROM protection_level.country_stats;
ELSE
      RETURN query SELECT * FROM protection_level.country_stats where country_stats.iso3=$1;
END IF;
END
$BODY$;

ALTER FUNCTION protection_level.api_country_stats(text)
    OWNER TO biopama_api_user;

COMMENT ON FUNCTION protection_level.api_country_stats(text)
    IS 'BIOPAMA Protection Statistics at country level. It returns a list of countries and related information. Data is updated every month
Use this API to retrieve all data or single country data given the parameter: iso3';

CREATE OR REPLACE FUNCTION protection_level.api_region_stats(
	region_acp text DEFAULT NULL::text)
    RETURNS SETOF protection_level.region_stats
    LANGUAGE 'plpgsql'

    COST 100
    VOLATILE 
    ROWS 1000
    
AS $BODY$
BEGIN
IF $1 is null THEN
      RETURN query SELECT * FROM protection_level.region_stats;
ELSE
      RETURN query SELECT * FROM protection_level.region_stats where region_stats.region_acp=$1;
END IF;
END
$BODY$;

ALTER FUNCTION protection_level.api_region_stats(text)
    OWNER TO biopama_api_user;

COMMENT ON FUNCTION protection_level.api_region_stats(text)
    IS 'BIOPAMA Protection Statistics at regional level. Data is uprated every month
Use this API to retrieve all data or single country data given the parameter: region_acp';
