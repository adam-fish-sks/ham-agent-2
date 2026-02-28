/**
 * Device classification utilities
 * Classifies devices into Standard/Enhanced categories for Windows and Mac
 */

export type DeviceClass = 
  | 'Enhanced Windows'
  | 'Standard Windows'
  | 'Enhanced Mac'
  | 'Standard Mac'
  | 'Other';

export interface DeviceSpecs {
  manufacturer?: string;
  model?: string;
  ram?: string;
  ramGb?: number;
  cpu?: string;
  isHighEnd: boolean;
}

/**
 * Parse device specifications from asset name field
 * Example: "Dell, Precision 5690, Intel Core Ultra 9-185H, 2024, 16", 32GB RAM, 1TB SSD, QWERTY Us, Grey, Laptops"
 */
export function parseDeviceSpecs(assetName: string): DeviceSpecs {
  const manufacturer = assetName.match(/^(\w+),/)?.[1];
  const model = assetName.match(/,\s*([^,]+?),/)?.[1];
  const ram = assetName.match(/(\d+GB RAM)/)?.[1];
  const ramGb = ram ? parseInt(ram.match(/(\d+)/)?.[1] || '0') : undefined;
  const cpu = assetName.match(/(Intel Core [^,]+|Apple M\d+[^,]*|Ultra \d+[^,]*)/i)?.[1];
  
  // Check if device is high-end based on model, RAM, or CPU
  const isHighEnd = Boolean(
    assetName.match(/Xps|Precision|Pro Max|32GB|64GB|i9|Ultra 9|M[345]\s+(Pro|Max)/i)
  );

  return {
    manufacturer,
    model,
    ram,
    ramGb,
    cpu,
    isHighEnd,
  };
}

/**
 * Classify a device based on its name and specifications
 */
export function classifyDevice(assetName: string): DeviceClass {
  if (!assetName) return 'Other';

  const specs = parseDeviceSpecs(assetName);

  // Mac classification
  if (assetName.match(/MacBook|Mac|Apple/i)) {
    // Enhanced Mac: M3/M4/M5 Pro/Max with 32GB+
    if (assetName.match(/M[345]\s+(Pro|Max)/i) && specs.ramGb && specs.ramGb >= 32) {
      return 'Enhanced Mac';
    }
    return 'Standard Mac';
  }

  // Windows classification (Dell)
  if (assetName.match(/Dell/i)) {
    // Standard Windows: Explicitly identify standard business lines first
    if (assetName.match(/Latitude|Pro 14|Pro 16|Vostro|Inspiron/i)) {
      return 'Standard Windows';
    }

    // Enhanced Windows: Only high-end workstation/premium lines
    // Must be Xps, Precision, or Pro Max (not Pro 14/16)
    // AND have either 32GB+ RAM OR high-end CPU (i9, Ultra 9, HX-series)
    if (assetName.match(/\b(Xps|Precision|Pro Max)\b/i)) {
      if (
        (specs.ramGb && specs.ramGb > 16) || 
        assetName.match(/\b(i9|Ultra 9)\b|i7.*HX/i)
      ) {
        return 'Enhanced Windows';
      }
    }

    // Default other Dell devices to Standard Windows
    return 'Standard Windows';
  }

  return 'Other';
}

/**
 * Get device classification criteria as human-readable text
 */
export function getDeviceClassCriteria(deviceClass: DeviceClass): string {
  switch (deviceClass) {
    case 'Enhanced Windows':
      return 'High-performance Windows laptops (Dell Xps, Precision, Pro Max) with >16GB RAM or high-end CPU (i9, Ultra 9, HX)';
    case 'Standard Windows':
      return 'Standard Windows laptops (Dell Latitude) with ≤16GB RAM and standard CPUs (i5, i7)';
    case 'Enhanced Mac':
      return 'MacBook Pro (2021+) with Apple Silicon M3/M4/M5 Pro/Max and ≥32GB RAM';
    case 'Standard Mac':
      return 'MacBook Air or older MacBook Pro with Intel or base Apple Silicon (M1, M2, base M3/M4/M5) and ≤16GB RAM';
    default:
      return 'Other devices not classified as Windows or Mac laptops';
  }
}
