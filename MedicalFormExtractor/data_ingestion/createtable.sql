-- Table: public.MedicalInfoExtractData

-- DROP TABLE IF EXISTS public."MedicalInfoExtractData";

CREATE TABLE IF NOT EXISTS public."MedicalInfoExtractData"
(
    record_id serial primary key,
    s3_path text COLLATE pg_catalog."default",
    patient_name text COLLATE pg_catalog."default",
    patient_dob text COLLATE pg_catalog."default",
    patient_mrn text COLLATE pg_catalog."default",
    patient_gender text COLLATE pg_catalog."default",
    patient_phone text COLLATE pg_catalog."default",
    patient_address text COLLATE pg_catalog."default",
    patient_city text COLLATE pg_catalog."default",
    patient_state text COLLATE pg_catalog."default",
    patient_st_zip text COLLATE pg_catalog."default",
    ref_to_name text COLLATE pg_catalog."default",
    ref_date text COLLATE pg_catalog."default",
    ref_to_phone text COLLATE pg_catalog."default"
    ref_to_fax text COLLATE pg_catalog."default",
    ref_to_address text COLLATE pg_catalog."default",
    ref_to_city text COLLATE pg_catalog."default",
    ref_to_st_zip text COLLATE pg_catalog."default",
    ref_to_state text COLLATE pg_catalog."default",
    ref_by_name text COLLATE pg_catalog."default",
    ref_by_phone text COLLATE pg_catalog."default",
    ref_by_fax text COLLATE pg_catalog."default",
    ref_by_address text COLLATE pg_catalog."default",
    ref_by_city text COLLATE pg_catalog."default",
    ref_by_st_zip text COLLATE pg_catalog."default",
    ref_by_state text COLLATE pg_catalog."default",
    primary_billing_diagnosis text COLLATE pg_catalog."default",
    ref_reason text COLLATE pg_catalog."default",
    icd_code text COLLATE pg_catalog."default",
    icd_description text COLLATE pg_catalog."default",
    icd_code_list jsonb,
    icd_info text COLLATE pg_catalog."default"
)
TABLESPACE pg_default;

ALTER TABLE IF EXISTS public."MedicalInfoExtractData"
    OWNER to postgres;

COMMENT ON TABLE public."MedicalInfoExtractData"
    IS 'table that conntains patient and refferer data
';