# AI Agent Query Guide

⚠️ **DEPRECATED**: This guide is outdated. The AI Assistant now automatically executes queries without requiring manual scripts.

## Current Implementation

The AI Assistant uses:
- **Automatic Query Execution**: Queries database directly, no code snippets needed
- **Device Classification**: Built-in logic in `packages/shared/device-classification.ts`
- **Natural Language Processing**: Detects countries, device classes, status keywords automatically
- **Single System Prompt**: Configured in Settings page, includes all classification rules

For AI configuration, see [AI_ASSISTANT_FEATURES.md](AI_ASSISTANT_FEATURES.md).

---

## Legacy Information (For Reference Only)

This guide previously enabled AI agents to query the HAM Agent database through manual scripts.

## Base URL

```
http://localhost:3001
```

## Available Endpoints

### 1. Warehouses

#### GET /warehouses
Returns all warehouses with address information.

**Example:**
```bash
curl http://localhost:3001/warehouses
```

**Response:**
```json
[
  {
    "id": "8",
    "name": "Canada Warehouse",
    "code": "YYZ",
    "addressId": "addr_123",
    "capacity": 5000,
    "status": "active",
    "type": "distribution",
    "address": { ... }
  }
]
```

**To filter by code:** Parse response and filter where `code === "YYZ"`

### 2. Assets

#### GET /assets
Returns all assets with product, employee, office, and warehouse details.

**Example:**
```bash
curl http://localhost:3001/assets
```

**Response:**
```json
[
  {
    "id": "asset_123",
    "serialNumber": "ABC123XYZ",
    "status": "available",
    "productId": "prod_456",
    "warehouseId": "8",
    "assignedToId": null,
    "officeId": null,
    "product": {
      "id": "prod_456",
      "name": "Dell Precision 7680",
      "manufacturer": "Dell",
      "model": "Precision 7680",
      "category": "Laptop",
      "os": "Windows",
      "cpu": "Intel Core i9-13950HX",
      "ramGb": 32,
      "storageGb": 1024,
      "gpuType": "NVIDIA RTX 4000 Ada",
      "discreteGpu": true
    },
    "warehouse": {
      "id": "8",
      "code": "YYZ",
      "name": "Canada Warehouse"
    }
  }
]
```

**Query Parameters:** None (filter in code after fetching)

### 3. Products

#### GET /products
Returns all products with specifications.

**Example:**
```bash
curl http://localhost:3001/products
```

## Query Workflow Examples

### Example 1: Find Enhanced Windows Devices in Canada (WORKING VERSION)

**PowerShell (Recommended):**
```powershell
$assets = Invoke-RestMethod -Uri http://localhost:3001/api/assets

# Filter for Canada (by assignedTo address OR warehouseId 8 = YYZ)
$canadaAssets = $assets | Where-Object { 
  $_.assignedTo.address.country -eq 'Canada' -or $_.warehouseId -eq '8'
}

# Filter for Enhanced Windows (Dell Xps/Precision/Pro Max with 32GB+ RAM or high-end CPU)
$enhanced = $canadaAssets | Where-Object { 
  $_.name -match 'Dell.*(Xps|Precision|Pro Max)' -and 
  ($_.name -match '32GB|64GB|i9|Ultra 9')
}

# Display results
$enhanced | Select-Object serialCode, 
  @{N='Device';E={($_.name -split ',')[0..3] -join ', '}}, 
  @{N='RAM';E={if($_.name -match '(\d+GB RAM)'){$matches[1]}}}, 
  status | Format-Table -Wrap
```

**JavaScript:**
```javascript
const response = await fetch('http://localhost:3001/api/assets');
const assets = await response.json();

// Filter for Canada assets
const canadaAssets = assets.filter(asset => 
  asset.assignedTo?.address?.country === 'Canada' || 
  asset.warehouseId === '8'  // YYZ warehouse
);

// Filter for Enhanced Windows
const enhanced = canadaAssets.filter(asset => {
  const name = asset.name || '';
  const isDell = name.match(/Dell/i);
  const isHighEndModel = name.match(/Xps|Precision|Pro Max/i);
  const hasHighSpecs = name.match(/32GB|64GB|i9|Ultra 9/i);
  
  return isDell && isHighEndModel && hasHighSpecs;
});

// Format results
const results = enhanced.map(asset => ({
  serial: asset.serialCode,
  device: asset.name.split(',').slice(0, 4).join(', '),
  ram: asset.name.match(/(\d+GB RAM)/)?.[1] || 'N/A',
  status: asset.status
}));

console.table(results);
```

### Example 2: Count Assets by Device Class (WORKING VERSION)

```powershell
$assets = Invoke-RestMethod -Uri http://localhost:3001/api/assets

function Get-DeviceClass($asset) {
  $name = $asset.name
  
  # Mac classification
  if ($name -match 'MacBook|Mac|Apple') {
    if ($name -match '(M[345]\s+(Pro|Max))' -and $name -match '(32|64)GB') {
      return 'Enhanced Mac'
    }
    return 'Standard Mac'
  }
  
  # Windows classification (Dell)
  if ($name -match 'Dell') {
    # Enhanced: Xps, Precision, Pro Max with 32GB+ or high-end CPU
    if (($name -match 'Xps|Precision|Pro Max') -and 
        ($name -match '32GB|64GB|i9|Ultra 9')) {
      return 'Enhanced Windows'
    }
    # Standard: Latitude with 16GB or less
    if ($name -match 'Latitude' -and $name -match '16GB') {
      return 'Standard Windows'
    }
    return 'Standard Windows'
  }
  
  return 'Other'
}

# Count by class
$counts = @{}
foreach ($asset in $assets) {
  $class = Get-DeviceClass $asset
  $counts[$class] = ($counts[$class] ?? 0) + 1
}

Write-Host "`nDevice Counts by Class:"
$counts.GetEnumerator() | Sort-Object Name | Format-Table -AutoSize
```

## Device Classification Rules

### Enhanced Windows
- **RAM**: > 16GB, OR
- **GPU**: Discrete graphics (NVIDIA, AMD), OR
- **CPU**: Contains "i9", "HX", or H-series i7 (e.g., "i7-12700H")
- **Examples**: Dell Precision, Dell XPS, Dell Pro Max

### Standard Windows
- **RAM**: ≤ 16GB
- **GPU**: Integrated only
- **CPU**: i5, i7, Ultra 7 (without high-performance suffix)
- **Examples**: Dell Latitude 5520, 5530

### Enhanced Mac
- **CPU**: M3 Pro/Max, M4 Pro/Max, M5 Pro/Max
- **RAM**: ≥ 32GB
- **Model**: MacBook Pro (2021+)

### Standard Mac
- **Models**: MacBook Air (all), MacBook Pro pre-2021
- **CPU**: Intel-based, M1, M2, base M3/M4/M5
- **RAM**: ≤ 16GB

## ACTUAL Data Schema (CRITICAL)

**IMPORTANT**: Product specs are NOT in separate fields. They're ALL in the `name` field as a comma-separated string!

```typescript
interface Asset {
  id: string;
  serialCode: string;
  name: string;  // ⚠️ THIS CONTAINS ALL SPECS: "Dell, Xps 16 9640, U9, 2024, 16\", 32GB RAM, 1TB SSD, QWERTY Us, Plat, Laptops"
  category: string;
  status: string;  // "available", "deployed", "in_transit", etc.
  productId: string | null;  // Usually null
  assignedToId: string | null;
  warehouseId: string | null;
  product: null;  // ⚠️ This is NULL - specs are in the name field!
  assignedTo: {
    id: string;
    firstName: string;  // PII scrubbed: "A***"
    lastName: string;   // PII scrubbed: "M***"
    email: string;      // PII scrubbed: "a***@gmail.com"
    address: {
      country: string;  // ⚠️ USE THIS for country filtering: "Canada", "United States", etc.
      city: string;
      region: string;
    } | null;
  } | null;
  warehouse: null;  // ⚠️ This is NULL - use warehouseId instead
}
```

### How to Parse Product Specs from name field:

```javascript
// Example name: "Dell, Precision 5690, Intel Core Ultra 9-185H, 2024, 16\", 32GB RAM, 1TB SSD, QWERTY Us, Grey, Laptops"

function parseSpecs(assetName) {
  return {
    manufacturer: assetName.match(/^(\w+),/)?.[1],  // "Dell"
    model: assetName.match(/,\s*([^,]+),/)?.[1],    // "Precision 5690"
    ram: assetName.match(/(\d+GB RAM)/)?.[1],        // "32GB RAM"
    cpu: assetName.match(/(Intel Core [^,]+|Apple M\d+ [^,]+)/)?.[1],
    isHighEnd: assetName.match(/Xps|Precision|Pro Max|32GB|64GB|i9|Ultra 9/i) !== null
  };
}
```

## Asset Status Values

- `available` - Ready for assignment
- `assigned` - Assigned to an employee
- `in_transit` - Being shipped
- `maintenance` - Under repair
- `retired` - End of life

## Warehouse Codes

| Code | Location            |
|------|---------------------|
| YYZ  | Canada              |
| ER3  | United States       |
| LDW  | United Kingdom      |
| VEW  | Netherlands         |
| SYD  | Australia           |
| SIW  | Singapore           |
| TYO  | Japan               |
| DXB  | United Arab Emirates|
| SOA  | South Africa        |
| LPB  | India               |
| LBZ  | Brazil              |
| MXW  | Mexico              |
| LPP  | Philippines         |
| CSW  | Costa Rica          |

## Complete Query Script Template (WORKING VERSION)

```powershell
# PowerShell function to query and classify devices
function Get-DevicesByLocation {
  param(
    [string]$Country,
    [string]$DeviceClass
  )
  
  # Fetch all assets
  $assets = Invoke-RestMethod -Uri http://localhost:3001/api/assets
  
  # Filter by country
  $filtered = $assets | Where-Object {
    $_.assignedTo.address.country -eq $Country
  }
  
  # Classify and filter by device class if specified
  $results = $filtered | ForEach-Object {
    $asset = $_
    $class = Get-DeviceClass $asset
    
    if (-not $DeviceClass -or $class -eq $DeviceClass) {
      [PSCustomObject]@{
        Serial = $asset.serialCode
        Device = ($asset.name -split ',')[0..2] -join ', '
        RAM = if($asset.name -match '(\d+GB RAM)'){$matches[1]}
        Status = $asset.status
        Class = $class
        Country = $asset.assignedTo.address.country
      }
    }
  }
  
  return $results
}

# Usage examples:
# All Enhanced Windows in Canada
Get-DevicesByLocation -Country 'Canada' -DeviceClass 'Enhanced Windows' | Format-Table

# All devices in United States
Get-DevicesByLocation -Country 'United States' | Format-Table
```

```javascript
// JavaScript version
async function queryDevicesByLocation(country, deviceClass) {
  // Fetch all assets
  const response = await fetch('http://localhost:3001/api/assets');
  const assets = await response.json();
  
  // Filter by country
  const filtered = assets.filter(asset => 
    asset.assignedTo?.address?.country === country
  );
  
  // Classify and filter
  const results = filtered
    .map(asset => ({
      serial: asset.serialCode,
      device: asset.name?.split(',').slice(0, 3).join(', '),
      ram: asset.name?.match(/(\d+GB RAM)/)?.[1],
      status: asset.status,
      class: classifyDevice(asset),
      country: asset.assignedTo?.address?.country
    }))
    .filter(item => !deviceClass || item.class === deviceClass);
  
  return results;
}

function classifyDevice(asset) {
  const name = asset.name || '';
  
  // Mac
  if (name.match(/MacBook|Mac|Apple/i)) {
    return name.match(/(M[345]\s+(Pro|Max))/i) && name.match(/32GB|64GB/i)
      ? 'Enhanced Mac' : 'Standard Mac';
  }
  
  // Windows
  if (name.match(/Dell/i)) {
    return name.match(/Xps|Precision|Pro Max/i) && name.match(/32GB|64GB|i9|Ultra 9/i)
      ? 'Enhanced Windows' : 'Standard Windows';
  }
  
  return 'Other';
}

// Usage:
const enhancedInCanada = await queryDevicesByLocation('Canada', 'Enhanced Windows');
console.table(enhancedInCanada);
```

---

**Last Updated**: February 27, 2026
