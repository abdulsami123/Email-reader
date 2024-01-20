from google.cloud import aiplatform
from google.auth import credentials
from typing import Optional

def init_sample(
    project: Optional[str] = "My First Project",
    location: Optional[str] = "us-central1",
    experiment: Optional[str] = "experiment_reader",
    staging_bucket: Optional[str] = "readerbucket0000",
    credentials: Optional[credentials.Credentials] = "C:\\Users\\Abdul Sami\\Downloads",
    encryption_spec_key_name: Optional[str] = "vertexreader@hopeful-sunset-411201.iam.gserviceaccount.com",
):
    aiplatform.init(
        project=project,
        location=location,
        experiment=experiment,
        staging_bucket=staging_bucket,
        credentials=credentials,
        encryption_spec_key_name=encryption_spec_key_name,
        service_account=service_account,
    )
