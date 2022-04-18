# Azure Data Factory DevOps with Python
DevOps practices deploying Azure Data Factory pipelines using Python.

This repository demonstrates two ways to deploy a Data Factory using Python client and Bicep.

## Python SDK
This approach uses Python to create the resources and run the Data Factory Pipeline.

1. First, you need to follow [this quickstart](https://docs.microsoft.com/en-us/azure/data-factory/quickstart-create-data-factory-python)
1. Create a `.env` file and fill these variables with your data:
   ```
   SUBSCRIPTION_ID=[YOUR SUBSCRIPTION]
   CLIENT_ID=[YOUR CLIENT ID]
   CLIENT_SECRET=[YOUR CLIENT SECRET]
   TENANT_ID=[YOUR TENENT ID]
   STORAGE_STRING=[YOUR STORAGE ACCOUNT CONNECTION STRING]
   ```
1. Run
   ```bash
   pip install -r requirements.txt
   python main.py
   ```

## IaC (Bicep) with Azure CLI
This scenario utilizes Bicep template to describe the resources (including the Data Factory Pipelines), than run the Pipeline using the Python client

1. Define environment variable
   ```bash
   AZ_RESOURCE_GROUP=temp_devopsdatafactory
   AZ_FACTORY_NAME=a9odevopsadf01
   ```
1. Deploy the bicep template. Provide the connection string when asked:
   ```bash
   az deployment group create --resource-group $AZ_RESOURCE_GROUP --template-file main.bicep
   ```
1. Run
   ```bash
   az datafactory pipeline create-run --resource-group $AZ_RESOURCE_GROUP --factory-name $AZ_FACTORY_NAME --name "copyPipeline"
   ```
