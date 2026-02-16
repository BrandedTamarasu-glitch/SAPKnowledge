# SAP ECC 6 — Org Structure

## Hierarchy

```
Client (Mandt)
├── Company Code (Bukrs) ── fiscal year, currency, chart of accounts
│   ├── Plant (Werks) ── manufacturing, procurement hub
│   │   └── Storage Location (Lgort) ── physical inventory
│   └── Business Area (optional, cross-company reporting)
├── Controlling Area (Kokrs) ── can span company codes
│   ├── Cost Center (Kostl)
│   └── Profit Center (Prctr)
├── Sales Organization (Vkorg)
│   └── Distribution Channel (Vtweg)
│       └── Division (Spart)
│           └── = Sales Area (Vkorg + Vtweg + Spart)
└── Purchasing Organization (Ekorg)
    └── Purchasing Group (Ekgrp)
```

## Key Assignments

- Plant → Company Code (1:1)
- Sales Org → Company Code (many:1)
- Purchasing Org → Company Code (many:1) or Plant (many:1)
- Controlling Area → Company Code (1:many)
