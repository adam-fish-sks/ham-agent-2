# Workwize Public API Documentation

## Base URL
```
https://prod-back.goworkwize.com/api/public
```

## Authentication
All API requests must be authenticated using a Bearer token in the Authorization header:
```
Authorization: Bearer {your_token}
```

## GET Endpoints

### Employees

#### Get All Employees
```
GET /employees
```
Returns an array of all employees with their details including department, registration status, and asset information.

**Query Parameters:**
- None required (no pagination on this endpoint)

**Example Request:**
```bash
curl --location '/employees' \
  --header 'Authorization: Bearer {token}'
```

**Response:**
```json
[
  {
    "id": 137077,
    "name": "John Doe",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@goworkwize.com",
    "ordersCount": null,
    "assetsCount": null,
    "team": "IT",
    "foreign_id": null,
    "registrationStatus": "Accepted",
    "isDeactivated": false,
    "total_price": 1,
    "total_price_formatted": "€ 1,00",
    "total_current_value": 0.75,
    "total_current_value_formatted": "-",
    "total_original_asset_value_formatted": "€ 1,00",
    "total_current_asset_value_formatted": "-",
    "user_id": 139558,
    "original_role": {
      "id": 4,
      "display_name": "Employer Admin",
      "name": "employer-admin"
    },
    "department": {
      "id": 19448,
      "employer_id": 490,
      "name": "IT",
      "rent_budget": 10000,
      "purchase_budget": 10000,
      "employees_count": 3,
      "created_at": "2025-02-06T10:36:45.000000Z",
      "updated_at": "2025-02-06T10:36:45.000000Z"
    }
  }
]
```

#### Get Single Employee
```
GET /employees/{id}
```
Returns details for a specific employee by ID.

**Path Parameters:**
- `id` (required) - Employee ID

**Response:** Returns direct object (not wrapped) - same structure as individual employee object from Get All Employees

#### Get Employee Addresses
```
GET /employees/{id}/addresses
```
Returns address information for a specific employee.

**Path Parameters:**
- `id` (required) - Employee ID

**Example Request:**
```bash
curl --location '/employees/137077/addresses' \
  --header 'Authorization: Bearer {token}'
```

**Response:**
```json
{
  "code": 200,
  "success": true,
  "status": true,
  "message": null,
  "data": {
    "id": 136657,
    "city": "Vonfurt",
    "country": {
      "id": 32,
      "name": "Netherlands",
      "code": "NL",
      "requires_tin": false
    },
    "company_name": null,
    "country_id": 32,
    "address_line_1": "Schuster Drive",
    "address_line_2": "977",
    "region": "South Carolina",
    "postcode": "39356",
    "postal_code": "39356",
    "additional_address_line": "Route",
    "name": "Brown",
    "first_name": "Brown",
    "last_name": "Schroeder",
    "email": "brown.schroeder@omartest.com",
    "phone_number": "+1-445-976-9749"
  },
  "links": {},
  "meta": {},
  "errors": [],
  "redirect": ""
}
```

**Notes:**
- Response is wrapped in `{code, success, status, message, data, links, meta, errors, redirect}` format (unlike GET /employees/{id} which returns direct object)
- Returns 404 if employee has no address
- Both `postcode` and `postal_code` fields are present with same value
- Address includes full country information with country code

### Assets

#### Get All Assets
```
GET /assets
```
Returns a paginated list of all assets with full location details including employee, warehouse, or office information.

**Query Parameters:**
- `page` (integer, optional) - Page number for pagination (default: 1)
- `per_page` (integer, optional) - Number of items per page (default: 200)

**Example Request:**
```bash
curl --location '/assets' \
  --header 'Authorization: Bearer {token}'
```

**Response:**
```json
{
  "data": [
    {
      "id": 66507888,
      "name": "Apple, MacBook Air, M3, 2024, 13\", 16GB RAM, 512GB SSD, AZERTY French, Silver, Laptops",
      "category": null,
      "location": {
        "location_id": 137077,
        "location_type": "employee",
        "location_detail": {
          "first_name": "John",
          "last_name": "Doe",
          "address": {
            "address_line_1": null,
            "address_line_2": null,
            "postal_code": null,
            "additional_address_line": null,
            "city": null,
            "region": null,
            "email": null,
            "phone_number": null
          },
          "team": "IT"
        }
      },
      "note": null,
      "serial_code": "2IMICKT3GG",
      "invoice_price": 1,
      "invoice_currency": null,
      "external_reference": null,
      "warehouse_status": "available",
      "condition": "new"
    },
    {
      "id": 66507890,
      "name": "Dell, P2423DE, 24\", QHD, IPS, Monitors",
      "category": {
        "id": 99,
        "name": "Monitors",
        "created_at": "2021-05-28T12:57:49.000000Z",
        "updated_at": "2021-05-28T12:57:49.000000Z"
      },
      "location": {
        "location_id": 1,
        "location_type": "warehouse",
        "location_detail": {
          "name": "Logistics Plus"
        }
      },
      "note": null,
      "serial_code": "L5I2N4ECLI",
      "invoice_price": 1,
      "invoice_currency": null,
      "external_reference": null,
      "warehouse_status": "available",
      "condition": "new"
    },
    {
      "id": 66507894,
      "name": "Apple, MacBook Air, M3, 2024, 13.6\", 16GB RAM, 512GB SSD, French AZERTY, Space Grey, Laptops",
      "category": {
        "id": 86,
        "name": "Laptops",
        "created_at": "2021-05-05T15:28:06.000000Z",
        "updated_at": "2021-05-05T15:28:06.000000Z"
      },
      "location": {
        "location_id": 27643,
        "location_type": "office",
        "location_detail": {
          "name": "Amsterdam Office",
          "address": {
            "address_line_1": "Damstraat 1",
            "address_line_2": "",
            "postal_code": "1012JS",
            "additional_address_line": "",
            "city": "Amsterdam",
            "region": "Noord-Holland",
            "email": "jan.devries@example.nl",
            "phone_number": "+31 20-1234567"
          }
        }
      },
      "note": null,
      "serial_code": "ADG8CST7E0",
      "invoice_price": 1,
      "invoice_currency": null,
      "external_reference": null,
      "warehouse_status": "available",
      "condition": "new"
    }
  ],
  "links": {
    "first": "http://127.0.0.1:8000/api/public/assets?page=1",
    "last": "http://127.0.0.1:8000/api/public/assets?page=1",
    "prev": null,
    "next": null
  },
  "meta": {
    "current_page": 1,
    "from": 1,
    "last_page": 1,
    "per_page": 200,
    "to": 31,
    "total": 31
  }
}
```

**Location Types:**
- `employee` - Asset assigned to an employee (includes employee name, address, team)
- `warehouse` - Asset located in a warehouse (includes warehouse name)
- `office` - Asset located in an office (includes office name and address)

#### Get Single Asset
```
GET /assets/{id}
```
Returns details for a specific asset including location information.

**Path Parameters:**
- `id` (required) - Asset ID

**Response:** Same structure as individual asset object from Get All Assets

### Products

#### Get All Products
```
GET /products
```
Returns a paginated list of all products with full details including availability by country and department.

**Query Parameters:**
- `page` (integer, optional) - Page number for pagination (default: 1)
- `include` (string, optional) - Comma-separated relationships to include (e.g., `countries,departments`)
- `filter[country_availability]` (string, optional) - Comma-separated country codes to filter by availability (e.g., `US,NL`)

**Example Request:**
```bash
curl --location -g '/products?include=countries%2Cdepartments&filter[country_availability]=US%2CNL' \
  --header 'Authorization: Bearer {token}'
```

**Response:**
```json
{
  "data": [
    {
      "id": 84148,
      "name": "Apple, MacBook Air, M3, 2024, 13\", 16GB RAM, 512GB SSD, QWERTY - US, Midnight, Laptops",
      "images": [
        "https://workwize-bucket.s3.eu-west-3.amazonaws.com/products/1712291304-k3vkC0VrBDEjRC2CsMkVimage_1-sq.jpg"
      ],
      "type": "Buy",
      "price": {
        "amount": "1",
        "currency": "XCR"
      },
      "short_description": "Apple, Laptops, 13.6\", 16GB RAM, 512GB SSD, Available in: EU",
      "description": "<p><strong>General Information</strong></p><ul><li>Brand: Apple</li><li>Model: Apple MacBook Air 2024...</li></ul>",
      "second_hand": false,
      "article_code": "MXCV3N/A-CTO",
      "category": "Laptops",
      "supplier": null,
      "created_at": "2025-01-28T14:19:39.000000Z",
      "updated_at": "2025-01-28T14:40:52.000000Z",
      "attribute": null,
      "variants": [],
      "ean": "0195949637117",
      "product_images": [],
      "countries": [
        {
          "id": 3,
          "name": "Austria",
          "code": "AT"
        },
        {
          "id": 32,
          "name": "Netherlands",
          "code": "NL"
        }
      ],
      "department_ids": [
        19448,
        19449,
        19450
      ]
    }
  ],
  "links": {
    "first": "http://127.0.0.1:8000/api/public/products?page=1",
    "last": "http://127.0.0.1:8000/api/public/products?page=3",
    "prev": null,
    "next": "http://127.0.0.1:8000/api/public/products?page=2"
  },
  "meta": {
    "current_page": 1,
    "from": 1,
    "last_page": 3,
    "per_page": 15,
    "to": 15,
    "total": 34
  }
}
```

### Orders

#### Get All Orders
```
GET /orders
```
Returns a paginated list of all orders with full details including products, shipments, and tracking information.

**Query Parameters:**
- `page` (integer, optional) - Page number for pagination (default: 1)
- `filter[employee_foreign_id]` (string, optional) - Filter orders by employee foreign ID

**Example Request:**
```bash
curl --location -g '/orders?filter[employee_foreign_id]=5678-EFGH' \
  --header 'Authorization: Bearer {token}'
```

**Response:**
```json
{
  "data": [
    {
      "id": 106288,
      "number": "AOCHWLGJY2",
      "total_products": 3,
      "currency": {
        "id": 2,
        "icon": "€",
        "name": "EUR",
        "created_at": "2020-12-25T13:32:23.000000Z",
        "updated_at": "2020-12-25T13:32:23.000000Z"
      },
      "actor": null,
      "receiver": "Wayne Witting",
      "express_delivery": null,
      "shipping_info": {
        "id": 136632,
        "city": "Thaddeusland",
        "country": {
          "id": 32,
          "name": "Netherlands",
          "code": "NL",
          "requires_tin": false
        },
        "company_name": null,
        "country_id": 32,
        "address_line_1": "Jacobson Drive",
        "address_line_2": "142",
        "region": "South Carolina",
        "postcode": "70342",
        "postal_code": "70342",
        "additional_address_line": "Drives",
        "name": "Wayne",
        "first_name": "Wayne",
        "last_name": "Witting",
        "email": "wayne.witting@workwizedemocsm.com",
        "phone_number": "1-941-312-1031"
      },
      "status": "Delivered",
      "products": [
        {
          "id": 295706,
          "order_id": 106288,
          "name": "Dell, P2724DEB, 27\", 2560 x 1440, LED monitor - QHD, Monitors",
          "type": "Buy",
          "short_description": "Dell, Monitors, 27\", Available in: ZA",
          "article_code": "P2724DEB",
          "product_quantity": 1,
          "price": true,
          "invoice_price": 576.62,
          "invoice_currency": "EUR",
          "status": "order_placed"
        }
      ],
      "buy_subtotal": 0.03,
      "rent_subtotal": 0,
      "shipments": [
        {
          "id": 220928,
          "order_number": "AOCHWLGJY2",
          "tracking_number": "81995541",
          "track_and_trace_url": "https://ferry.com/",
          "status": "In Transit",
          "destination_address": {
            "id": 136632,
            "city": "Thaddeusland",
            "country": {
              "id": 32,
              "name": "Netherlands",
              "code": "NL"
            },
            "address_line_1": "Jacobson Drive",
            "address_line_2": "142",
            "postal_code": "70342"
          },
          "products": [
            {
              "name": "Dell, P2724DEB, 27\", 2560 x 1440, LED monitor - QHD, Monitors",
              "quantity": 1
            }
          ],
          "deliveryDate": "Feb 01, 2025"
        }
      ],
      "created_at": "2024-09-06T08:17:56.000000Z",
      "updated_at": "2025-02-03T08:17:56.000000Z"
    }
  ],
  "links": {
    "first": "https://prod-back.goworkwize.com/api/public/orders?page=1",
    "last": "https://prod-back.goworkwize.com/api/public/orders?page=1",
    "prev": null,
    "next": null
  },
  "meta": {
    "current_page": 1,
    "from": 1,
    "last_page": 1,
    "per_page": 15,
    "to": 1,
    "total": 1
  }
}
```

#### Get Order Products
```
GET /orders/{order_number}/products
```
Returns detailed product information for a specific order.

**Path Parameters:**
- `order_number` (required) - Order number (e.g., "tYFPPHJ1DMX")

**Example Request:**
```bash
curl --location -g '/orders/{{order_number}}/products' \
  --header 'Authorization: Bearer {token}'
```

**Response:**
```json
{
  "data": {
    "id": 106316,
    "number": "tYFPPHJ1DMX",
    "total_products": null,
    "currency": {
      "id": 2,
      "icon": "€",
      "name": "EUR"
    },
    "actor": {
      "id": 139558,
      "given_name": "John",
      "family_name": "Doe",
      "full_name": "John Doe",
      "email": "john@goworkwize.com"
    },
    "receiver": "",
    "receiver_type": "office",
    "status": "Processed",
    "products": [
      {
        "id": 295774,
        "order_id": 106316,
        "name": "Apple, MacBook Air, M3, 2024, 13\", 16GB RAM, 512GB SSD, QWERTY US, Silver, Laptops",
        "type": "Buy",
        "short_description": "Apple, Laptops, 13\", 16GB RAM, 512GB SSD, Available in: IN",
        "article_code": "MXCT3HN/A",
        "product_quantity": 1,
        "images": [
          "https://workwize-bucket.s3.eu-west-3.amazonaws.com/products/1724235022-3JUaBSonT8j5U731RUel72f43c54-2807-4423-a851-f7783db9e9ec.jpg"
        ],
        "price": true,
        "invoice_price": 188011,
        "invoice_currency": "XCR",
        "supplier": {
          "id": 318,
          "name": "Dynacons MDM",
          "hasShipment": 1
        },
        "status": "order_placed"
      }
    ],
    "buy_subtotal": 2,
    "rent_subtotal": 0
  }
}
```

### Offices

#### Get All Offices
```
GET /offices
```
Returns a paginated list of all office locations with their addresses and manager information.

**Example Request:**
```bash
curl --location '/offices' \
  --header 'Authorization: Bearer {token}'
```

**Response:**
```json
{
  "data": [
    {
      "id": 27643,
      "name": "Amsterdam Office",
      "employer_id": 490,
      "manager_id": 139558,
      "created_at": "2025-02-06T10:36:48.000000Z",
      "updated_at": "2025-02-06T10:36:48.000000Z",
      "manager": {
        "id": 139558,
        "name": "John",
        "last_name": "Doe",
        "phone_number": "11111111111",
        "email": "John@goworkwize.com",
        "display_name": "John Doe",
        "role": {
          "id": 4,
          "display_name": "Employer Admin",
          "name": "employer-admin"
        }
      },
      "address": {
        "id": 136667,
        "city": "Amsterdam",
        "country": {
          "id": 32,
          "name": "Netherlands",
          "code": "NL",
          "requires_tin": false
        },
        "company_name": null,
        "country_id": 32,
        "address_line_1": "Damstraat 1",
        "address_line_2": "",
        "region": "Noord-Holland",
        "postcode": "1012JS",
        "postal_code": "1012JS",
        "additional_address_line": "",
        "name": "Jan",
        "first_name": "Jan",
        "last_name": "De Vries",
        "email": "jan.devries@example.nl",
        "phone_number": "+31 20-1234567"
      }
    },
    {
      "id": 27644,
      "name": "London Office",
      "employer_id": 490,
      "manager_id": 139558,
      "created_at": "2025-02-06T10:36:48.000000Z",
      "updated_at": "2025-02-06T10:36:48.000000Z",
      "manager": {
        "id": 139558,
        "name": "John",
        "last_name": "Doe",
        "email": "John@goworkwize.com",
        "display_name": "John Doe"
      },
      "address": {
        "id": 136668,
        "city": "London",
        "country": {
          "id": 15,
          "name": "United Kingdom",
          "code": "GB",
          "requires_tin": false
        },
        "address_line_1": "221B Baker Street",
        "region": "Greater London",
        "postal_code": "NW1 6XE",
        "first_name": "John",
        "last_name": "Smith",
        "email": "john.smith@example.co.uk",
        "phone_number": "+44 20-7946-0958"
      }
    }
  ],
  "links": {
    "first": "https://prod-back.goworkwize.com/api/public/offices?page=1",
    "last": "https://prod-back.goworkwize.com/api/public/offices?page=1",
    "prev": null,
    "next": null
  },
  "meta": {
    "current_page": 1,
    "from": 1,
    "last_page": 1,
    "per_page": 20,
    "to": 5,
    "total": 5
  }
}
```

**Notes:**
- Default pagination: 20 items per page
- Each office includes nested manager and address objects
- Address includes full country information with country code
- Manager may include nested employee, department, and employer details (truncated in example for brevity)

### Warehouses

#### Get All Warehouses
```
GET /warehouses
```
Get a list of warehouses available as an offboard destination.

**Query Parameters:**
- `include` (string, optional) - Comma-separated list of relationships to include (e.g., `countries`)

**Example Request:**
```bash
curl --location '/warehouses?include=countries' \
  --header 'Authorization: Bearer {token}'
```

**Response:**
```json
[
  {
    "id": 1,
    "warehouse_provider": "logistic_plus",
    "name": "Logistics Plus",
    "warehouse_code": "LDW",
    "created_at": "2023-06-22T13:39:37.000000Z",
    "updated_at": "2024-12-20T07:47:46.000000Z",
    "countries": [
      {
        "id": 15,
        "name": "United Kingdom",
        "code": "GB",
        "requires_tin": false
      },
      {
        "id": 337,
        "name": "Jersey",
        "code": "JE",
        "requires_tin": false
      }
    ]
  },
  {
    "id": 2,
    "warehouse_provider": "logistic_plus",
    "name": "Logistics Plus",
    "warehouse_code": "ER3",
    "created_at": "2023-06-22T13:39:37.000000Z",
    "updated_at": "2024-12-20T07:47:46.000000Z",
    "countries": [
      {
        "id": 46,
        "name": "United States",
        "code": "US",
        "requires_tin": false
      }
    ]
  },
  {
    "id": 4,
    "warehouse_provider": "logistic_plus",
    "name": "Logistics Plus",
    "warehouse_code": "VEW",
    "created_at": "2023-08-23T10:51:57.000000Z",
    "updated_at": "2024-12-20T07:47:46.000000Z",
    "countries": [
      {
        "id": 3,
        "name": "Austria",
        "code": "AT",
        "requires_tin": false
      },
      {
        "id": 5,
        "name": "Belgium",
        "code": "BE",
        "requires_tin": false
      },
      {
        "id": 32,
        "name": "Netherlands",
        "code": "NL",
        "requires_tin": false
      }
      // ... (26 total European countries)
    ]
  },
  {
    "id": 6,
    "warehouse_provider": "logistic_plus",
    "name": "Logistics Plus",
    "warehouse_code": "LPB",
    "created_at": "2024-02-12T09:15:27.000000Z",
    "updated_at": "2024-12-20T07:47:46.000000Z",
    "countries": [
      {
        "id": 329,
        "name": "India",
        "code": "IN",
        "requires_tin": true
      }
    ]
  },
  {
    "id": 7,
    "warehouse_provider": "logistic_plus",
    "name": "Logistics Plus",
    "warehouse_code": "LBZ",
    "created_at": "2024-02-12T09:15:27.000000Z",
    "updated_at": "2025-01-10T09:27:48.000000Z",
    "countries": [
      {
        "id": 273,
        "name": "Brazil",
        "code": "BR",
        "requires_tin": true
      }
    ]
  },
  {
    "id": 8,
    "warehouse_provider": "logistic_plus",
    "name": "Logistics Plus",
    "warehouse_code": "YYZ",
    "created_at": "2024-07-17T08:08:55.000000Z",
    "updated_at": "2024-12-20T07:47:46.000000Z",
    "countries": [
      {
        "id": 47,
        "name": "Canada",
        "code": "CA",
        "requires_tin": false
      }
    ]
  },
  {
    "id": 9,
    "warehouse_provider": "logistic_plus",
    "name": "Logistics Plus",
    "warehouse_code": "SYD",
    "created_at": "2024-07-17T08:08:55.000000Z",
    "updated_at": "2024-12-20T07:47:46.000000Z",
    "countries": [
      {
        "id": 259,
        "name": "Australia",
        "code": "AU",
        "requires_tin": false
      }
    ]
  },
  {
    "id": 10,
    "warehouse_provider": "logistic_plus",
    "name": "Logistics Plus",
    "warehouse_code": "LPP",
    "created_at": "2024-09-23T07:50:02.000000Z",
    "updated_at": "2024-12-20T07:47:46.000000Z",
    "countries": [
      {
        "id": 387,
        "name": "Philippines",
        "code": "PH",
        "requires_tin": false
      }
    ]
  },
  {
    "id": 11,
    "warehouse_provider": "logistic_plus",
    "name": "Logistics Plus",
    "warehouse_code": "MXW",
    "created_at": "2024-10-21T10:45:02.000000Z",
    "updated_at": "2024-12-20T07:47:46.000000Z",
    "countries": [
      {
        "id": 361,
        "name": "Mexico",
        "code": "MX",
        "requires_tin": false
      }
    ]
  }
]
```

**Notes:**
- Returns a flat array (no pagination)
- Warehouse codes: LDW (UK), ER3 (US), VEW (Europe), LPB (India), LBZ (Brazil), YYZ (Canada), SYD (Australia), LPP (Philippines), MXW (Mexico)
- VEW warehouse serves 26 European countries (truncated in example for brevity)
- `requires_tin` indicates if country requires tax identification number (true for India and Brazil)
- All current warehouses use "logistic_plus" as provider

### Offboards

#### Get All Offboards
```
GET /offboards
```
Returns a paginated list of all offboarding records with employee information, assets, and destination details.

**Query Parameters:**
- `page` (integer, optional) - Page number for pagination

**Example Request:**
```bash
curl --location '/offboards' \
  --header 'Authorization: Bearer {token}'
```

**Response:**
```json
{
  "code": 200,
  "success": true,
  "status": true,
  "message": null,
  "data": [
    {
      "assets_count": 2866,
      "id": "17388382082864",
      "employee_id": "137080",
      "employee_name": "Leland Brekke",
      "name": "Leland Brekke",
      "city": "Faheyborough",
      "address_line_1": "Veum Drive",
      "postal_code": "65560-4182",
      "address_line_2": "12091",
      "region": "Tennessee",
      "country_id": 32,
      "country": {
        "id": 32,
        "name": "Netherlands",
        "code": "NL",
        "requires_tin": false
      },
      "extra_info": "Molestiae sint esse quia voluptatibus quia autem quam aut.",
      "email": "camila.kirlin@example.org",
      "phone_number": "615-310-9507",
      "company_name": "Omar Test",
      "approved_at": null,
      "status": "in_transit_to_warehouse",
      "type": null,
      "assets": [
        {
          "id": 66507893,
          "name": "Apple, MacBook Air, M3, 2024, 15\", 16GB RAM, 512GB SSD, QWERTY UK, Silver, Laptops",
          "category": {
            "id": 86,
            "name": "Laptops",
            "created_at": "2021-05-05T15:28:06.000000Z",
            "updated_at": "2021-05-05T15:28:06.000000Z"
          },
          "location": {
            "location_id": 137080,
            "location_type": "employee",
            "location_detail": {
              "first_name": "Leland",
              "last_name": "Brekke",
              "address": {
                "address_line_1": "Veum Drive",
                "address_line_2": "12091",
                "postal_code": "65560-4182",
                "additional_address_line": "Port",
                "city": "Faheyborough",
                "region": "Tennessee",
                "email": "leland.brekke@omartest.com",
                "phone_number": "1-805-377-8865"
              },
              "team": "Sales"
            }
          },
          "note": null,
          "serial_code": "YE8MJNJOAQ",
          "invoice_price": 1,
          "invoice_currency": null,
          "external_reference": null,
          "warehouse_status": "available",
          "condition": "new"
        }
      ],
      "created_at": "2025-02-06T10:36:48.000000Z",
      "notified_employee_at": null,
      "requestor_id": 490,
      "offboarded_by": null,
      "offboarded_by_name": null,
      "destination_type": "warehouse",
      "destination_id": 7,
      "destination_name": "Warehouse BR",
      "shipments": []
    },
    {
      "assets_count": 2866,
      "id": "17388382082865",
      "employee_id": "137085",
      "employee_name": "Walter Rempel",
      "status": "details_confirmed",
      "destination_type": "warehouse",
      "destination_id": 7,
      "destination_name": "Warehouse BR",
      "assets": [
        {
          "id": 66507908,
          "name": "Apple, MacBook Air, M3, 2024, 13.6\", 16GB RAM, 512GB SSD, French AZERTY, Space Grey, Laptops",
          "serial_code": "7XVRUAB9P6",
          "warehouse_status": "available",
          "condition": "new"
        }
      ],
      "shipments": []
    }
  ],
  "links": {
    "first": "https://prod-back.goworkwize.com/api/public/offboards?page=1",
    "last": "https://prod-back.goworkwize.com/api/public/offboards?page=1",
    "prev": null,
    "next": null
  },
  "meta": {
    "current_page": 1,
    "from": 1,
    "last_page": 1,
    "per_page": 15,
    "to": 2,
    "total": 2
  },
  "errors": [],
  "redirect": ""
}
```

**Notes:**
- Response wrapped in `{code, success, status, message, data, links, meta, errors, redirect}` format
- Default pagination: 15 items per page
- Status values include: `in_transit_to_warehouse`, `details_confirmed`, and others
- `destination_type` can be "warehouse" or potentially other types
- Each offboard includes nested `assets` array with full asset details including location
- Assets include same structure as GET /assets endpoint (category, location, serial_code, etc.)
- `shipments` array tracks shipment details (empty if not yet shipped)
- Employee address information included at offboard level

### Users

#### Get All Users
```
GET /users
```
Returns a list of all users in the system.

### Addresses

#### Get All Addresses
```
GET /addresses
```
Returns a list of all addresses.

### Categories

#### Get All Categories
```
GET /categories
```
Returns a list of all asset/product categories.

### Invites

#### Get All Invites
```
GET /invites
```
Returns a list of all pending invitations.

### Tags

#### Get All Tags
```
GET /tags
```
Returns a list of all tags used in the system.

### Departments

#### Get All Departments
```
GET /departments
```
Returns a list of all departments.

## Notes

### Important API Behaviors

1. **Employee Endpoint Response Format**: The `/employees/{id}` endpoint returns data directly (not wrapped in a `success`/`data` object), while `/employees/{id}/addresses` uses the wrapped format.

2. **Asset Location Data**: 
   - Bulk `/assets` endpoint does NOT include warehouse/office location data
   - Individual `/assets/{id}` endpoint INCLUDES location data with `location_type` and `location_id`

3. **Pagination**: Most list endpoints support pagination via `page` and `per_page` query parameters.

4. **Authentication**: All endpoints require Bearer token authentication. API responds with 403 Forbidden if token is missing or invalid.

## Common Response Codes

- `200 OK` - Request successful
- `403 Forbidden` - Invalid or missing authentication token
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error
