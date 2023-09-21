-- Created By:    Cristian Scutaru
-- Creation Date: Sep 2023
-- Company:       XtractPro Software

CREATE OR REPLACE DATABASE streamlit_erd_viewer;

GRANT USAGE ON DATABASE streamlit_erd_viewer TO ROLE public;
GRANT USAGE ON SCHEMA streamlit_erd_viewer.public TO ROLE public;

CREATE STAGE stage
    directory = (enable=true)
    file_format = (type=CSV field_delimiter=None record_delimiter=None);

PUT file://C:\Projects\streamlit-apps\streamlit-erd-viewer\main.py @stage
    overwrite=true auto_compress=false;

CREATE STREAMLIT streamlit_erd_viewer
    ROOT_LOCATION = '@streamlit_erd_viewer.public.stage'
    MAIN_FILE = '/main.py'
    QUERY_WAREHOUSE = "COMPUTE_WH";
SHOW STREAMLITS;
