@description('Location for all resources')
param location string = resourceGroup().location

@description('App Service Plan name')
param appServicePlanName string = 'plan-ai-pm'

@description('Backend App Service name')
param backendAppName string = 'app-ai-pm-backend'

@description('Frontend Static Web App name')
param frontendAppName string = 'stapp-ai-pm-frontend'

resource appServicePlan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: appServicePlanName
  location: location
  sku: {
    name: 'B1'
    tier: 'Basic'
  }
  kind: 'linux'
  properties: {
    reserved: true
  }
}

resource backendApp 'Microsoft.Web/sites@2023-01-01' = {
  name: backendAppName
  location: location
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.12'
      appCommandLine: 'uvicorn app.main:app --host 0.0.0.0 --port 8000'
      appSettings: [
        { name: 'SCM_DO_BUILD_DURING_DEPLOYMENT', value: 'true' }
      ]
    }
    httpsOnly: true
  }
}

resource frontendStaticWebApp 'Microsoft.Web/staticSites@2023-01-01' = {
  name: frontendAppName
  location: location
  sku: {
    name: 'Free'
    tier: 'Free'
  }
  properties: {}
}

output backendUrl string = 'https://${backendApp.properties.defaultHostName}'
output frontendUrl string = 'https://${frontendStaticWebApp.properties.defaultHostname}'
