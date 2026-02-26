# Workwize Warehouse Physical Locations

This document maps warehouse codes to their **physical locations**. Note that warehouses may serve multiple countries beyond their physical location.

**Example**: VEW is physically located in the Netherlands but serves 33 European countries (see Workwize API for full service regions).

## Warehouse Directory

| ID | Code | Physical Location |
|----|------|------------------|
| 1  | LDW  | United Kingdom (GB) |
| 2  | ER3  | United States (US) |
| 4  | VEW  | Netherlands (NL) |
| 6  | LPB  | India (IN) |
| 7  | LBZ  | Brazil (BR) |
| 8  | YYZ  | Canada (CA) |
| 9  | SYD  | Australia (AU) |
| 10 | LPP  | Philippines (PH) |
| 11 | MXW  | Mexico (MX) |
| 12 | SIW  | Singapore (SG) |
| 13 | SOA  | South Africa (ZA) |
| 14 | CSW  | Costa Rica (CR) |
| 15 | TYO  | Japan (JP) |
| 16 | DXB  | United Arab Emirates (AE) |

## Regional Distribution

**Europe**: GB (LDW), NL (VEW)

**Americas**: US (ER3), CA (YYZ), MX (MXW), BR (LBZ), CR (CSW)

**Asia-Pacific**: AU (SYD), IN (LPB), PH (LPP), SG (SIW), JP (TYO)

**Middle East & Africa**: ZA (SOA), AE (DXB)

---

**Note**: The Workwize API `GET /warehouses?include=countries` returns service regions, not physical locations. For service coverage by warehouse, refer to the API response in `data-samples/warehouses_with_countries.json`.

**Last Updated**: February 26, 2026

