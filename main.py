import os
from azure.identity import ClientSecretCredential 
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.datafactory import DataFactoryManagementClient
from azure.mgmt.datafactory.models import *
from datetime import datetime, timedelta
import time
from dotenv import load_dotenv


def print_item(group):
    """Print an Azure object instance."""
    print(f"\tName: {group.name}")
    print(f"\tId: {group.id}")
    if hasattr(group, 'location'):
        print(f"\tLocation: {group.location}")
    if hasattr(group, 'tags'):
        print(f"\tTags: {group.tags}")
    if hasattr(group, 'properties'):
        print_properties(group.properties)

def print_properties(props):
    """Print a ResourceGroup properties instance."""
    if props and hasattr(props, 'provisioning_state') and props.provisioning_state:
        print("\tProperties:")
        print(f"\t\tProvisioning State: {props.provisioning_state}")
    print("\n\n")

def print_activity_run_details(activity_run):
    """Print activity run details."""
    print("\n\tActivity run details\n")
    print(f"\tActivity run status: {activity_run.status}")
    if activity_run.status == 'Succeeded':
        print(f"\tNumber of bytes read: {activity_run.output['dataRead']}")
        print(f"\tNumber of bytes written: {activity_run.output['dataWritten']}")
        print(f"\tCopy duration: {activity_run.output['copyDuration']}")
    else:
        print(f"\tErrors: {activity_run.error['message']}")

def main():
    """Entry point"""
    # Azure subscription ID
    subscription_id = os.getenv('SUBSCRIPTION_ID')

    # This program creates this resource group. If it's an existing resource group, comment out the code that creates the resource group
    rg_name = 'temp_devopsdatafactory'

    # The data factory name. It must be globally unique.
    df_name = 'a9odevopsadf01'

    # Specify your Active Directory client ID, client secret, and tenant ID
    credentials = ClientSecretCredential(
        client_id=os.getenv('CLIENT_ID'),
        client_secret=os.getenv('CLIENT_SECRET'),
        tenant_id=os.getenv('TENANT_ID')
    )

    # Specify following for Soverign Clouds, import right cloud constant and then use it to connect.
    # from msrestazure.azure_cloud import AZURE_PUBLIC_CLOUD as CLOUD
    # credentials = DefaultAzureCredential(authority=CLOUD.endpoints.active_directory, tenant_id=tenant_id)

    resource_client = ResourceManagementClient(credentials, subscription_id)
    adf_client = DataFactoryManagementClient(credentials, subscription_id)

    rg_params = {'location':'westus'}
    df_params = {'location':'westus'}

    # create the resource group
    # comment out if the resource group already exits
    resource_client.resource_groups.create_or_update(rg_name, rg_params)

    # Create a data factory
    df_resource = Factory(location='westus')
    df = adf_client.factories.create_or_update(rg_name, df_name, df_resource)
    print_item(df)
    while df.provisioning_state != 'Succeeded':
        df = adf_client.factories.get(rg_name, df_name)
        time.sleep(1)

    # Create an Azure Storage linked service
    ls_name = 'storageLinkedService001'

    # IMPORTANT: specify the name and key of your Azure Storage account.
    storage_string = SecureString(value=os.getenv('STORAGE_STRING'))

    ls_azure_storage = LinkedServiceResource(properties=AzureStorageLinkedService(connection_string=storage_string)) 
    ls = adf_client.linked_services.create_or_update(rg_name, df_name, ls_name, ls_azure_storage)
    print_item(ls)

    # Create an Azure blob dataset (input)
    ds_name = 'ds_in'
    ds_ls = LinkedServiceReference(reference_name=ls_name)
    blob_path = 'input'
    blob_filename = 'input.txt'
    ds_azure_blob = DatasetResource(properties=AzureBlobDataset(
        linked_service_name=ds_ls, folder_path=blob_path, file_name=blob_filename))
    ds = adf_client.datasets.create_or_update(
        rg_name, df_name, ds_name, ds_azure_blob)
    print_item(ds)

    # Create an Azure blob dataset (output)
    dsout_name = 'ds_out'
    output_blobpath = 'output'
    dsout_azure_blob = DatasetResource(properties=AzureBlobDataset(linked_service_name=ds_ls, folder_path=output_blobpath))
    dsout = adf_client.datasets.create_or_update(
        rg_name, df_name, dsout_name, dsout_azure_blob)
    print_item(dsout)

    # Create a copy activity
    act_name = 'copyBlobtoBlob'
    blob_source = BlobSource()
    blob_sink = BlobSink()
    dsin_ref = DatasetReference(reference_name=ds_name)
    dsout_ref = DatasetReference(reference_name=dsout_name)
    copy_activity = CopyActivity(name=act_name, inputs=[dsin_ref], outputs=[
                                 dsout_ref], source=blob_source, sink=blob_sink)

    # Create a pipeline with the copy activity
    p_name = 'copyPipeline'
    params_for_pipeline = {}
    p_obj = PipelineResource(
        activities=[copy_activity], parameters=params_for_pipeline)
    p = adf_client.pipelines.create_or_update(rg_name, df_name, p_name, p_obj)
    print_item(p)

    # Create a pipeline run
    run_response = adf_client.pipelines.create_run(rg_name, df_name, p_name, parameters={})

    # Monitor the pipeline run
    time.sleep(30)
    pipeline_run = adf_client.pipeline_runs.get(
        rg_name, df_name, run_response.run_id)
    print(f"\n\tPipeline run status: {pipeline_run.status}")
    filter_params = RunFilterParameters(
        last_updated_after=datetime.now() - timedelta(1),
        last_updated_before=datetime.now() + timedelta(1)
    )
    query_response = adf_client.activity_runs.query_by_pipeline_run(
        rg_name, df_name, pipeline_run.run_id, filter_params)
    print_activity_run_details(query_response.value[0])


# loads .env file into application environment
load_dotenv()

# Data Factory deployment and execution
main()
