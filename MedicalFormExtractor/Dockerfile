FROM public.ecr.aws/lambda/python:3.8

# Copy function code
COPY lambda_function.py ${LAMBDA_TASK_ROOT}
#COPY data_ingest.py ${LAMBDA_TASK_ROOT}
COPY entities_analysis ${LAMBDA_TASK_ROOT}/entities_analysis
COPY medicalformextractor ${LAMBDA_TASK_ROOT}/medicalformextractor
COPY *.json ${LAMBDA_TASK_ROOT}/
#COPY *.env ${LAMBDA_TASK_ROOT}/
COPY *.xml ${LAMBDA_TASK_ROOT}/
# Install the function's dependencies using file requirements.txt
# from your project folder.

COPY requirements.txt  .
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "lambda_function.lambda_handler" ]
