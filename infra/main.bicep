// Main Bicep template for Azure infrastructure
targetScope = 'subscription'

@description('The Azure region for resources')
param location string = 'eastus'

@description('The environment name (dev, staging, prod)')
@allowed([
  'dev'
  'staging'
  'prod'
])
param environment string = 'dev'

@description('The application name')
param appName string = 'ham-agent'

// Resource group
resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: '${appName}-${environment}-rg'
  location: location
  tags: {
    environment: environment
    application: appName
  }
}

// PostgreSQL Database
module database './modules/postgres.bicep' = {
  scope: rg
  name: 'postgresql-deployment'
  params: {
    location: location
    environment: environment
    appName: appName
  }
}

// Redis Cache
module redis './modules/redis.bicep' = {
  scope: rg
  name: 'redis-deployment'
  params: {
    location: location
    environment: environment
    appName: appName
  }
}

// Key Vault
module keyVault './modules/keyvault.bicep' = {
  scope: rg
  name: 'keyvault-deployment'
  params: {
    location: location
    environment: environment
    appName: appName
  }
}

// Container Apps Environment
module containerAppsEnv './modules/container-apps-env.bicep' = {
  scope: rg
  name: 'container-apps-env-deployment'
  params: {
    location: location
    environment: environment
    appName: appName
  }
}

// Backend Container App
module backendApp './modules/container-app.bicep' = {
  scope: rg
  name: 'backend-app-deployment'
  params: {
    location: location
    environment: environment
    appName: '${appName}-backend'
    containerAppsEnvironmentId: containerAppsEnv.outputs.environmentId
    containerImage: 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'
    targetPort: 3001
    environmentVariables: [
      {
        name: 'DATABASE_URL'
        secretRef: 'database-url'
      }
      {
        name: 'NODE_ENV'
        value: environment == 'prod' ? 'production' : 'development'
      }
    ]
  }
}

// Frontend Container App
module frontendApp './modules/container-app.bicep' = {
  scope: rg
  name: 'frontend-app-deployment'
  params: {
    location: location
    environment: environment
    appName: '${appName}-frontend'
    containerAppsEnvironmentId: containerAppsEnv.outputs.environmentId
    containerImage: 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'
    targetPort: 3000
    environmentVariables: [
      {
        name: 'NEXT_PUBLIC_API_URL'
        value: backendApp.outputs.fqdn
      }
      {
        name: 'NODE_ENV'
        value: environment == 'prod' ? 'production' : 'development'
      }
    ]
  }
}

output resourceGroupName string = rg.name
output backendUrl string = backendApp.outputs.fqdn
output frontendUrl string = frontendApp.outputs.fqdn
