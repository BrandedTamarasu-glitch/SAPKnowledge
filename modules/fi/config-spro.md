---
module: fi
content_type: config-spro
ecc_version: "6.0"
ehp_range: "0-8"
confidence: high
last_verified: 2026-02-16
---

# Financial Accounting — SPRO/IMG Configuration

> ECC 6.0 reference. All paths use the "Financial Accounting (New)" node (introduced with New GL in ECC 6.0). For Classic GL systems, the root node is "Financial Accounting" without "(New)".

> **How to read this file:** Each config step shows the full IMG path string first, then the T-code shortcut in parentheses. Use the IMG path when navigating the tree manually; use the T-code to jump directly.

## GL Configuration

### Step 1: Define Chart of Accounts

**IMG Path:** Financial Accounting (New) ▸ General Ledger Accounting (New) ▸ Master Data ▸ G/L Accounts ▸ Preparations ▸ Edit Chart of Accounts List (OB13)

**What to do:**
1. Create a chart of accounts key (4 characters, e.g., CAUS for USA operations) or copy from SAP reference (INT = International)
2. Set description and maintenance language
3. Set the account length (typically 6 or 10 digits)
4. Optionally assign a group chart of accounts for consolidation

**Key fields:** KTOPL (chart of accounts key), account length. Do not change account length after accounts are created.

### Step 2: Assign Chart of Accounts to Company Code

**IMG Path:** Financial Accounting (New) ▸ General Ledger Accounting (New) ▸ Master Data ▸ G/L Accounts ▸ Preparations ▸ Assign Company Code to Chart of Accounts (OB62)

**What to do:**
1. Select company code, assign chart of accounts key from Step 1
2. Optionally assign a country chart of accounts for local statutory reporting
3. Save — this assignment cannot be easily changed after accounts are created

### Step 3: Maintain Fiscal Year Variant

**IMG Path:** Financial Accounting (New) ▸ Financial Accounting Global Settings (New) ▸ Ledgers ▸ Fiscal Year and Posting Periods ▸ Fiscal Year ▸ Maintain Fiscal Year Variant (OB29)

**What to do:**
1. Create or copy a fiscal year variant (K4 = calendar year, V3 = April-March fiscal year)
2. Define period dates for non-calendar fiscal years
3. Set number of special periods (typically 4, used for year-end adjustments)

**Note:** SAP delivers standard variants. Copy and modify rather than creating from scratch.

### Step 4: Assign Fiscal Year Variant to Company Code

**IMG Path:** Financial Accounting (New) ▸ Financial Accounting Global Settings (New) ▸ Ledgers ▸ Fiscal Year and Posting Periods ▸ Fiscal Year ▸ Assign Company Code to a Fiscal Year Variant (OB37)

**What to do:** Select company code, assign the fiscal year variant created in Step 3. Save.

### Step 5: Define Document Types

**IMG Path:** Financial Accounting (New) ▸ Financial Accounting Global Settings (New) ▸ Document ▸ Document Types ▸ Define Document Types for Entry View (OBA7)

**What to do:**
1. Review SAP-delivered document types: SA = GL posting, KR = vendor invoice, KZ = vendor payment, DR = customer invoice, DZ = customer payment, AA = asset posting
2. For each document type: assign number range, set account types allowed, set reversal document type
3. Create custom document types as needed

**Key fields:** BLART (document type key), NRART (number range), allowed account types.

### Step 6: Define Posting Keys

**IMG Path:** Financial Accounting (New) ▸ Financial Accounting Global Settings (New) ▸ Document ▸ Line Item ▸ Controls ▸ Define Posting Keys (OB41)

**What to do:** Review and adjust field status for each posting key. Standard posting keys:
- 40 = GL debit; 50 = GL credit
- 01 = customer invoice (debit); 11 = customer credit memo (credit)
- 31 = vendor invoice (credit); 21 = vendor credit memo (debit)
- 70 = asset debit; 75 = asset credit

**Note:** SAP delivers all standard posting keys. Rarely need to create custom ones — modify field status (required/optional/hidden) for existing keys as needed.

### Step 7: Define Field Status Variants and Groups

**IMG Path:** Financial Accounting (New) ▸ Financial Accounting Global Settings (New) ▸ Ledgers ▸ Fields ▸ Define Field Status Variants (OBC4)

**What to do:**
1. Create or copy a field status variant (copy 0001 = SAP standard)
2. Within the variant, define field status groups (G001 = general GL, G004 = bank accounts)
3. For each group, configure fields as Required, Optional, or Hidden across: general data, account assignments (cost center, profit center), payment transactions

**Key link:** Field status groups (FSTAG in SKB1) are assigned per GL account and control what appears on posting screens.

### Step 8: Define GL Account Groups

**IMG Path:** Financial Accounting (New) ▸ General Ledger Accounting (New) ▸ Master Data ▸ G/L Accounts ▸ Preparations ▸ Define Account Group (OBD4)

**What to do:**
1. Define account groups (e.g., 0001 = assets, 0010 = liabilities, 1000 = revenue)
2. For each group: assign number range and field status group
3. Account group controls required/optional fields when creating GL accounts in FS00

### Step 9: Open/Close Posting Periods

**IMG Path:** Financial Accounting (New) ▸ Financial Accounting Global Settings (New) ▸ Ledgers ▸ Fiscal Year and Posting Periods ▸ Posting Periods ▸ Open and Close Posting Periods (OB52)

**What to do:**
1. Enter the posting period variant
2. For each account type (A=assets, D=customers, K=vendors, S=GL, M=materials, +=all), set From Period and To Period
3. Save — effective immediately; no transport needed for period opens in production

**Gotcha:** Account type "+" acts as default; specific account type rows override it. Allows selective opening (e.g., keep GL open but close vendors).

---

## AP/AR Configuration

### Step 1: Define Payment Terms

**IMG Path:** Financial Accounting (New) ▸ Accounts Receivable and Accounts Payable ▸ Business Transactions ▸ Outgoing Invoices/Credit Memos ▸ Define Terms of Payment (OBB8)

**What to do:**
1. Create payment term key (e.g., 0001, Z030)
2. Set baseline date calculation (document date, posting date, or fixed day of month)
3. Define up to 3 installments with days and discount percentages (e.g., 14 days 2%, 30 days net)
4. Assign default for AP and/or AR

**Note:** Payment terms are assigned in LFB1.ZTERM (vendor) and KNB1.ZTERM (customer). They drive due date calculation in F110 and F-28.

### Step 2: Define Tolerance Groups

**IMG Path:** Financial Accounting (New) ▸ Accounts Receivable and Accounts Payable ▸ Business Transactions ▸ Incoming Invoices/Credit Memos ▸ Define Tolerance Groups for Employees (OBA3 for GL/vendor; OBA4 for customers)

**What to do:**
1. Define tolerance group key (blank key = default, applies to all users without explicit assignment)
2. Set upper limits for posting amounts per document and per line item
3. Set cash discount limits (amount and percentage allowed)
4. Assign users to tolerance groups via OB57

### Step 3: Define Dunning Procedures

**IMG Path:** Financial Accounting (New) ▸ Accounts Receivable and Accounts Payable ▸ Business Transactions ▸ Dunning ▸ Dunning Procedure ▸ Define Dunning Procedures (FBMP)

**What to do:**
1. Create dunning procedure (e.g., 0001 = standard)
2. Define number of dunning levels (e.g., 4: reminder, first notice, second notice, legal action)
3. For each level: set days overdue threshold, dunning text form, minimum amounts, interest calculation
4. Set dunning interval (days between successive dunning runs)
5. Assign dunning procedure to customer master (KNB1)

### Step 4: Configure Automatic Payment Program (FBZP)

**IMG Path:** Financial Accounting (New) ▸ Accounts Receivable and Accounts Payable ▸ Business Transactions ▸ Outgoing Payments ▸ Automatic Outgoing Payments ▸ Set Up All Company Codes for Payment Transactions (FBZP)

**What to do — FBZP is the central configuration hub for F110. It has five sub-areas:**

**1. All Company Codes** (FBZP → All Company Codes):
- Assign paying company code and sending company code
- Set outgoing payment tolerance, minimum payment amount

**2. Paying Company Codes** (FBZP → Paying Company Codes):
- For the paying company code: assign forms, set minimum payment amounts per currency
- Unlocks cross-company-code payment

**3. Payment Methods in Country** (FBZP → Payment Methods in Country):
- Define payment methods per country (C = check, T = bank transfer, E = EFT)
- Specify the DME program for each method (bank file format)
- Set whether a print program is needed (check printing)

**4. Payment Methods in Company Code** (FBZP → Payment Methods in Company Code):
- Per company code + payment method: min/max amounts, bank optimization, document type
- Assign check printing form or bank file format

**5. Bank Determination** (FBZP → Bank Determination):
- Rank available house bank accounts by currency and payment method
- Set available amounts for each bank account
- Controls which bank account F110 selects for each payment

**CRITICAL distinction:** FBZP is CONFIGURATION. F110 is EXECUTION. Complete FBZP configuration before running F110.

### Step 5: Define Vendor Account Groups

**IMG Path:** Financial Accounting (New) ▸ Accounts Receivable and Accounts Payable ▸ Vendor Accounts ▸ Master Data ▸ Preparations for Creating Vendor Master Data ▸ Define Account Groups with Screen Layout (Vendors) (OBD3)

**What to do:**
1. Create/review vendor account groups (KRED = standard creditor, LIEF = supplier)
2. For each group: define number range, set field status per segment (required/optional/hidden)

### Step 6: Define Customer Account Groups

**IMG Path:** Financial Accounting (New) ▸ Accounts Receivable and Accounts Payable ▸ Customer Accounts ▸ Master Data ▸ Preparations for Creating Customer Master Data ▸ Define Account Groups with Screen Layout (Customers) (OBD2)

**What to do:** Same structure as OBD3 but for customer account groups (KUNA = standard, DEBTR = debtor).

---

## Asset Accounting Configuration

> **CRITICAL — Configuration order:** Asset Accounting configuration steps must be executed in sequence. Doing them out of order causes system errors that are difficult to unwind. The mandatory sequence is:
> **EC08 → OAOB → OAOA → AO90 → AFAMA**

### Step 1: Copy Reference Chart of Depreciation (EC08)

**IMG Path:** Financial Accounting (New) ▸ Asset Accounting ▸ Organizational Structures ▸ Copy Reference Chart of Depreciation/Depreciation Areas (EC08)

**What to do:**
1. Copy a SAP reference chart of depreciation (1US = US GAAP, 1DE = German HGB) to create your chart
2. The copy brings all depreciation areas predefined (01 = book, 10 = tax, 15 = IFRS, 20 = cost accounting)
3. Review and activate/deactivate depreciation areas not needed

**Note:** Never configure Asset Accounting without completing this step first. The chart of depreciation defines all depreciation areas available to asset classes and assets.

### Step 2: Assign Chart of Depreciation to Company Code (OAOB)

**IMG Path:** Financial Accounting (New) ▸ Asset Accounting ▸ Organizational Structures ▸ Assign Chart of Depreciation to Company Code (OAOB)

**What to do:**
1. Select the company code
2. Assign the chart of depreciation from Step 1
3. Set the asset fiscal year (usually same as FI fiscal year variant)

**Note:** One company code = one chart of depreciation. This cannot be changed after assets are created.

### Step 3: Define Asset Classes (OAOA)

**IMG Path:** Financial Accounting (New) ▸ Asset Accounting ▸ Organizational Structures ▸ Asset Classes ▸ Define Asset Classes (OAOA)

**What to do:**
1. Create asset classes (e.g., 1000 = Buildings, 2000 = Vehicles, 3000 = Machinery and Equipment)
2. For each class: assign number range, screen layout, account determination key
3. Set default depreciation terms (depreciation key, useful life) that new assets inherit

### Step 4: Specify G/L Account Determination (AO90)

**IMG Path:** Financial Accounting (New) ▸ Asset Accounting ▸ Integration with the General Ledger ▸ Assign G/L Accounts (AO90)

**What to do:**
1. For each combination of chart of depreciation + account determination key + depreciation area:
2. Assign GL accounts for: asset balance sheet account, accumulated depreciation, depreciation expense, retirement gain/loss, clearing accounts for acquisitions
3. Save for each depreciation area separately

**Note:** AO90 requires that assigned GL accounts exist in SKB1 for the company code. Create GL accounts in FS00 first if needed. This is the AA-to-GL integration point.

### Step 5: Maintain Depreciation Keys (AFAMA)

**IMG Path:** Financial Accounting (New) ▸ Asset Accounting ▸ Depreciation ▸ Valuation Methods ▸ Depreciation Key ▸ Maintain Depreciation Key (AFAMA)

**What to do:**
1. Review delivered depreciation keys (LINR = straight-line to zero, DBNL = declining balance)
2. For each key: define calculation method (base method, declining balance, period control)
3. Create custom keys only when delivered keys don't match local statutory requirements

**Note:** Depreciation keys are assigned in asset class defaults (OAOA) and in ANLB per asset. AFAB uses these keys to calculate periodic depreciation.

---

## New GL Configuration

> **Assumption:** New GL is active (standard for ECC 6.0 post-2008). If Classic GL is still active, the "Financial Accounting (New)" SPRO node may not show New GL sub-nodes.

### Step 1: Activate New General Ledger Accounting

**IMG Path:** Financial Accounting (New) ▸ Financial Accounting Global Settings (New) ▸ Ledgers ▸ Ledger ▸ Activate New General Ledger Accounting

**What to do:** Set activation indicator for the client. One-time, irreversible activation. Once active, Classic GL tables (GLT0) stop being updated.

**Warning:** New GL activation is client-wide. No per-company-code activation — only deactivation.

### Step 2: Define Ledgers for General Ledger Accounting

**IMG Path:** Financial Accounting (New) ▸ Financial Accounting Global Settings (New) ▸ Ledgers ▸ Ledger ▸ Define Ledgers for General Ledger Accounting

**What to do:**
1. The leading ledger (0L) is automatically created; assign to accounting principle (IFRS, US GAAP, local GAAP)
2. Ledger 0L stores all postings to FAGLFLEXT and FAGLFLEXP
3. Only one leading ledger is allowed per client

### Step 3: Define and Activate Non-Leading Ledgers

**IMG Path:** Financial Accounting (New) ▸ Financial Accounting Global Settings (New) ▸ Ledgers ▸ Ledger ▸ Define and Activate Non-Leading Ledgers

**What to do:**
1. Create non-leading ledgers for parallel accounting (e.g., L1 = local GAAP, T1 = tax)
2. Assign each to an accounting principle
3. Activate for relevant company codes

**Use case:** Company reporting under both IFRS (leading ledger) and local GAAP (non-leading) maintains separate depreciation values via separate ledger assignments in OAOB/ANLB.

### Step 4: Activate Document Splitting

**IMG Path:** Financial Accounting (New) ▸ General Ledger Accounting (New) ▸ Business Transactions ▸ Document Splitting ▸ Activate Document Splitting

**What to do:**
1. Activate document splitting for the client (global activation)
2. Select splitting method (standard = 0000000012 in most implementations)
3. Enable "Inheritance" if passive splitting (inheriting segment/profit center) is required

**CRITICAL:** Document splitting activation is **client-level**. It applies to all company codes. To exclude specific company codes: Financial Accounting (New) ▸ Financial Accounting Global Settings (New) ▸ Ledgers ▸ Ledger ▸ Deactivate Document Splitting per Company Code.

### Step 5: Define Document Splitting Characteristics

**IMG Path:** Financial Accounting (New) ▸ General Ledger Accounting (New) ▸ Business Transactions ▸ Document Splitting ▸ Define Document Splitting Characteristics for General Ledger Accounting

**What to do:**
1. Select characteristics to split on every document line (commonly: Segment, Profit Center, Business Area)
2. For each characteristic, set whether zero balance is required (if yes, a zero-balance clearing account is needed)

### Step 6: Classify G/L Accounts for Document Splitting

**IMG Path:** Financial Accounting (New) ▸ General Ledger Accounting (New) ▸ Business Transactions ▸ Document Splitting ▸ Classify G/L Accounts for Document Splitting

**What to do:** Assign each GL account to an item category (01000 = balance sheet, 02000 = customer receivables, 03000 = vendor payables, 04000 = cash accounts). Item category determines how the account participates in splitting rules.

### Step 7: Classify Document Types for Document Splitting

**IMG Path:** Financial Accounting (New) ▸ General Ledger Accounting (New) ▸ Business Transactions ▸ Document Splitting ▸ Classify Document Types for Document Splitting

**What to do:** Assign each document type to a business transaction and variant (e.g., KR → 0300 = vendor invoice). Controls which splitting rule the system applies.
