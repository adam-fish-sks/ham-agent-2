// Azure Key Vault module
param location string
param environment string
param appName string

var keyVaultName = '${appName}-${environment}-kv'

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
    enablePurgeProtection: true
  }
}

output name string = keyVault.name
output uri string = keyVault.properties.vaultUri
