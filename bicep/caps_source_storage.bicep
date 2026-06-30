// EduBoost CAPS source document object storage.
// Deploy with:
//   az deployment group create \
//     --resource-group <RG_NAME> \
//     --template-file bicep/caps_source_storage.bicep \
//     --parameters storageAccountName=<globally_unique_name>

@description('Azure region for the source-document storage account.')
param location string = resourceGroup().location

@description('Globally unique storage account name, 3-24 lowercase letters/numbers.')
@minLength(3)
@maxLength(24)
param storageAccountName string

@description('Blob container used for official CAPS source PDFs.')
param containerName string = 'caps-sources'

@description('Storage redundancy SKU.')
@allowed([
  'Standard_LRS'
  'Standard_GRS'
  'Standard_ZRS'
])
param storageSku string = 'Standard_LRS'

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: storageSku
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    allowCrossTenantReplication: false
    defaultToOAuthAuthentication: true
    minimumTlsVersion: 'TLS1_2'
    publicNetworkAccess: 'Enabled'
    supportsHttpsTrafficOnly: true
  }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  parent: storageAccount
  name: 'default'
  properties: {
    deleteRetentionPolicy: {
      enabled: true
      days: 30
    }
    containerDeleteRetentionPolicy: {
      enabled: true
      days: 30
    }
  }
}

resource sourceContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blobService
  name: containerName
  properties: {
    publicAccess: 'None'
    metadata: {
      workload: 'eduboost-caps-source-documents'
      source: 'official-dbe-caps'
    }
  }
}

output storageAccountName string = storageAccount.name
output blobEndpoint string = storageAccount.properties.primaryEndpoints.blob
output containerName string = sourceContainer.name
output containerUri string = '${storageAccount.properties.primaryEndpoints.blob}${sourceContainer.name}'
