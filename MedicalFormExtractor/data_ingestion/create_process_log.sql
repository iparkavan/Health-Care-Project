CREATE TABLE public.process_log (
	request_uuid text NULL,
	uploaded_s3_path text NULL,
	event_received timestamp NULL,
	submitted_to_textract timestamp NULL,
	response_from_textract timestamp NULL,
	transformation_start timestamp NULL,
	transformation_end timestamp NULL,
	follow_up_reason text NULL,
	event_completed timestamp NULL,
    primary key(request_uuid)
);