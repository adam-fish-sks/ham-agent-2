// Azure Cache for Redis module
param location string
param environment string
param appName string

var cacheName = '${appName}-${environment}-redis'

resource redisCache 'Microsoft.Cache/redis@2023-08-01' = {
  name: cacheName
  location: location
  properties: {
    sku: {
      name: environment == 'prod' ? 'Standard' : 'Basic'
      family: 'C'
      capacity: environment == 'prod' ? 1 : 0
    }
    enableNonSslPort: false
    minimumTlsVersion: '1.2'
    publicNetworkAccess: 'Enabled'
    redisConfiguration: {
      'maxmemory-policy': 'allkeys-lru'
    }
  }
}

output name string = redisCache.name
output hostName string = redisCache.properties.hostName
output sslPort int = redisCache.properties.sslPort
output primaryKey string = redisCache.listKeys().primaryKey
