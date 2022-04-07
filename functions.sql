CREATE OR REPLACE VIEW protection_level.v_country_stats AS 
 
	 with country as(
	 select isoa3_id, name from ancillary.gaul_acp
	 )
	select 
	id as id,
	iso3 as iso3,
	grouping_i as "grouping",
	region_acp as region,
	count as total_count,
	terrestrial_count as ter_count,
	marine_count as mar_count,
	costal_count as cos_count,
	country_area_km as ter_area,
	prot_km as ter_area_prot,
	prot_perc as ter_perc_prot,
	country_mar_area_km as mar_area,
	prot_mar_km as mar_area_prot,
	prot_mar_perc as mar_perc_prot,
	country.name
	    FROM protection_level.country_stats
		
LEFT JOIN country on country_stats.iso3::character varying = country.isoa3_id::character varying



create or replace view protection_level.v_region_stats as 
select 
id as id,
region_acp as region,
count_reg_tot as total_count,
reg_terr_count as ter_count,
reg_mar_count as mar_count,
reg_costal_count as cos_count,
reg_land_area as ter_area,
reg_land_area_prot as ter_area_prot,
reg_terr_prot_perc as ter_perc_prot,
reg_mar_area as mar_area,
reg_mar_area_prot as mar_area_prot,
reg_mar_prot_perc as mar_perc_prot
from protection_level.region_stats;

create or replace view protection_level.v_acp_stats as 
select 
id as id,
tot_count_acp as total_count,
terr_count_acp as ter_count,
mar_count_acp as mar_count,
costal_count_acp as cos_count,
ter_area_acp as ter_area,
ter_area_prot_acp as ter_area_prot,
ter_prot_perc_acp as ter_perc_prot,
mar_area_acp as mar_area,
mar_area_prot_acp as mar_area_prot,
mar_prot_perc_acp as mar_perc_prot
from protection_level.acp_stats

--ACP API

CREATE OR REPLACE FUNCTION protection_level.api_acp_stats(
	id text DEFAULT NULL::text)
    RETURNS SETOF protection_level.v_acp_stats
    LANGUAGE 'plpgsql'

    COST 100
    VOLATILE 
    ROWS 1000
    
AS $BODY$
BEGIN
IF $1 is null THEN
      RETURN query SELECT * FROM protection_level.v_acp_stats;
ELSE
      RETURN query SELECT * FROM protection_level.v_acp_stats where v_acp_stats.id=$1;
END IF;
END
$BODY$;

ALTER FUNCTION protection_level.api_acp_stats(text)
    OWNER TO biopama_api_user;

COMMENT ON FUNCTION protection_level.api_acp_stats(text)
    IS 'BIOPAMA Protection Statistics at ACP level. Data is updated every month. Use this API to retrieve ACP data.';
    
--COUNTRY LIST API    

CREATE OR REPLACE FUNCTION protection_level.api_country_list_stats(
	region text DEFAULT NULL::text)
    RETURNS SETOF protection_level.v_country_stats
    LANGUAGE 'plpgsql'

    COST 100
    VOLATILE 
    ROWS 1000
    
AS $BODY$
BEGIN
IF $1 is null THEN
      RETURN query SELECT * FROM protection_level.v_country_stats;
ELSE
      RETURN query SELECT * FROM protection_level.v_country_stats where v_country_stats.region=$1;
END IF;
END
$BODY$;

ALTER FUNCTION protection_level.api_country_list_stats(text)
    OWNER TO biopama_api_user;

COMMENT ON FUNCTION protection_level.api_country_list_stats(text)
    IS 'BIOPAMA Protection Statistics at country level. It returns a list of countries and related information. Data is updated every month
Use this API to retrieve all data or single country data given the parameter: region_acp';

--COUNTRY API

CREATE OR REPLACE FUNCTION protection_level.api_country_stats(
	iso3 text DEFAULT NULL::text)
    RETURNS SETOF protection_level.v_country_stats
    LANGUAGE 'plpgsql'

    COST 100
    VOLATILE 
    ROWS 1000
    
AS $BODY$
BEGIN
IF $1 is null THEN
      RETURN query SELECT * FROM protection_level.v_country_stats;
ELSE
      RETURN query SELECT * FROM protection_level.v_country_stats where v_country_stats.iso3=$1;
END IF;
END
$BODY$;

ALTER FUNCTION protection_level.api_country_stats(text)
    OWNER TO biopama_api_user;

COMMENT ON FUNCTION protection_level.api_country_stats(text)
    IS 'BIOPAMA Protection Statistics at country level. It returns a list of countries and related information. Data is updated every month
Use this API to retrieve all data or single country data given the parameter: iso3';

--REGION API

CREATE OR REPLACE FUNCTION protection_level.api_region_stats(
	region text DEFAULT NULL::text)
    RETURNS SETOF protection_level.v_region_stats
    LANGUAGE 'plpgsql'

    COST 100
    VOLATILE 
    ROWS 1000
    
AS $BODY$
BEGIN
IF $1 is null THEN
      RETURN query SELECT * FROM protection_level.v_region_stats;
ELSE
      RETURN query SELECT * FROM protection_level.v_region_stats where v_region_stats.region=$1;
END IF;
END
$BODY$;

ALTER FUNCTION protection_level.api_region_stats(text)
    OWNER TO biopama_api_user;

COMMENT ON FUNCTION protection_level.api_region_stats(text)
    IS 'BIOPAMA Protection Statistics at regional level. Data is uprated every month
Use this API to retrieve all data or single country data given the parameter: region_acp';

--IUCN CATS

CREATE OR REPLACE FUNCTION protection_level.api_region_iucn_cat(
	region_acp text DEFAULT NULL::text)
    RETURNS SETOF protection_level.region_iucn_cat
    LANGUAGE 'plpgsql'

    COST 100
    VOLATILE 
    ROWS 1000
    
AS $BODY$
BEGIN
IF $1 is null THEN
      RETURN query SELECT * FROM protection_level.region_iucn_cat;
ELSE
      RETURN query SELECT * FROM protection_level.region_iucn_cat where region_iucn_cat.region_acp=$1;
END IF;
END
$BODY$;

ALTER FUNCTION protection_level.api_region_iucn_cat(text)
    OWNER TO biopama_api_user;

COMMENT ON FUNCTION protection_level.api_region_iucn_cat(text)
    IS 'BIOPAMA Protection Statistics at regional level. Data is uprated every month
Use this API to retrieve all data or single country data given the parameter: region_acp';


