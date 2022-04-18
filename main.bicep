@description('The resource location is taken from the Resource Group.')
param location string = resourceGroup().location

@secure()
param storageConnectionString string

resource df 'Microsoft.DataFactory/factories@2018-06-01' = {
  name: 'a9odevopsadf01'
  location: location
}

resource ls_azure_storage 'Microsoft.DataFactory/factories/linkedservices@2018-06-01' = {
  name: 'storageLinkedService001'
  parent: df
  properties: {
    type: 'AzureStorage'
    typeProperties: {
      connectionString: storageConnectionString
    }
  }
}

resource ds_azure_blob 'Microsoft.DataFactory/factories/datasets@2018-06-01' = {
  name: 'ds_in'
  parent: df
  properties: {
    linkedServiceName: {
      parameters: {}
      referenceName: ls_azure_storage.name
      type: 'LinkedServiceReference'
    }
    type: 'AzureBlob'
    typeProperties: {
      folderPath: 'input'
      fileName: 'input.txt'
    }
  }
}

resource dsout_azure_blob 'Microsoft.DataFactory/factories/datasets@2018-06-01' = {
  name: 'ds_out'
  parent: df
  properties: {
    linkedServiceName: {
      parameters: {}
      referenceName: ls_azure_storage.name
      type: 'LinkedServiceReference'
    }
    type: 'AzureBlob'
    typeProperties: {
      folderPath: 'output'
    }
  }
}

resource p 'Microsoft.DataFactory/factories/pipelines@2018-06-01' = {
  name: 'copyPipeline'
  parent: df
  properties: {
    activities: [
      {
        name: 'copyBlobtoBlob'
        type: 'Copy'
        inputs: [
          {
            referenceName: ds_azure_blob.name
            type: 'DatasetReference'
          }
        ]
        outputs: [
          {
            referenceName: dsout_azure_blob.name
            type: 'DatasetReference'
          }
        ]
        typeProperties: {
          source: {
            type: 'BlobSource'
          }
          sink: {
            type: 'BlobSink'
          }
        }
      }
    ]
  }
}
