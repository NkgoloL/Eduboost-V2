// EduBoost V2 — Azure Container Apps production deployment
// Production deployment target: Azure Container Apps (ACA)
//
// Deploy with:
//   az deployment group create \
//     --resource-group <RG_NAME> \
//     --template-file bicep/container_apps.bicep \
//     --parameters @bicep/container_apps.parameters.json

@description('Azure region for all resources')
param location string = resourceGroup().location

@description('Environment name suffix (e.g. prod, staging)')
param environmentName string = 'prod'

@description('Container image tag to deploy')
param imageTag string = 'latest'

@description('Azure Container Registry login server')
param acrLoginServer string

@description('ACR admin username (from ACR access keys)')
@secure()
param acrUsername string

@description('ACR admin password (from ACR access keys)')
@secure()
param acrPassword string

@description('PostgreSQL connection string (Azure Database for PostgreSQL - Flexible Server)')
@secure()
param databaseUrl string

@description('Azure Cache for Redis connection string')
@secure()
param redisUrl string

@description('JWT signing secret (min 32 chars)')
@secure()
param jwtSecret string

@description('Groq API key for LLM inference')
@secure()
param groqApiKey string

@description('Anthropic API key for LLM fallback')
@secure()
param anthropicApiKey string

// ---------------------------------------------------------------------------
// Log Analytics Workspace (for ACA environment)
// ---------------------------------------------------------------------------

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: 'eduboost-v2-logs-${environmentName}'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// ---------------------------------------------------------------------------
// Container Apps Environment
// ---------------------------------------------------------------------------

resource acaEnvironment 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: 'eduboost-v2-env-${environmentName}'
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
  }
}

// ---------------------------------------------------------------------------
// EduBoost V2 API — Container App
// ---------------------------------------------------------------------------

resource eduboostApi 'Microsoft.App/containerApps@2023-05-01' = {
  name: 'eduboost-v2-api-${environmentName}'
  location: location
  properties: {
    managedEnvironmentId: acaEnvironment.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 8000
        transport: 'http'
        corsPolicy: {
          allowedOrigins: ['*']
          allowedMethods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
          allowedHeaders: ['*']
          allowCredentials: false
        }
      }
      registries: [
        {
          server: acrLoginServer
          username: acrUsername
          passwordSecretRef: 'acr-password'
        }
      ]
      secrets: [
        { name: 'acr-password', value: acrPassword }
        { name: 'database-url', value: databaseUrl }
        { name: 'redis-url', value: redisUrl }
        { name: 'jwt-secret', value: jwtSecret }
        { name: 'groq-api-key', value: groqApiKey }
        { name: 'anthropic-api-key', value: anthropicApiKey }
      ]
    }
    template: {
      containers: [
        {
          name: 'eduboost-v2-api'
          image: '${acrLoginServer}/eduboost-v2-api:${imageTag}'
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: [
            { name: 'APP_ENV', value: 'production' }
            { name: 'APP_NAME', value: 'EduBoost V2' }
            { name: 'LOG_LEVEL', value: 'INFO' }
            { name: 'JWT_ALGORITHM', value: 'HS256' }
            { name: 'CONSTITUTIONAL_AI_ENABLED', value: 'true' }
            { name: 'DATABASE_URL', secretRef: 'database-url' }
            { name: 'REDIS_URL', secretRef: 'redis-url' }
            { name: 'JWT_SECRET', secretRef: 'jwt-secret' }
            { name: 'GROQ_API_KEY', secretRef: 'groq-api-key' }
            { name: 'ANTHROPIC_API_KEY', secretRef: 'anthropic-api-key' }
          ]
          probes: [
            {
              type: 'Liveness'
              httpGet: {
                path: '/health'
                port: 8000
              }
              initialDelaySeconds: 15
              periodSeconds: 30
              failureThreshold: 3
            }
            {
              type: 'Readiness'
              httpGet: {
                path: '/ready'
                port: 8000
              }
              initialDelaySeconds: 10
              periodSeconds: 15
            }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 5
        rules: [
          {
            name: 'http-scaling'
            http: {
              metadata: {
                concurrentRequests: '20'
              }
            }
          }
        ]
      }
    }
  }
}

// ---------------------------------------------------------------------------
// Outputs
// ---------------------------------------------------------------------------

output apiUrl string = 'https://${eduboostApi.properties.configuration.ingress.fqdn}'
output environmentId string = acaEnvironment.id
