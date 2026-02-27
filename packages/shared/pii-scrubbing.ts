/**
 * PII Scrubbing Utilities
 *
 * These functions scrub Personally Identifiable Information (PII) before caching data.
 * ALL cached data from Workwize API must be scrubbed before storage.
 */

/**
 * Anonymize email address
 * Example: john.doe@company.com -> j***@company.com
 */
export function anonymizeEmail(email: string): string {
  if (!email) return '';

  const [localPart, domain] = email.split('@');
  if (!domain) return email;

  const anonymized = localPart.charAt(0) + '***';
  return `${anonymized}@${domain}`;
}

/**
 * Redact name to initial only
 * Example: John -> J***
 */
export function redactName(name: string): string {
  if (!name) return '';
  return name.charAt(0) + '***';
}

/**
 * Scrub address to only include city and region
 * Removes street addresses and detailed location info
 */
export function scrubAddress(address: {
  address_line_1?: string;
  address_line_2?: string;
  city?: string;
  region?: string;
  postal_code?: string;
  country?: string;
}): string {
  if (!address) return '';

  const parts = [];
  if (address.city) parts.push(address.city);
  if (address.region) parts.push(address.region);

  return parts.join(', ');
}

/**
 * Scrub text content for PII patterns
 * Redacts: emails, phone numbers, SSNs, credit cards
 */
export function scrubText(text: string): string {
  if (!text) return '';

  let scrubbed = text;

  // Email pattern
  scrubbed = scrubbed.replace(
    /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g,
    '[EMAIL_REDACTED]'
  );

  // Phone number patterns (various formats)
  scrubbed = scrubbed.replace(
    /(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}/g,
    '[PHONE_REDACTED]'
  );

  // SSN pattern (xxx-xx-xxxx)
  scrubbed = scrubbed.replace(/\b\d{3}-\d{2}-\d{4}\b/g, '[SSN_REDACTED]');

  // Credit card pattern (16 digits with optional separators)
  scrubbed = scrubbed.replace(/\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b/g, '[CARD_REDACTED]');

  return scrubbed;
}

/**
 * Scrub employee data for caching
 * Redacts: first name, last name, email
 * Keeps: department, role, status, job title
 */
export function scrubEmployeeForCache(employee: any): any {
  if (!employee) return null;

  return {
    id: employee.id,
    firstName: redactName(employee.firstName || employee.first_name || ''),
    lastName: redactName(employee.lastName || employee.last_name || ''),
    email: anonymizeEmail(employee.email || ''),
    department: employee.department,
    role: employee.role,
    status: employee.status,
    jobTitle: employee.jobTitle || employee.job_title,
    managerId: employee.managerId || employee.manager_id,
    officeId: employee.officeId || employee.office_id,
    startDate: employee.startDate || employee.start_date,
    endDate: employee.endDate || employee.end_date,
  };
}

/**
 * Scrub asset data for caching
 * - Only stores employee ID (not name) for assignedTo
 * - Scrubs location to city/state only
 * - Scrubs notes for PII patterns
 */
export function scrubAssetForCache(asset: any): any {
  if (!asset) return null;

  return {
    id: asset.id,
    assetTag: asset.assetTag || asset.asset_tag,
    name: asset.name,
    category: asset.category,
    status: asset.status,
    serialNumber: asset.serialNumber || asset.serial_number,
    productId: asset.productId || asset.product_id,
    assignedToId: asset.assignedToId || asset.assigned_to_id || asset.assignedTo?.id,
    location: asset.location
      ? scrubAddress({ city: asset.location.city, region: asset.location.region })
      : null,
    purchaseDate: asset.purchaseDate || asset.purchase_date,
    purchasePrice: asset.purchasePrice || asset.purchase_price,
    currency: asset.currency,
    warrantyExpires: asset.warrantyExpires || asset.warranty_expires,
    notes: asset.notes ? scrubText(asset.notes) : null,
    officeId: asset.officeId || asset.office_id,
    warehouseId: asset.warehouseId || asset.warehouse_id,
  };
}

/**
 * Scrub order data for caching
 */
export function scrubOrderForCache(order: any): any {
  if (!order) return null;

  return {
    id: order.id,
    orderNumber: order.orderNumber || order.order_number,
    status: order.status,
    orderDate: order.orderDate || order.order_date,
    deliveryDate: order.deliveryDate || order.delivery_date,
    totalAmount: order.totalAmount || order.total_amount,
    currency: order.currency,
    customerId: order.customerId || order.customer_id,
    employeeId: order.employeeId || order.employee_id,
    warehouseId: order.warehouseId || order.warehouse_id,
    notes: order.notes ? scrubText(order.notes) : null,
  };
}

/**
 * Scrub address data for caching
 * Only keeps city, region, country - no street addresses
 */
export function scrubAddressForCache(address: any): any {
  if (!address) return null;

  return {
    id: address.id,
    city: address.city,
    region: address.region || address.state,
    country: address.country,
    postalCode: null, // Scrubbed for privacy
    latitude: address.latitude,
    longitude: address.longitude,
  };
}

/**
 * Validate that data has been properly scrubbed
 * Returns false if potential PII detected
 */
export function validateScrubbed(data: any): boolean {
  if (!data) return true;

  const jsonString = JSON.stringify(data);

  // Check for email patterns (should be anonymized or redacted)
  const emailPattern = /\b[A-Za-z0-9._%+-]{2,}@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/;
  if (emailPattern.test(jsonString) && !jsonString.includes('***@')) {
    return false;
  }

  // Check for phone number patterns
  const phonePattern = /(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}/;
  if (phonePattern.test(jsonString)) {
    return false;
  }

  // Check for SSN pattern
  const ssnPattern = /\b\d{3}-\d{2}-\d{4}\b/;
  if (ssnPattern.test(jsonString)) {
    return false;
  }

  // Check for credit card pattern
  const cardPattern = /\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b/;
  if (cardPattern.test(jsonString)) {
    return false;
  }

  return true;
}
