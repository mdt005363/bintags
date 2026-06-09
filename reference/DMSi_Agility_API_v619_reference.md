# DMSi Agility Public API — v619 Reference

Extracted from the official Postman documentation (v619). 192 endpoints, 14 services.

## HIO production connection
- Base: `https://api-1634-1.dmsi.com/.../AgilityPublic/rest`  (docs show dev sandbox `api-8101-1.dmsi.dev/develtestdb`)
- Branch: `01HIO` | User: `HIOAPI` | House/CustomerID: `1`
- Auth: POST `Session/Login` -> returns `ContextId` (SessionContextId), valid up to 24h (default 4h idle timeout)
- Required headers on most calls: `ContextId`, `Branch`, `Content-Type: application/json`
- All calls HTTPS only (http rejected). Payloads TLS-encrypted in transit.

## Data types & conventions
- Date: `yyyy-mm-dd` (blank = `null`). DateTime: `yyyy-mm-ddThh:mm:ss`. Time: military `00:00`-`23:59`.
- Decimal/Integer default `0` (but 0 is valid for some fields e.g. Price — read business rules).
- Clear free-form char fields with `""` or `null` (test in non-prod first).
- Payload wrapper: `{ "request": { "ds<Name>": { "dt<Name>": [ { ...fields } ] } } }` (casing is sensitive).

## Data chunking (select methods)
- `RecordFetchLimit` (records per call; capped by System Config max chunk size)
- `ChunkStartPointer` (start record; from prior `NextChunkStartPointer`)
- `MoreResultsAvailable` (output: more records exist)


---

# AccountsPayable Service  (3 methods)

## InvoiceCreate
`POST /AccountsPayable/InvoiceCreate`

Purpose
Creates an A/P invoice
Required Inputs

InvoiceID

InvoiceDate

SupplierID

SupplierRemitToSequence; dtAPExpenseAccounts and/or dtAPInvoiceOrders (when applicable)

Optional Inputs

PostingPeriod

PostingYear

Notes

You must include at least one A/P Invoice Orders detail or A/P Expense Accounts detail with the A/P Invoice Header

When a field contains a value of null, the system creates the A/P Invoice based on the default specified in Agility

Multiple transactions and/or expense G/L accounts can be associated with a single A/P Invoice, and the net total creates either an A/P Invoice or an A/P Credit memo

To use the discountable field, ‘Apply ADF in A/P’ must be set on the associated payment terms code. The voucher ADF amount will be the difference between the specified AP clearing amount (dtInvoiceOrdersRequest amount) and the discountable amount.

The SuppressCurrencyMatch field is available in v543

The dtInvoiceHeaderRequest TaxAmount field is available in v549

When TaxAmount is provided in both the dtInvoiceHeaderRequest and the dtInvoiceOrdersRequest, only the dtInvoiceHeaderRequest TaxAmount value is used

With v549, non-taxable vouchers with a tax amount can be created when the dtInvoiceHeaderRequest section includes a value for TaxAmount

When the PostingPeriod and PostingYear tags are not included in the request, has a value of 0, or value of 'null', the system assigns the default posting period and year to the invoice. If the A/P Parameters flag 'Validate invoice date with period entered' is set, the system assigns a posting period and year to the invoice that matches the month and year of the invoice date entered.

When creating expense invoices, the GLExpAccount tag cannot contain an A/P clearing account number.

When the CostType value is not included with the request, has a value of blank, or value of 'null', the system uses the default cost type assigned to the supplier record.

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v539

**Request body:**
```json
{
    "request": {
        "dsInvoiceRequest": {
            "dtInvoiceHeaderRequest": [
                {
                    "InvoiceID": "",
                    "InvoiceDate": "2022-06-30",
                    "PostingPeriod": 0,
                    "PostingYear": 0,
                    "SupplierID": "",
                    "SupplierRemitToSequence": 0,
                    "EnforceSupplierMatch": "",
                    "PaymentMethod": "",
                    "PaymentTermsCode": "",
                    "DueDate": "2022-06-30",
                    "BatchID": 0,
                    "Requires1099": "",
                    "Payment1099TypeCode": "",
                    "Taxable": "",
                    "TaxCode": "",
                    "DiscountDate": "",
                    "DiscountAmount": "",
                    "VoucherStatus": "",
                    "FreightID": "",
                    "CashGLAccount": "",
                    "DiscountGLAccount": "",
                    "APGLAccount": "",
                    "PaymentRemark": "",
                    "HandlingCode": "",
                    "HandlingCodeAddlInfo": "",
                    "SuppressCurrencyMatch": false
                }
            ],
            "dtInvoiceOrdersRequest": [
                {
                    "TranOrAPReconID": "0",
                    "Amount": 0,
                    "DiscountableAmount": 0,
                    "TaxAmount": 0,
                    "CostType": ""
                }
            ],
            "dtExpenseAccountsRequest": [
                {
                    "GLExpAccount": "",
                    "Amount": 0,
                    "ProjectNumber": "",
                    "Remark": ""
                }
            ]
        }
    }
}
```

## InvoiceDelete
`POST /AccountsPayable/InvoiceDelete`

Purpose
Allow users to void an existing A/P voucher
Required Inputs

VoucherNumber

Optional Inputs

UseVoucherPeriod

Notes

None

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v615

**Request body:**
```json
{
    "request": {
        "InvoiceDeleteJSON": {
            "dsAPInvoiceDeleteRequest": {
                "dtAPInvoiceDeleteRequest": [
                    {
                        "VoucherNumber": 0,
                        "UseVoucherPeriod": true
                    }
                ]
            }
        }
    }
}
```

## InvoiceUpdate
`POST /AccountsPayable/InvoiceUpdate`

Purpose
Allow users to modify existing A/P vouchers
Required Inputs

VoucherNumber

Optional Inputs

InvoiceID

PaymentMethod

PaymentTermsCode

DueDate

DiscountAmount

Notes

None

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v615

**Request body:**
```json
{
    "request": {
        "InvoiceUpdateJSON": {
            "dsAPInvoiceUpdateRequest": {
                "dtAPInvoiceUpdateHeader": [
                    {
                        "VoucherNumber": 0,
                        "InvoiceID": "",
                        "PaymentMethod": "",
                        "PaymentTermsCode": "",
                        "DueDate": null,
                        "DiscountAmount": 0.0,
                        "DiscountDate": null
                    }
                ]
            }
        }
    }
}
```

---

# AccountsReceivable Service  (15 methods)

## BalancesList
`POST /AccountsReceivable/BalancesList`

Purpose
Returns the current AR aging information and related invoices
Required Inputs

CustomerID

Optional Inputs

N/A

Notes

This method returns sold-to level information only, regardless of the levels for printing statements defined on the customer record

If you have data allocations to some but not all of the ship-tos for a customer, the method returns only A/R balance information for the ship-tos you are authorized to access

This method may return information for branches the user does not have access to, depending on the setting the View A/R Detail for All Branches action allocation

The Type and Cycle Code settings on the customer record are ignored when retrieving information using this method

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Valid values for CustomerID come from CustomersList or CustomerShiptoList

Version Deployed
v539

**Request body:**
```json
{
    "request": {
        "CustomerID": ""
    }
}
```

## CashReceiptsACHPayment
`POST /AccountsReceivable/CashReceiptsACHPayment`

Purpose
Creates ACH cash on account using the bank specified
Required Inputs

CustomerID

ShiptoSequence

BilltoSequence

BankGUID

AmountTendered

Optional Inputs

PaymentDate

Notes

The ‘Enter Payment via CashReceiptsPayment API’ action allocation must be granted to use this request.

Data allocations must be granted for the customer specified.

Whether a customer bill-to or ship-to sequence is required is determined by the ‘Cash and finance charge level’ set in AR Parameters. If set to bill-to, you can use a bill-to, ship-to, or a valid combination of both. If set to ship-to, a ship-to sequence must be provided, and any provided bill-to sequence will be ignored.

The BankGUID input is a system-assigned value that uniquely identifies the Customer Bank record. This is not the bank account.

When AR Parameters ‘Cash and finance charge level’ is set to “Ship-to”, the BankGUID value is validated against all three levels of Customer Bank records (“Ship-to”, “Bill-to” or “Customer”) based on the ship-to sequence specified.

When AR Parameters ‘Cash and finance charge level’ is set to “Bill-to”, any ship-to specified must be valid for the bill-to sequence specified. The BankGUID value is validated against all three levels of Customer Bank records based on the bill-to and/or ship-to sequence specified.

PaymentDate defaults to the current day if no date is provided.

Relationships

ContextId and Branch come from Login

BankGUID comes from CustomerACHBankList

Version Deployed
v555

**Request body:**
```json
{
    "request": {
        "CashReceiptsPaymentJSON": {
            "dsCashReceiptsPaymentRequest": {
                "dtCashReceiptsPaymentRequest": [
                    {
                        "CustomerID": "",
                        "ShiptoSequence": 1,
                        "BilltoSequence": 1,
                        "BankGUID": "",
                        "AmountTendered": 0,
                        "PaymentDate": ""
                    }
                ]
            }
        }
    }
}
```

## CashReceiptsCCManualPayment
`POST /AccountsReceivable/CashReceiptsCCManualPayment`

Purpose
Creates cash on a customer account using the ID from a previously processed transaction.
Required Inputs

CustomerID

ShiptoSequence

BilltoSequence

ProcessorTransactionID

Optional Inputs

PaymentDate

Notes

Access to the Credit Card Interface must be granted to use this request.

The ‘Enter Payment via CashReceiptsPayment API’ action allocation must be granted to use this request.

Data allocations must be granted for the customer specified.

Whether a customer bill-to or ship-to sequence is required is determined by the ‘Cash and finance charge level’ set in AR Parameters. If set to bill-to, you can use a bill-to, ship-to, or a valid combination of both. If set to ship-to, a ship-to sequence must be provided, and any provided bill-to sequence will be ignored.

This request is used to record transactions in Agility that have taken place in eCommerce platforms. Use the TransactionID provided by WorldPay on the original transaction as the ProcessorTransactionID when sending the request to Agility.

PaymentDate defaults to the current day if no date is provided.

Relationships

ContextId and Branch come from Login

Version Deployed
v555

**Request body:**
```json
{
    "request": {
        "CashReceiptsPaymentJSON": {
            "dsCashReceiptsPaymentRequest": {
                "dtCashReceiptsPaymentRequest": [
                    {
                        "CustomerID": "",
                        "ShiptoSequence": 1,
                        "BilltoSequence": 1,
                        "ProcessorTransactionID": "",
                        "PaymentDate": ""
                    }
                ]
            }
        }
    }
}
```

## CashReceiptsCCTokenPayment
`POST /AccountsReceivable/CashReceiptsCCTokenPayment`

Purpose
Creates cash on a customer account using a saved credit card token
Required Inputs

CustomerID

ShiptoSequence

BilltoSequence

PaymentAccountID

AmountTendered

Optional Inputs

PaymentDate

AllowTokenDate

Surcharge

SurchargeBasis

UseAgilitySurcharge

Notes

Access to the Credit Card Interface must be granted to use this request.

The ‘Enter Payment via CashReceiptsPayment API’ action allocation must be granted to use this request.

Data allocations must be granted for the customer specified.

Whether a customer bill-to or ship-to sequence is required is determined by the ‘Cash and finance charge level’ set in AR Parameters. If set to bill-to, you can use a bill-to, ship-to, or a valid combination of both. If set to ship-to, a ship-to sequence must be provided, and any provided bill-to sequence will be ignored.

This request is processed immediately in Agility using a PaymentAccountID.

If the PaymentAccountID is not already in the customer’s saved credit cards list, the AllowDeleteToken value must be set to true. Deleted tokens cannot be reused in subsequent requests.

AllowTokenDelete defaults to false.

PaymentDate defaults to the current day if no date is provided.

Detailed information about this payment is written to A/R remarks (ARREM).

If UseAgilitySurcharge is true, Surcharge and SurchargeBasis are ignored.

If UseAgilitySurcharge is false, the surcharge is calculated based on the values in Surcharge and SurchargeBasis. Surcharge discounts set at the bill-to or ship-to level are ignored.

You cannot add a surcharge via the Surcharge and SurchargeBasis fields if either of following are true.

A surcharge is not defined on the payment method.

The applicable bill-to/ship-to record, based on the value of the 'Credit card storage option on the sold-to record, is set to 'Do not calculate'.

Information intended for receipt creation is returned on both approved and declined transactions

Relationships

ContextId and Branch come from Login

Version Deployed
v555

**Request body:**
```json
{
    "request": {
        "CashReceiptsPaymentJSON": {
            "dsCashReceiptsPaymentRequest": {
                "dtCashReceiptsPaymentRequest": [
                    {
                        "CustomerID": "",
                        "ShiptoSequence": 1,
                        "BilltoSequence": 1,
                        "PaymentAccountID": "",
                        "AllowTokenDelete": false,
                        "AmountTendered": 0,
                        "PaymentDate": "",
                        "Surcharge": 0,
                        "SurchargeBasis": "",
                        "UseAgilitySurcharge": false
                    }
                ]
            }
        }
    }
}
```

## CreditStatusUpdate
`POST /AccountsReceivable/CreditStatusUpdate`

Purpose
Change the credit hold status of an existing Sales Order
Required Inputs

Branch

SalesOrderID

ShipmentNum

CreditStatus

Optional Inputs

PendingNote

Notes
Relationships

Valid Values for CreditStatus are Hold, Pending, Approved

Version Deployed
v601

**Request body:**
```json
{
    "request": {
        "SalesOrderID": 0,
        "ShipmentNum": 0,
        "CreditStatusUpdateJSON": {
            "dsCreditStatusUpdateRequest": {
                "dtCreditStatusUpdateRequest": [
                    {
                        "CreditStatus": "",
                        "PendingNote": ""
                    }
                ]
            }
        }
    }
}
```

## CustomerACHBankList
`POST /AccountsReceivable/CustomerACHBankList`

Purpose
Returns a list of approved customer bank records for a specific customer ship-to or bill-to
Required Inputs

CustomerID

ShiptoSequence

BilltoSequence

Optional Inputs

N/A

Notes

You must specify either a bill-to or ship-to sequence. If a bill-to is not provided, the bill-to assigned to the ship-to sequence is used.

User must have data allocations granted for the customer specified.

The BankGUID input is a system-assigned value that uniquely identifies the Customer Bank record. This is not the bank account.

Only banks set to approved for ACH processing display.

When a ship-to sequence is specified, the system uses the ship-to bank if it exists. If it does not exist, the bill-to bank is used. If a bill-to bank does not exist, the customer bank is used.

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v556

**Request body:**
```json
{
    "request": {
        "CustomerACHBankListJSON": {
            "dsCustomerRequest": {
                "dtCustomerRequest": [
                    {
                        "CustomerID": "",
                        "ShiptoSequence": 1,
                        "BilltoSequence": 1
                    }
                ]
            }
        }
    }
}
```

## CustomerBilltoBalancesList
`POST /AccountsReceivable/CustomerBilltoBalancesList`

Purpose
Returns the current AR aging information at the customer bill-to level
Required Inputs

CustomerID

Optional Inputs

BilltoSequence

Notes

The method only returns A/R balance information for customers the user is authorized to access

When BilltoSequence is not included in the request or is 0 then all bill-tos are returned for the CustomerID provided

Relationships

Valid values for CustomerID come from CustomersList

Valid values for BilltoSequence come from CustomerBilltosList

Version Deployed
v618

**Request body:**
```json
{
    "request": {
        "CustomerID": "",
        "BilltoSequence ": 0
    }
}
```

## CustomerOpenActivity
`POST /AccountsReceivable/CustomerOpenActivity`

Purpose
Returns a list of open orders, open quotes, open credit memos, and the AR balances for a specific customer
Required Inputs

CustomerID

Optional Inputs

ShiptoSequence

Notes

This method is conditioned to return only open sales orders, credit memos, and quotes. Invoiced and cancelled transactions are excluded.

This method can be run with or without a ShiptoSequence. When run with a ShiptoSequence, AR balance information is returned at the sold-to level only

CustomerOpenActivity returns the BalanceResponse at the sold-to level across all branches, however detail returned on the transaction level will respect the header branch.

Relationships

ContextId comes from Login

Alternate branches come from BranchList

Valid values for CustomerID come from CustomersList or CustomerShiptoList

Valid values for ShiptoSequence come from CustomerShiptoList

Version Deployed
v539

**Request body:**
```json
{
    "request": {
        "CustomerID": "",
        "ShiptoSequence": 1
    }
}
```

## CustomerShiptoBalancesList
`POST /AccountsReceivable/CustomerShiptoBalancesList`

Purpose
Returns the current AR aging information at the customer ship-to level
Required Inputs

CustomerID

Optional Inputs

ShiptoSequence

BilltoSequence

Notes

The method only returns A/R balance information for the ship-tos the user is authorized to access

When ShiptoSequence is not included in the request or is 0 then all ship-tos assigned to the user are returned for the CustomerID provided

When BilltoSequence is included, the results will only include valid ship-tos that are related to the bill-to sequence

Relationships

Valid values for CustomerID come from CustomersList

Valid values for ShiptoSequence come from CustomerShiptosList or CustomerShiptosInChunksList

Valid values for BilltoSequence come from CustomerBilltosList

Version Deployed
v618

**Request body:**
```json
{
    "request": {
        "CustomerID": "",
        "ShiptoSequence": 0,
        "BilltoSequence": 0
    }
}
```

## InvoicePayment
`POST /AccountsReceivable/InvoicePayment`

Purpose
Applies payments to invoices
Required Inputs

CustomerID

dtInvoiceRequest (BranchID, InvoiceNumber, PaymentAmount, DiscountAmount)

dtPaymentRequest (BranchID, Invoice Number, PaymentAmount)

Optional Inputs

PaymentDate

InstallmentSequence

Remark

Notes

Multiple dtInvoiceRequest and/or dtPaymentRequest can be specified

If PaymentDate is not specified, the current date is used

Includes payments with the following ref_types: CA (cash on account), CM (credit memo), CI (credit invoice).

Includes invoices with the following ref_types: IN (invoice), FC (finance charge invoice), DM (debit memo).

PaymentAmount represents the amount of payment being applied to the invoice not including the discount amount.

Each payment and invoice require a non-zero PaymentAmount.

The total PaymentAmount of all invoices must be equal to the total PaymentAmount of all payments.

The total of PaymentAmount + DiscountAmount must be <= the open amount of the invoice. For payments, PaymentAmount cannot exceed the open amount of the payment.

All PaymentAmount and DiscountAmount values are processed as a positive regardless of the positive or negative value included in the request.

Invoices and payments are validated against the current branch’s A/R sharing branch. BranchID represents the branch the invoice/payment exists.

This method may apply payments for branches the user does not have access to, depending on the setting the View A/R Detail for All Branches security action.

Remarks sent create a standard A/R Remark for the invoice and the payment, are set to editable, and are not set to print on statements. Remarks must be less than 6000 characters.

Reason Codes created in Reason Code Maintenance with A/R open type and Available for use can be specified for invoices and payments.

When a customer short pays an invoice, the system can optionally assign a reason code to the record. Refer to the Short Pay Reason Codes section within the Processing Rules of A/R Cash Application for more information.

The following applies only to customers on Agility version 604 and above:

The InstallmentSequence is used if specifying an installment sequence when applying payments to installment invoices.

When the value in this field corresponds to an installment on the specified invoice, the system applies the payment to the specific installment.

When the value in this field is "0" and there are no payments with an installment sequence defined, the system applies the payment to the lowest (numerically) open installment until it is fully paid or the payment is fully applied.

If there are remaining payments to apply, the system continues to the next lowest installment until all invoices are paid or the payment is fully applied.

If a discount is specified on an installment invoice payment and the InstallmentSequence is “0”, the system applies the discount to the first installment.

When utilizing the InstallmentSequence field, the value must be zero or greater and cannot be left blank.

Relationships

ContextId and Branch come from Login

Version Deployed
v555

**Request body:**
```json
{
    "request": {
        "InvoicePaymentJSON": {
            "dsInvoicePaymentRequest": {
                "dtCustomerRequest": [
                    {
                        "CustomerID": "",
                        "PaymentDate": "",
                        "dtInvoiceRequest": [
                            {
                                "BranchID": "",
                                "InvoiceNumber": "",
                                "InstallmentSequence": 1,
                                "PaymentAmount": 0,
                                "DiscountAmount": 0,
                                "Remark": "",
                                "Reason Code": ""
                            }
                        ],
                        "dtPaymentRequest": [
                            {
                                "BranchID": "",
                                "InvoiceNumber": "",
                                "PaymentAmount": 0,
                                "Remark": "",
                                "Reason Code": ""
                            }
                        ]
                    }
                ]
            }
        }
    }
}
```

## InvoicesList
`POST /AccountsReceivable/InvoicesList`

Purpose
Returns a list of invoices, including invoice details, for a specific customer
Required Inputs

CustomerID

ShiptoSequence

IncludeOnlyOpenInvoices

InvoiceDateRangeStart

InvoiceDateRangeEnd

ChunkStartPointer

RecordFetchLimit

Optional Inputs

SearchBy

SearchValue

Notes

To request invoices for all ship-tos, enter a value of 0 in ShiptoSequence

This method allows a date range for criteria. Please see the Special notes for input values related to data topic for more information

This method allows a user to request a specific number of records. Please see the Chunking topic for more information

When including the SearchBy input, the only valid value is Order ID. The SearchValue input must be a valid transaction ID.

With a valid transaction ID entered, the CustomerID input can be sent with a blank value.

The following rules apply when displaying shipping tracking information:

When the InvoiceDetailSequence = 0, the tracking information is stored at the header

When the InvoiceDetailSequence is not 0, the tracking information applies to the invoice detail sequence specified

The system displays tracking information at the lowest level. For example, if a tracking number exists at the header level and another exists at the detail level, the system displays the detail level tracking number. If tracking numbers exist only at the header level, then the system displays these header level tracking numbers.

Relationships

Parent/Child relationship exists between dtInvoiceOrder and dtInvoiceDetail through InvoiceNumber. Please see Parent/Child relationship topic for more information

ContextId comes from Login

Alternate branches come from BranchList

Valid values for CustomerID come from CustomersList or CustomerShiptoList

Valid values for ShiptoSequence come from CustomerShiptosList

Please see Parent/Child relationship topic for more information on the following:

A one to many Parent/Child relationship exists between dtInvoiceOrderResponse and dtInvoiceDetailResponse through InvoiceNumber.

A one to many Parent/Child relationship exists between dtInvoiceOrderResponse and dtTrackingHeaderResponse through InvoiceNumber.

A one to many Parent/Child relationship exists between dtInvoiceDetailResponse and dtSerialNumberDetailResponse through Sequence.

The ShipVia is the stored on the shipment at the time of invoicing. If the stored value is blank, then the system displays the ship via value from the sales order header.

The PartNumber displays the part number stored on the so_detail. If this is blank, then the system searches for the related cross reference. If the cross reference is for a sheet good item, then the system finds the dimension-specific cross reference if available. If the item is a dimensional item but not a sheet good item, the system finds the 00x00x00 cross reference.

The ItemXrefUsedToOrder displays the item cross reference field from the Sales order detail.

Version Deployed
v539

**Request body:**
```json
{
    "request": {
        "SearchBy": "",
        "SearchValue": "",
        "CustomerID": "",
        "ShiptoSequence": 0,
        "IncludeOnlyOpenInvoices": false,
        "InvoiceDateRangeStart": "2019-03-02",
        "InvoiceDateRangeEnd": "2019-12-02",
        "ChunkStartPointer": "",
        "RecordFetchLimit": 0
    }
}
```

## PendingPaymentList
`POST /AccountsReceivable/PendingPaymentList`

Purpose
Returns a list of transactions with open pending payments for a specific customer ship-to, BankGUID, or payment account ID
Required Inputs

PaymentAccountID and/or CustomerID and ShiptoSequence OR

BankGUID and/or CustomerID and ShiptoSequence

Optional Inputs

N/A

Notes

To return a list of sales orders with pending payments, specify a customer ID and ship-to sequence and/or a payment account ID or BankGUID.

When CustomerID and ShipToSequence only are provided, the system returns data for current branch matching that customer ID and ship-to sequence. The user must have Data Allocations granted for the customer.

When PaymentAccountID or BankGUID only is provided, the system returns data for any branch with pending payments that match the payment account ID or BankGUID. Data Allocations are not validated.

When CustomerID, ShipToSequence, and PaymentAccountID or BankGUID are provided, the system returns data for any branch with pending payments that match both the customer and payment account ID or BankGUID. The user must have Data Allocations granted for the customer.

This method may return information for branches the user does not have access to, depending on the setting for the View A/R Detail for All Branches action allocation.

Relationships

ContextId and Branch come from Login

Version Deployed
v556

**Request body:**
```json
{
    "request": {
        "PendingPaymentJSON": {
            "dsPendingPaymentRequest": {
                "dtPendingPaymentRequest": [
                    {
                        "CustomerID": "",
                        "ShiptoSequence": 1,
                        "PaymentAccountID": "",
                        "BankGUID": ""
                    }
                ]
            }
        }
    }
}
```

## SavedCreditCardCreate
`POST /AccountsReceivable/SavedCreditCardCreate`

Purpose
Used to direct customers who store credit cards in Agility to a specified Hosted Payments page where they can enter a new credit card to save or use to process a new transaction
Required Inputs

CustomerID

ShiptoSequence

ReturnURL

Optional Inputs

N/A

Notes

Access to the Credit Card Interface must be granted to use this request.

User must have data allocations granted for the customer specified.

Only PCI compliant information is transferred. No sensitive data is sent.

Account information is not sent through the card issuer for authorization and only needs to pass a Mod10 check to be stored.

The response contains information necessary to identify, validate, and the initiate the account creation transaction with WorldPay.

TransactionSetupID uniquely identifies the transaction with WorldPay. The ID can only be used once expires 10 minutes after being generated.

ValidationCode is used to verify the saved card transaction. Compare the ValidationCode from this method with the ValidationCode returned by the HostedPaymentURL.

HostedPaymentURL directs the user to the Hosted Payment Page, which provides a GUI to enter and submit credit card information.

If you specify a ReturnURL in the request, the HostedPaymentURL will redirect to the ReturnURL once the transaction has either been successfully processed or cancelled. In the event of a successful account creation, the following fields are appended to the ReturnURL’s query string: HostedPaymentStatus, TransactionSetupID, ServicesID, ExpressResponseCode, ExpressResponseMessage, PaymentAccountID, ValidationCode, BillingAddress1, and Entry. In the event of a cancelled account creation, only the TransactionSetupID and HostedPaymentStatus are appended.

If you leave the ReturnURL blank or send it as null, the HostedPaymentURL will not redirect the user after the transaction has been processed or cancelled. Instead, the Hosted Payment Page will display the Result, Services ID, Payment Account ID, and Card Number (truncated).

The PaymentAccountedID generated using the HostedPaymentURL should not be used outside of Agility APIs. Doing so may cause NetworkTransactionIDs to fall out of sync.

Relationships

ContextId and Branch come from Login

Version Deployed
v555

**Request body:**
```json
{
    "request": {
        "SavedCreditCardCreateJSON": {
            "dsSavedCreditCardCreateRequest": {
                "dtSavedCreditCardCreateRequest": [
                    {
                        "CustomerID": "",
                        "ShiptoSequence": 1,
                        "ReturnURL": ""
                    }
                ]
            }
        }
    }
}
```

## SavedCreditCardDelete
`POST /AccountsReceivable/SavedCreditCardDelete`

Purpose
Deletes a saved credit card
Required Inputs

PaymentAccountID

Optional Inputs

N/A

Notes

Access to the Credit Card Interface must be granted to use this request.

Cards with pending payments cannot be deleted.

Only one card can be deleted at a time.

Data allocations do not apply.

Relationships

ContextId and Branch come from Login

Version Deployed
v555

**Request body:**
```json
{
    "request": {
        "SavedCreditCardDeleteJSON": {
            "dsPaymentAccountRequest": {
                "dtPaymentAccountRequest": [
                    {
                        "PaymentAccountID": ""
                    }
                ]
            }
        }
    }
}
```

## SavedCreditCardList
`POST /AccountsReceivable/SavedCreditCardList`

Purpose
Returns a list of saved credit cards for a specific customer ship-to or bill-to
Required Inputs

CustomerID

ShiptoSequence

Optional Inputs

N/A

Notes

To return credit cards stored on customer bill-to records, specify a ship-to sequence associated with the desired bill-to record.

Only active ship-to records return credit card lists.

User must have data allocations granted for the customer specified.

SurchargeAmount is based on the surcharge specified on the payment method as well as any surcharge discounts specified at the bill-to or ship-to level.

Relationships

ContextId and Branch come from Login

Version Deployed
v555

**Request body:**
```json
{
    "request": {
        "CustomerJSON": {
            "dsCustomerShipto": {
                "dtCustomerShipto": [
                    {
                        "CustomerID": "",
                        "ShiptoSequence": 1
                    }
                ]
            }
        }
    }
}
```

---

# Customer Service  (27 methods)

## CustomerBank
`POST /Customer/CustomerBank`

Purpose
Creates or updates sold-to customer bank information
Required Inputs

CustomerID

AccountNumber

RoutingNumber

BankJSON

Optional Inputs

N/A

Notes

The sold-to customer must exist

Any fields not include in the BankJSON assume the default values of the new or existing customer bank information record

DMSi strongly recommends reviewing dsAuditResults regardless of the ReturnCode value

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v534

**Request body:**
```json
{
    "request": {
        "CustomerID": "",
        "AccountNumber": "",
        "RoutingNumber": "",
        "BankJSON": {
            "dsCustomerBank": {
                "dtCustomerBank": [
                    {
                        "BankName": "",
                        "BankAccountName": "",
                        "AccountType": "",
                        "DefaultBranch": "",
                        "UseForACHProcessing": false,
                        "ApprovedForACHProcessing": false,
                        "DefaultACHAcctForCashApp": false
                    }
                ]
            }
        }
    }
}
```

## CustomerBilltoBank
`POST /Customer/CustomerBilltoBank`

Purpose
Creates or updates bill-to customer bank information
Required Inputs

CustomerID

BilltoSequence

AccountNumber

RoutingNumber

BankJSON

Optional Inputs

N/A

Notes

The sold-to and bill-to customers must exist

Any fields not include in the BankJSON assume the default values of the new or existing customer bill-to bank information record

DMSi strongly recommends reviewing dsAuditResults regardless of the ReturnCode value

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v534

**Request body:**
```json
{
    "request": {
        "CustomerID": "",
        "BilltoSequence": 1,
        "AccountNumber": "",
        "RoutingNumber": "",
        "BankJSON": {
            "dsCustomerBilltoBank": {
                "dtCustomerBilltoBank": [
                    {
                        "BankName": "",
                        "BankAccountName": "",
                        "AccountType": "",
                        "DefaultBranch": "",
                        "UseForACHProcessing": true,
                        "ApprovedForACHProcessing": false,
                        "DefaultACHAcctForCashApp": false
                    }
                ]
            }
        }
    }
}
```

## CustomerBilltoContact
`POST /Customer/CustomerBilltoContact`

Purpose
Creates or updates bill-to customer contact
Required Inputs

CustomerID

BilltoSequence

ContactName

ContactType,

ContactJSON

Optional Inputs

N/A

Notes

The sold-to and bill-to customers must exist

Any fields not included in the ContactJSON assume the default values of the new or existing customer bill-to contact record

DMSi strongly recommends reviewing dsAuditResults regardless of the ReturnCode value

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v534

**Request body:**
```json
{
    "request": {
        "CustomerID": "",
        "BilltoSequence": 1,
        "ContactName": "",
        "ContactType": "",
        "ContactJSON": {
            "dsCustomerBilltoContact": {
                "dtCustomerBilltoContact": [
                    {
                        "Primary": true,
                        "Address1": "",
                        "Address2": "",
                        "Address3": "",
                        "City": "",
                        "State": "",
                        "ZIP": "",
                        "Country": "",
                        "Phone1": "",
                        "Phone2": "",
                        "OtherPhone": "",
                        "MobilePhone": "",
                        "Fax": "",
                        "EmailAddress": "",
                        "NotifyShipmentEnRoute": true,
                        "NotifyShipmentDelivered": false,
                        "NotifyShipmentRefused": false,
                        "ContactTitle": "",
                        "Salutation": "",
                        "OtherData": "",
                        "Remarks": ""
                    }
                ]
            }
        }
    }
}
```

## CustomerBilltoCreate
`POST /Customer/CustomerBilltoCreate`

Purpose
Creates a bill-to customer
Required Inputs

CustomerID

BilltoJSON

Optional Inputs

N/A

Notes

The sold-to customer must exist before creating a bill-to customer

Any fields not included in the BilltoJSON assume the default values of a new customer bill-to

DMSi strongly recommends reviewing dsAuditResults regardless of the ReturnCode value

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v534

**Request body:**
```json
{
    "request": {
        "CustomerID": "",
        "BilltoJSON": {
            "dsCustomerBillto": {
                "dtCustomerBillto": [
                    {
                        "Name": "",
                        "Address1": "",
                        "Address2": "",
                        "Address3": "",
                        "City": "",
                        "State": "",
                        "ZIP": "",
                        "Country": "",
                        "PhoneFormat": "",
                        "Fax": "",
                        "Phone": "",
                        "MobilePhone": "",
                        "Email": "",
                        "UseBilltoInvNumFormat": true,
                        "UseBranchPrefix": "",
                        "UseHyphenBeforeShipmentID": "",
                        "NumCharactersForTranID": 1,
                        "NumCharactersForShipmentID": 1,
                        "CrossRefRequired": "",
                        "CrossRefRequiredSpecialOrders": "",
                        "DefaultStandardPriceLevel": 0,
                        "DiscountGraceDays": 0,
                        "ApplyCCSurchargeFee": "",
                        "CCSurchargeDiscountPercent": 0,
                        "IncludeInAutoCash": false,
                        "FinanceCharge": "",
                        "EDIMailbox": "",
                        "EDIOrgIDDigits": "",
                        "EDIAlternateCashAccount": "",
                        "EDIAlternateCashGLComponent": "",
                        "EDIPaymentRules": 0,
                        "AutoApplyARRemitLockboxPayments": true,
                        "AcceptDupInvARRemit": "",
                        "AcceptDupInvLockboxPayments": "",
                        "CreateAdjInvForVariancePayDetail": "",
                        "SalesAgentForAdjInv": "",
                        "BranchForAdjInv": "",
                        "RemittoDivision": "",
                        "CustomInvoiceProcessing": "",
                        "AppliesToShiptoInvoices": true,
                        "InvoiceEmailGroupBy": "",
                        "PrintInvoiceCopyForBillto": "",
                        "BilltoInvoicePhone": "",
                        "BilltoInvoiceFax": "",
                        "PrintInvoiceCopyForShipto": "",
                        "ShiptoInvoicePhone": "",
                        "ShiptoInvoiceFax": "",
                        "UseBilltoStatementSettings": "",
                        "StatementType": "",
                        "CycleCode": "",
                        "StatementPrintSummaryOnly": true,
                        "StatementPrintDiscDate": "",
                        "StatementPrintDiscAmt": "",
                        "StatementPrintDueDate": "",
                        "StatementPrintInvoices": true,
                        "ReferenceNum": "",
                        "FederalTaxNum": "",
                        "StateTaxNum": "",
                        "MunicipalTaxNum": "",
                        "MinimumFinanceCharge": 0,
                        "FinanceChargeThreshold": 0,
                        "IncludeFinanceChargeInvoices": true,
                        "CheckCredit": "",
                        "DontCheckCreditThru": "2028-12-31",
                        "CreditBypassAmt": 0,
                        "CreditLimitAmt": 0,
                        "OverdueAmt": 0,
                        "OverduePercentage": 0,
                        "OverdueDays": 0,
                        "CreditLimitExpDate": "2028-11-30",
                        "CreditScore": 0,
                        "CreditRating": "",
                        "CreditReviewDate": "2028-01-15",
                        "BureauNum1Rating": "",
                        "BureauNum1EffectiveDate": "2028-02-01",
                        "BureauNum2Rating": "",
                        "BureauNum2EffectiveDate": "2028-05-23",
                        "MiscField1": "",
                        "MiscField2": "",
                        "MiscField3": "",
                        "MiscField4": "",
                        "MiscField5": "",
                        "MiscField6": "",
                        "MiscField7": "",
                        "MiscField8": "",
                        "MiscField9": "",
                        "MiscField10": "",
                        "MiscField11": "",
                        "MiscField12": "",
                        "AccountType": ""
                    }
                ]
            }
        }
    }
}
```

## CustomerBilltoLaserControls
`POST /Customer/CustomerBilltoLaserControls`

Purpose
Creates or updates bill-to customer laser controls
Required Inputs

CustomerID

BilltoSequence

FormType

PrinterSequence

LaserControlJSON

Optional Inputs

N/A

Notes

The sold-to and bill-to customers must exist

Any fields not included in the LaserControlJSON assume the default values of the new or existing customer bill-to laser control record

DMSi strongly recommends reviewing dsAuditResults regardless of the ReturnCode value

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v534

**Request body:**
```json
{
    "request": {
        "CustomerID": "",
        "BilltoSequence": 1,
        "FormType": "",
        "PrinterSequence": 1,
        "LaserControlJSON": {
            "dsCustomerBilltoLaserControls": {
                "dtCustomerBilltoLaserControls": [
                    {
                        "PrinterName": "",
                        "FaxEmailToSource": "",
                        "Fax": "",
                        "Email": "",
                        "Copies": 0,
                        "FormFooter": ""
                    }
                ]
            }
        }
    }
}
```

## CustomerBilltosList
`POST /Customer/CustomerBilltosList`

Purpose
Returns a list of customer bill-tos available to the user and available in the current branch the user is logged into
Required Inputs

N/A

Optional Inputs

SearchBy

SearchValue

CustomerID

BilltoSequence

FetchOnlyChangedSince

ChunkStartPointer

RecordFetchLimit

Notes

This method allows a user to request customer bill-tos that have changed since a particular date and time.

This method allows a user to request a specific number of records. Please see the Chunking topic for more information.

Valid SearchBy values:

Bill-to Name

Bill-to Address 1

Bill-to Address 2

Bill-to City

Bill-to State

Bill-to ZIP

Bill-to phone

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Valid values for CustomerID come from CustomersList

Response fields CustomerCurrentBalance and CustomerHomeBranch are from the customer sold-to record

Version Deployed
v613

**Request body:**
```json
{
    "request": {
        "SearchBy": "",
        "SearchValue": "",
        "CustomerID": "",
        "BilltoSequence": 1,
        "AdditionalSearchCriteriaJSON": {
            "dsCustomerBilltoSearchRequest": {
                "dtCustomerBilltoSearchRequest": [
                    {
                        "FetchOnlyChangedSince": null,
                        "ChunkStartPointer": 0,
                        "RecordFetchLimit": 50
                    }
                ]
            }
        }
    }
}
```

## CustomerBilltoUpdate
`POST /Customer/CustomerBilltoUpdate`

Purpose
Updates a bill-to customer
Required Inputs

CustomerID

BilltoSequence

BilltoJSON

Optional Inputs

N/A

Notes

The bill-to customer must exist

Any fields not included in the BilltoJSON assume the default values of the existing customer bill-to record

DMSi strongly recommends reviewing dsAuditResults regardless of the ReturnCode value

During processing of the request, if the 'Release eligible orders upon credit criteria change' field is set to 'Prompt' on the Agility A/R Parameters record, and the new ReleaseOrdersUponCreditChange field is set to 'True', the system automatically rechecks credit and releases orders based on credit criteria changes received from the API request for the customer bill-to record.

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v534

**Request body:**
```json
{
    "request": {
        "CustomerID": "",
        "BilltoSequence": 1,
        "BilltoJSON": {
            "dsCustomerBillto": {
                "dtCustomerBillto": [
                    {
                        "Name": "",
                        "Address1": "",
                        "Address2": "",
                        "Address3": "",
                        "City": "",
                        "State": "",
                        "ZIP": "",
                        "Country": "",
                        "PhoneFormat": "",
                        "Fax": "",
                        "Phone": "",
                        "MobilePhone": "",
                        "Email": "",
                        "UseBilltoInvNumFormat": true,
                        "UseBranchPrefix": false,
                        "UseHyphenBeforeShipmentID": false,
                        "NumCharactersForTranID": 1,
                        "NumCharactersForShipmentID": 0,
                        "CrossRefRequired": "",
                        "CrossRefRequiredSpecialOrders": "",
                        "DefaultStandardPriceLevel": 0,
                        "DiscountGraceDays": 0,
                        "ApplyCCSurchargeFee": "",
                        "CCSurchargeDiscountPercent": 0,
                        "IncludeInAutoCash": true,
                        "FinanceCharge": false,
                        "EDIMailbox": "",
                        "EDIOrgIDDigits": "",
                        "EDIAlternateCashAccount": "",
                        "EDIAlternateCashGLComponent": 0,
                        "EDIPaymentRules": 0,
                        "AutoApplyARRemitLockboxPayments": false,
                        "AcceptDupInvARRemit": false,
                        "AcceptDupInvLockboxPayments": false,
                        "CreateAdjInvForVariancePayDetail": false,
                        "SalesAgentForAdjInv": "",
                        "BranchForAdjInv": "",
                        "RemittoDivision": "",
                        "CustomInvoiceProcessing": "",
                        "AppliesToShiptoInvoices": false,
                        "InvoiceEmailGroupBy": "",
                        "PrintInvoiceCopyForBillto": false,
                        "BilltoInvoicePhone": "",
                        "BilltoInvoiceFax": "",
                        "PrintInvoiceCopyForShipto": false,
                        "ShiptoInvoicePhone": "",
                        "ShiptoInvoiceFax": "",
                        "UseBilltoStatementSettings": false,
                        "StatementType": "",
                        "CycleCode": "",
                        "StatementPrintSummaryOnly": false,
                        "StatementPrintDiscDate": false,
                        "StatementPrintDiscAmt": false,
                        "StatementPrintDueDate": false,
                        "StatementPrintInvoices": false,
                        "ReferenceNum": "",
                        "FederalTaxNum": "",
                        "StateTaxNum": "",
                        "MunicipalTaxNum": "",
                        "MinimumFinanceCharge": 0.0,
                        "FinanceChargeThreshold": 0.0,
                        "IncludeFinanceChargeInvoices": false,
                        "CheckCredit": "",
                        "DontCheckCreditThru": "2018-05-23",
                        "CreditBypassAmt": 0.0,
                        "CreditLimitAmt": 0.0,
                        "OverdueAmt": 0.0,
                        "OverduePercentage": 0.0,
                        "OverdueDays": 0,
                        "CreditLimitExpDate": "2018-05-23",
                        "CreditScore": 0.0,
                        "CreditRating": "",
                        "CreditReviewDate": "2018-05-23",
                        "ReleaseOrdersUponCreditChange": false,
                        "BureauNum1Rating": "",
                        "BureauNum1EffectiveDate": "2018-05-23",
                        "BureauNum2Rating": "",
                        "BureauNum2EffectiveDate": "2018-05-23",
                        "MiscField1": "",
                        "MiscField2": "",
                        "MiscField3": "",
                        "MiscField4": "",
                        "MiscField5": "",
                        "MiscField6": "",
                        "MiscField7": "",
                        "MiscField8": "",
                        "MiscField9": "",
                        "MiscField10": "",
                        "MiscField11": "",
                        "MiscField12": "",
                        "AccountType": ""
                    }
                ]
            }
        }
    }
}
```

## CustomerBranchShiptoCreate
`POST /Customer/CustomerBranchShiptoCreate`

Purpose
Creates a branch ship-to customer
Required Inputs

CustomerID

ShiptoSequence

BranchShiptoJSON

Optional Inputs

N/A

Notes

The sold-to and ship-to customer must exist before creating a branch ship-to customer

The associated 'enable' flag must be included and set to 'true' to input a value on a branch ship-to record

Any fields not included in the BranchShiptoJSON assume the default values of a new customer branch ship-to record

DMSi strongly recommends reviewing dsAuditResults regardless of the ReturnCode value

PriceGroupsAction has one valid value during a record create. The ‘Add’ action assigns values from PriceGroups to the newly created branch ship-to

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v534

**Request body:**
```json
{
    "request": {
        "CustomerID": "",
        "ShiptoSequence": 1,
        "BranchShiptoJSON": {
            "dsCustomerBranchShipto": {
                "dtCustomerBranchShipto": [
                    {
                        "UseBranchLaserControls": false,
                        "EnableDefaultFlags": false,
                        "Active": true,
                        "Prospect": false,
                        "ShipComplete": false,
                        "WMSShipComplete": false,
                        "AcceptsBO": false,
                        "Nonsalable": false,
                        "PricedPickDelv": false,
                        "OverridePickDelvSortOrder": false,
                        "ApplyPromoPricesDisc": false,
                        "DisplayPiecePrice": false,
                        "RepriceOrderAtShipment": false,
                        "RequireOrderAcknowledgment": false,
                        "TrackLinkedReceiptsOrderAck": false,
                        "AcceptsNightDeliveries": true,
                        "DisplayPaymentsOnSOSave": false,
                        "FullPaymentRequired": false,
                        "FullPaymentReqPartialShipment": false,
                        "FullPaymentRequiredOrderTypes": "",
                        "AllowOverpaymentsInvoicing": false,
                        "ApplyOverpaymentType": "",
                        "DefaultShipmentStatus": "",
                        "MinOrderHoldAmount": 0,
                        "MinOrderHoldForceShipComplete": false,
                        "EnableDefaultCodes": false,
                        "FreightTerms": "",
                        "ShipVia": "",
                        "SaleType": "",
                        "ECommerceSaleType": "",
                        "Zone": "",
                        "Priority": 0,
                        "EnableTaxes": false,
                        "Taxable": false,
                        "Taxcode": "",
                        "EnableSalesAgents": false,
                        "SalesAgent1": "",
                        "SalesAgent1PctOfOrder": 0.0,
                        "SalesAgent2": "",
                        "SalesAgent2PctOfOrder": 0.0,
                        "SalesAgent3": "",
                        "SalesAgent3PctOfOrder": 0.0,
                        "EnablePaymentTerms": false,
                        "PaymentTermsCode": "",
                        "CMPaymentTermsCode": "",
                        "EnableFieldRequirements": false,
                        "OrderedByRequired": false,
                        "AuthToChargeRequired": false,
                        "ShipViaRequired": false,
                        "ShipViaRequiredOrderTypes": "",
                        "EnableShippingTracking": false,
                        "ShippingTrackingInsuranceReq": false,
                        "ShippingTrackingSaturdayDelivery": false,
                        "ShippingTrackingSundayDelivery": false,
                        "ShippingTrackingDelvInstructions": "",
                        "UpdSalesAgentOpenSO": false,
                        "UpdSalesAgentOpenQuote": false,
                        "UpdSalesAgentOpenCM": false,
                        "UpdSalesAgentOpenPOSSO": false,
                        "UpdSalesAgentOpenPOSQuote": false,
                        "UpdSalesAgentOpenPOSCM": false,
                        "UpdSalesAgentOpenTranNotOverride": false,
                        "UpdPayTermOpenSO": false,
                        "UpdPayTermOpenQuote": false,
                        "UpdPayTermOpenCM": false,
                        "UpdPayTermOpenTranNotOverride": false,
                        "UpdMinOrderHoldAmtOpenSO": false,
                        "SetNonSalableWithOpen": false
                    }
                ]
            }
        }
    }
}
```

## CustomerBranchShiptoList
`POST /Customer/CustomerBranchShiptoList`

Purpose
Gets customer branch ship-to information
Required Inputs

CustomerID

ShiptoSequence

Optional Inputs

N/A

Notes
N/A
Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v539

**Request body:**
```json
{
    "request": {
        "CustomerID": "",
        "ShiptoSequence": 1
    }
}
```

## CustomerBranchShiptoLaserControls
`POST /Customer/CustomerBranchShiptoLaserControls`

Purpose
Creates or updates branch ship-to customer laser controls
Required Inputs

CustomerID

ShiptoSequence

FormType

PrinterSequence

LaserControlJSON

Optional Inputs

N/A

Notes

The sold-to and ship-to customers must exist

Any fields not included in the LaserControlJSON assume the default values of the new or existing customer branch ship-to laser control record

DMSi strongly recommends reviewing dsAuditResults regardless of the ReturnCode value

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v534

**Request body:**
```json
{
    "request": {
        "CustomerID": "",
        "ShiptoSequence": 1,
        "FormType": "",
        "PrinterSequence": 1,
        "LaserControlJSON": {
            "dsCustBranchShiptoLaserControls": {
                "dtCustBranchShiptoLaserControls": [
                    {
                        "PrinterName": "",
                        "FaxEmailToSource": "",
                        "Fax": "",
                        "Email": "",
                        "Copies": 0,
                        "FormFooter": ""
                    }
                ]
            }
        }
    }
}
```

## CustomerBranchShiptoUpdate
`POST /Customer/CustomerBranchShiptoUpdate`

Purpose
Updates a branch ship-to customer
Required Inputs

CustomerID

ShiptoSequence

BranchShiptoJSON

Optional Inputs

N/A

Notes

The branch ship-to record must exist

The associated 'enable' flag must be included and set to 'true' to update a field on a branch ship-to record

Any fields not included in the BranchShiptoJSON assume the default values of the existing customer branch ship-to record

DMSi strongly recommends reviewing dsAuditResults regardless of the ReturnCode value

PriceGroupsAction has four valid values:

Add – Adds values from PriceGroups to the end of the existing price groups in rank order

Replace – Replaces all current price groups with the values from PriceGroups. If there are no values in PriceGroups, a warning is given and the price groups are not updated.

Delete – Deletes price groups specified in PriceGroups

Delete all – Deletes all current price groups.

This method includes actions that are performed after the record is updated.

When an action updates transaction(s), the field(s) being updated on the transaction must match the original value on the customer record to perform the update.

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v534

**Request body:**
```json
{
    "request": {
        "CustomerID": "",
        "ShiptoSequence": 1,
        "BranchShiptoJSON": {
            "dsCustomerBranchShipto": {
                "dtCustomerBranchShipto": [
                    {
                        "UseBranchLaserControls": false,
                        "EnableDefaultFlags": false,
                        "Active": false,
                        "Prospect": false,
                        "ShipComplete": false,
                        "WMSShipComplete": false,
                        "AcceptsBO": false,
                        "Nonsalable": false,
                        "PricedPickDelv": false,
                        "OverridePickDelvSortOrder": false,
                        "ApplyPromoPricesDisc": false,
                        "DisplayPiecePrice": false,
                        "RepriceOrderAtShipment": false,
                        "RequireOrderAcknowledgment": false,
                        "TrackLinkedReceiptsOrderAck": false,
                        "AcceptsNightDeliveries": false,
                        "DisplayPaymentsOnSOSave": false,
                        "FullPaymentRequired": false,
                        "FullPaymentReqPartialShipment": false,
                        "FullPaymentRequiredOrderTypes": "",
                        "AllowOverpaymentsInvoicing": false,
                        "ApplyOverpaymentType": "",
                        "DefaultShipmentStatus": "",
                        "MinOrderHoldAmount": 0,
                        "MinOrderHoldForceShipComplete": false,
                        "EnableDefaultCodes": false,
                        "PriceGroupsAction": "",
                        "PriceGroups": "",
                        "FreightTerms": "",
                        "ShipVia": "",
                        "SaleType": "",
                        "ECommerceSaleType": "",
                        "Zone": "",
                        "Priority": 0,
                        "EnableTaxes": false,
                        "Taxable": false,
                        "Taxcode": "",
                        "EnableSalesAgents": false,
                        "SalesAgent1": "",
                        "SalesAgent1PctOfOrder": 0.0,
                        "SalesAgent2": "",
                        "SalesAgent2PctOfOrder": 0.0,
                        "SalesAgent3": "",
                        "SalesAgent3PctOfOrder": 0.0,
                        "EnablePaymentTerms": false,
                        "PaymentTermsCode": "",
                        "CMPaymentTermsCode": "",
                        "EnableFieldRequirements": false,
                        "OrderedByRequired": false,
                        "AuthToChargeRequired": false,
                        "ShipViaRequired": false,
                        "ShipViaRequiredOrderTypes": "",
                        "EnableShippingTracking": false,
                        "ShippingTrackingInsuranceReq": false,
                        "ShippingTrackingSaturdayDelivery": false,
                        "ShippingTrackingSundayDelivery": false,
                        "ShippingTrackingDelvInstructions": "",
                        "UpdSalesAgentOpenSO": false,
                        "UpdSalesAgentOpenQuote": false,
                        "UpdSalesAgentOpenCM": false,
                        "UpdSalesAgentOpenPOSSO": false,
                        "UpdSalesAgentOpenPOSQuote": false,
                        "UpdSalesAgentOpenPOSCM": false,
                        "UpdSalesAgentOpenTranNotOverride": false,
                        "UpdPayTermOpenSO": false,
                        "UpdPayTermOpenQuote": false,
                        "UpdPayTermOpenCM": false,
                        "UpdPayTermOpenTranNotOverride": false,
                        "UpdMinOrderHoldAmtOpenSO": false,
                        "SetNonSalableWithOpen": false
                    }
                ]
            }
        }
    }
}
```

## CustomerContact
`POST /Customer/CustomerContact`

Purpose
Creates or updates a sold-to customer contact
Required Inputs

CustomerID

ContactName

ContactType

ContactJSON

Optional Inputs

N/A

Notes

The sold-to customer must exist

Any fields not included in the ContactJSON assume the default values of the new or existing customer contact record

DMSi strongly recommends reviewing dsAuditResults regardless of the ReturnCode value

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v534

**Request body:**
```json
{
    "request": {
        "CustomerID": "",
        "ContactName": "",
        "ContactType": "",
        "ContactJSON": {
            "dsCustomerContact": {
                "dtCustomerContact": [
                    {
                        "Primary": false,
                        "Address1": "",
                        "Address2": "",
                        "Address3": "",
                        "City": "",
                        "State": "",
                        "ZIP": "",
                        "Country": "",
                        "Phone1": "",
                        "Phone2": "",
                        "OtherPhone": "",
                        "MobilePhone": "",
                        "Fax": "",
                        "EmailAddress": "",
                        "NotifyShipmentEnRoute": false,
                        "NotifyShipmentDelivered": false,
                        "NotifyShipmentRefused": false,
                        "ContactTitle": "",
                        "Salutation": "",
                        "OtherData": "",
                        "Remarks": ""
                    }
                ]
            }
        }
    }
}
```

## CustomerCreate
`POST /Customer/CustomerCreate`

Purpose
Creates a sold-to customer
Required Inputs

CustomerID

CustomerJSON

Optional Inputs

N/A

Notes

Creating a customer also creates default ship-to and bill-to records with a sequence of 1.

When the ‘Auto assign customer ID’ option in Branch Controls is set, the CustomerID field is not a required input. If the CustomerID input is not populated, the next available sequence number is used.

There are required fields on the ship-to and bill-to records that need to be updated before this customer can be used to create any transaction. Sales agent 1 and Payment terms must be updated on the ship-to record. Sales Agent for adj invoice must be updated on the bill-to record.

Any fields not included in the CustomerJSON assume the default values of a new customer

DMSi strongly recommends reviewing dsAuditResults regardless of the ReturnCode value

SecondaryGroupAction has four valid values:

Add – Adds values from SecondaryGroups to the end of the existing secondary customer groups in rank order

Replace – Replaces all current secondary customer groups with the values from SecondaryGroups. If there are no values in SecondaryGroups, all existing secondary customer groups are removed.

Delete – Deletes secondary customer groups specified in SecondaryGroups (not applicable for CustomerCreate).

Delete all – Deletes all current secondary customer groups (not applicable for CustomerCreate).

Added secondary groups are assigned a ranking automatically in the order in which they are listed (Ex. “Sec group 1, Sec group 2”)

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v534

**Request body:**
```json
{
    "request": {
        "CustomerID": "",
        "CustomerJSON": {
            "dsCustomer": {
                "dtCustomer": [
                    {
                        "Name": "",
                        "DivisionID": "",
                        "GroupID": "",
                        "Address1": "",
                        "Address2": "",
                        "Address3": "",
                        "City": "",
                        "State": "",
                        "ZIP": "",
                        "Country": "",
                        "PhoneFormat": "",
                        "Fax": "",
                        "Phone": "",
                        "MobilePhone": "",
                        "Email": "",
                        "Website": "",
                        "DefaultCurrency": "",
                        "PrintCurrency": "",
                        "FormPrefix": "",
                        "FirstInvoiceDate": "",
                        "StartDate": "",
                        "FirstOrderDate": "",
                        "LastInvoiceDate": "",
                        "Active": true,
                        "FinanceCharge": false,
                        "Nonsaleable": false,
                        "Prospect": false,
                        "CopyPriceGroupsFromShiptoSeq": 0,
                        "CreditCardStorageOption": "",
                        "CheckSoldtoCredit": false,
                        "CheckBilltoCredit": false,
                        "CheckShiptoCredit": false,
                        "PrintSoldtoStatement": false,
                        "PrintBilltoStatement": false,
                        "PrintShiptoStatement": false,
                        "StatementType": "",
                        "CycleCode": "",
                        "StatementPrintSummaryOnly": false,
                        "StatementPrintDiscDate": false,
                        "StatementPrintDiscAmt": false,
                        "StatementPrintDueDate": false,
                        "StatementPrintInvoices": false,
                        "TargetCustomer": false,
                        "RequireInvoice": false,
                        "RequireOrderAcknowledgment": false,
                        "ReferenceNum": "",
                        "ParentCustomerID": "",
                        "FederalTaxNum": "",
                        "StateTaxNum": "",
                        "MunicipalTaxNum": "",
                        "CertificateAppliesTo": "",
                        "AllowCashPayments": false,
                        "AllowCheckPayments": false,
                        "AllowCreditCardPayments": false,
                        "DisplayPriceOnCCDevice": "",
                        "CheckCredit": "",
                        "DontCheckCreditThru": "",
                        "CreditBypassAmt": 0.0,
                        "CreditLimitAmt": 0.0,
                        "OverdueAmt": 0.0,
                        "OverduePercentage": 0.0,
                        "OverdueDays": 0,
                        "DUNNNumber": "",
                        "CreditManager": "",
                        "CreditLimitExpDate": "",
                        "CreditScore": 0.0,
                        "CreditRating": "",
                        "CreditReviewDate": "",
                        "BureauNum1Rating": "",
                        "BureauNum1EffectiveDate": "",
                        "BureauNum2Rating": "",
                        "BureauNum2EffectiveDate": "",
                        "LastReviewDate": "",
                        "LastApplicationDate": "",
                        "TradeClass": "",
                        "Class": "",
                        "ConsigneeCode": "",
                        "IndustryCode": "",
                        "MiscField1": "",
                        "MiscField2": "",
                        "MiscField3": "",
                        "MiscField4": "",
                        "MiscField5": "",
                        "MiscField6": "",
                        "MiscField7": "",
                        "MiscField8": "",
                        "MiscField9": "",
                        "MiscField10": "",
                        "MiscField11": "",
                        "MiscField12": "",
                        "UpdShiptoActiveWhenSetActive": false,
                        "UpdShiptoProspectWhenSetProspect": false,
                        "SetShipToBillToAddresses": "",
                        "UpdAddressOnNonOverriddenTrans": "",
                        "UpdAddressOnOverriddenTrans": false,
                        "SecondaryGroupsAction": "",
                        "SecondaryGroups": "",
                        "HomeBranch": "",
                        "AccountType": "",
                        "IRS8300POS": false
                    }
                ]
            }
        }
    }
}
```

## CustomerCustomFormAssignment
`POST /Customer/CustomerCustomFormAssignment`

Purpose
Creates or updates sold-to custom form settings
Required Inputs

CustomerID

StandardFormName

FormName

Optional Inputs

FormCode

Notes

Valid values for StandardFormName include the following:

Account Statement

Delivery Ticket

Finance Charge Invoice

Invoice

Order Acknowledgment

Payment Receipt

Pick Report

Pick Ticket

Quotation

RMA

Valid values for FormName and FormCode come from Custom Form Name Maintenance

Relationships

ContextId and Branch come from Login

Version Deployed
v619

**Request body:**
```json
{
    "request": {
        "CustomerID": "",
        "StandardFormName": "",
        "CustomFormAssignmentJSON": {
            "dsCustomFormAssignment": {
                "dtCustomFormAssignment": [
                    {
                        "FormName": "",
                        "FormCode": ""
                    }
                ]
            }
        }
    }
}
```

## CustomerLaserControls
`POST /Customer/CustomerLaserControls`

Purpose
Creates or updates sold-to laser controls
Required Inputs

CustomerID

FormType

PrinterSequence

LaserControlJSON

Optional Inputs

N/A

Notes

The sold-to customer must exist

Any fields not included in the LaserControlJSON assume the default values of the new or existing customer laser control record

DMSi strongly recommends reviewing dsAuditResults regardless of the ReturnCode value

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v534

**Request body:**
```json
{
    "request": {
        "CustomerID": "",
        "FormType": "",
        "PrinterSequence": 1,
        "LaserControlJSON": {
            "dsCustomerLaserControls": {
                "dtCustomerLaserControls": [
                    {
                        "PrinterName": "",
                        "FaxEmailToSource": "",
                        "Fax": "",
                        "Email": "",
                        "Copies": 0,
                        "FormFooter": ""
                    }
                ]
            }
        }
    }
}
```

## CustomerShiptoBank
`POST /Customer/CustomerShiptoBank`

Purpose
Creates or updates ship-to customer bank information
Required Inputs

CustomerID

ShiptoSequence

AccountNumber

RoutingNumber

BankJSON

Optional Inputs

N/A

Notes

The sold-to and ship-to customers must exist

Any fields not include in the BankJSON assume the default values of the new or existing customer ship-to bank information record

DMSi strongly recommends reviewing dsAuditResults regardless of the ReturnCode value

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v534

**Request body:**
```json
{
    "request": {
        "CustomerID": "",
        "ShiptoSequence": 1,
        "AccountNumber": "",
        "RoutingNumber": "",
        "BankJSON": {
            "dsCustomerShiptoBank": {
                "dtCustomerShiptoBank": [
                    {
                        "BankName": "",
                        "BankAccountName": "",
                        "AccountType": "",
                        "DefaultBranch": "",
                        "UseForACHProcessing": true,
                        "ApprovedForACHProcessing": false,
                        "DefaultACHAcctForCashApp": false
                    }
                ]
            }
        }
    }
}
```

## CustomerShiptoContact
`POST /Customer/CustomerShiptoContact`

Purpose
Creates or updates ship-to customer contacts
Required Inputs

CustomerID

ShiptoSequence

ContactName

ContactType

ContactJSON

Optional Inputs

N/A

Notes

The sold-to and ship-to customers must exist

Any fields not included in the ContactJSON assume the default values of the new or existing customer ship-to contact record

DMSi strongly recommends reviewing dsAuditResults regardless of the ReturnCode value

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v534

**Request body:**
```json
{
    "request": {
        "CustomerID": "",
        "ShiptoSequence": 1,
        "ContactName": "",
        "ContactType": "",
        "ContactJSON": {
            "dsCustomerShiptoContact": {
                "dtCustomerShiptoContact": [
                    {
                        "Primary": true,
                        "Address1": "",
                        "Address2": "",
                        "Address3": "",
                        "City": "",
                        "State": "",
                        "ZIP": "",
                        "Country": "",
                        "Phone1": "",
                        "Phone2": "",
                        "OtherPhone": "",
                        "MobilePhone": "",
                        "PrimaryMobileContact": false,
                        "Fax": "",
                        "EmailAddress": "",
                        "NotifyShipmentEnRoute": false,
                        "NotifyShipmentDelivered": true,
                        "NotifyShipmentRefused": true,
                        "ContactTitle": "",
                        "Salutation": "",
                        "OtherData": "",
                        "IncludeInfoInFormsSrcData": false,
                        "Remarks": ""
                    }
                ]
            }
        }
    }
}
```

## CustomerShiptoContactDelete
`POST /Customer/CustomerShiptoContactDelete`

Purpose
Deletes a customer ship-to contact record
Required Inputs

CustomerID

ShiptoSequence

ContactName

ContactType

ContactJSON

Optional Inputs

N/A

Notes

Only one contact can be deleted per request

You can leave the ContactType value empty if the ship-to Contact Maintenance window in Agility does not contain a value for ths field

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v553

**Request body:**
```json
{
    "request": {
        "CustomerID": "",
        "ShiptoSequence": 1,
        "ContactName": "",
        "ContactType": ""
    }
}
```

## CustomerShiptoCreate
`POST /Customer/CustomerShiptoCreate`

Purpose
Creates a ship-to customer
Required Inputs

CustomerID

ShiptoJSON

Optional Inputs

N/A

Notes

The sold-to customer must exist before creating a ship-to customer

Any fields not included in the ShiptoJSON assume the default values of a new customer ship-to

DMSi strongly recommends reviewing dsAuditResults regardless of the ReturnCode value

PriceGroupsAction has one valid value during a record create. The ‘Add’ action assigns values from PriceGroups to the newly created ship-to

If ActivateBasedOnHBOrgHierLevel is set to true and HomeBranchOrgHierLevel is not included in the request then the default value from Branch Parameters will be used

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v534

**Request body:**
```json
{
    "request": {
        "CustomerID": "",
        "ShiptoJSON": {
            "dsCustomerShipto": {
                "dtCustomerShipto": [
                    {
                        "ActiveInAllBranches": false,
                        "Name": "",
                        "Address1": "",
                        "Address2": "",
                        "Address3": "",
                        "City": "",
                        "State": "",
                        "ZIP": "",
                        "Country": "",
                        "PhoneFormat": "",
                        "Fax": "",
                        "Phone": "",
                        "MobilePhone": "",
                        "EmergencyPhone": "",
                        "Email": "",
                        "County": "",
                        "BilltoSequence": 0,
                        "AllowAsTemplate": false,
                        "UserDefinedKeywords": "",
                        "Active": false,
                        "Prospect": false,
                        "ShipComplete": false,
                        "ShipCompleteWMS": false,
                        "AcceptsBackorders": false,
                        "Nonsaleable": false,
                        "FinanceCharge": false,
                        "OverridePickDelvSortOrder": false,
                        "ApplyPromoPriceDiscount": false,
                        "DisplayPiecePrice": false,
                        "RepriceOrderAtShipment": false,
                        "DefaultShipmentOnHoldInvoicing": false,
                        "RequireOrderAcknowledgment": false,
                        "TrackLinkedReceiptsOrderAck": false,
                        "AcceptsNightDeliveries": false,
                        "DisplayPaymentsOnSOSave": false,
                        "FullPaymentRequired": false,
                        "FullPaymentReqPartialShipment": false,
                        "FullPaymentRequiredOrderTypes": "",
                        "AllowOverpaymentsInvoicing": false,
                        "ApplyOverpaymentType": "",
                        "AllowCreditBalanceAsPayment": false,
                        "ApplyCCSurchargeFee": "",
                        "CCSurchargeDiscountPercent": 0.0,
                        "DefaultShipmentStatus": "",
                        "OrderEntryBranchOption": "",
                        "BranchOptionDefaultBranch": "",
                        "BranchOptionPromptDefaultBranch": false,
                        "MinOrderHoldAmount": 0.0,
                        "MinOrderHoldForceShipComplete": false,
                        "AdditionalScheduleLeadDays": 0,
                        "ApplyWMSPickThreshold": false,
                        "WMSUnderPickThresholdPercent": 0.0,
                        "CallForAppointment": false,
                        "StartLoadHours": "06:30",
                        "EndLoadHours": "19:00",
                        "AllowAddonChargeCost": "",
                        "EDIOrgID": "",
                        "EDISOCreatedInBranch": "",
                        "EDISpecialOrdersCreatedInBranch": "",
                        "EDIItemActivityCreatedInBranch": "",
                        "ShippingTrackingInsuranceReq": false,
                        "ShippingTrackingSaturdayDelivery": false,
                        "ShippingTrackingSundayDelivery": false,
                        "ShippingTrackingDelvInstructions": "",
                        "LienRequired": false,
                        "LienDaysFromFirstShipment": 0,
                        "LienDaysFromLastShipment": 0,
                        "LienDaysFromLastInvoice": 0,
                        "LienShipmentAmtGreaterThan": 0.0,
                        "LienStatus": "",
                        "LienDateOption": "",
                        "LienDaysToFile": 0,
                        "LienMinAmountToFile": 0.0,
                        "FreightTerms": "",
                        "ShipVia": "",
                        "SaleType": "",
                        "ECommerceSaleType": "",
                        "Zone": "",
                        "Priority": 0,
                        "PriceGroupsAction": "",
                        "PriceGroups": "",
                        "Taxable": false,
                        "TaxCode": "",
                        "SetTaxCategoryOrderEntryOnly": false,
                        "TaxCategory": "",
                        "SalesAgent1": "",
                        "SalesAgent1PctOfOrder": 0.0,
                        "SalesAgent2": "",
                        "SalesAgent2PctOfOrder": 0.0,
                        "SalesAgent3": "",
                        "SalesAgent3PctOfOrder": 0.0,
                        "PaymentTermsCode": "",
                        "CMPaymentTermsCode": "",
                        "ApplyPayTermsFromPayMethod": false,
                        "OrderedByRequired": false,
                        "AuthToChargeRequired": false,
                        "ShipViaRequired": false,
                        "ShipViaRequiredOrderTypes": "",
                        "PORequired": false,
                        "PORequiredOrderTypes": "",
                        "POCheckDuplicatesBy": "",
                        "POCheckDuplicatesNumMonths": 0,
                        "PORule": "",
                        "POBlanketValue": "",
                        "POValidationCode": "",
                        "JobNumberRequired": false,
                        "JobNumberRequiredOrderTypes": "",
                        "JobNumberRule": "",
                        "JobNumberBlanketValue": "",
                        "JobValidationCode": "",
                        "ReferenceRequired": false,
                        "ReferenceRequiredOrderTypes": "",
                        "ReferenceValidationCode": "",
                        "PickDelvPricedTicket": false,
                        "PickPrintDetailPrices": false,
                        "PickPrintPriceAsNet": false,
                        "PickPrintExtendedPrice": false,
                        "PickPrintDimExtendedPrice": false,
                        "DelvPrintDetailPrices": false,
                        "DelvPrintPriceAsNet": false,
                        "DelvPrintExtendedPrice": false,
                        "DelvPrintDimExtendedPrice": false,
                        "AdditionalCODBasis": "",
                        "CODAmount": 0.0,
                        "CODNotToExceedBasis": "",
                        "CODNotToExceedFixedAmount": 0.0,
                        "PrintBOMLabels": false,
                        "BOMLabelFormat": "",
                        "PrintStockLabels": false,
                        "StockLabelFormat": "",
                        "PrintNonStockLabels": false,
                        "NonstockLabelFormat": "",
                        "PrintOrderLabels": true,
                        "OrderLabelFormat": "",
                        "QuotePrintPriceAsNet": false,
                        "QuotePrintPriceOnly": false,
                        "QuotePrintExtendedPrice": false,
                        "QuotePrintDimExtendedPrice": false,
                        "OrderAckFormTitle": "",
                        "OrdAckPrintDetailPrices": false,
                        "OrdAckPrintPriceAsNet": false,
                        "OrdAckPrintExtendedPrice": false,
                        "OrdAckPrintDimExtendedPrice": false,
                        "OrdAckPrintTotals": false,
                        "OrdAckDispGroupOptions": false,
                        "OrdAckGroupDefault": "",
                        "ASNPrintDefault": "",
                        "ASNAutoSendWithWMS": false,
                        "ASNAutoSendWithEDIS856ASN": false,
                        "ASNShiptoStopPrintOptions": "",
                        "InvPrintDetailPrices": false,
                        "InvPrintPriceAsNet": false,
                        "InvPrintExtendedPrice": false,
                        "InvPrintDimExtendedPrice": false,
                        "InvPrintPayTerm": false,
                        "InvPrintADFAmount": false,
                        "InvDispGroupOptions": false,
                        "InvGroupDefault": "",
                        "StatementPrintDiscDate": false,
                        "StatementPrintDiscAmt": false,
                        "StatementPrintDueDate": false,
                        "StatementPrintInvoices": false,
                        "MiscField1": "",
                        "MiscField2": "",
                        "MiscField3": "",
                        "MiscField4": "",
                        "MiscField5": "",
                        "MiscField6": "",
                        "MiscField7": "",
                        "MiscField8": "",
                        "MiscField9": "",
                        "MiscField10": "",
                        "MiscField11": "",
                        "MiscField12": "",
                        "FederalTaxNum": "",
                        "StateTaxNum": "",
                        "MunicipalTaxNum": "",
                        "MinimumFinanceCharge": 0.0,
                        "FinanceChargeThreshold": 0.0,
                        "IncludeFinanceChargeInvoices": false,
                        "CheckCredit": "",
                        "DontCheckCreditThru": "2018-05-23",
                        "CreditBypassAmt": 0.0,
                        "CreditLimitAmt": 0.0,
                        "OverdueAmt": 0.0,
                        "OverduePercentage": 0.0,
                        "OverdueDays": 0,
                        "CreditLimitExpDate": "2018-05-23",
                        "CreditScore": 0.0,
                        "CreditRating": "",
                        "CreditReviewDate": "2018-05-23",
                        "BureauNum1Rating": "",
                        "BureauNum1EffectiveDate": "2018-05-23",
                        "BureauNum2Rating": "",
                        "BureauNum2EffectiveDate": "2018-05-23",
                        "UpdAddressOnNonOverriddenTrans": "",
                        "UpdAddressOnOverriddenTrans": false,
                        "UpdSalesAgentOpenSO": false,
                        "UpdSalesAgentOpenQuote": false,
                        "UpdSalesAgentOpenCM": false,
                        "UpdSalesAgentOpenPOSSO": false,
                        "UpdSalesAgentOpenPOSQuote": false,
                        "UpdSalesAgentOpenPOSCM": false,
                        "UpdSalesAgentOpenTranNotOverride": false,
                        "UpdPayTermOpenSO": false,
                        "UpdPayTermOpenQuote": false,
                        "UpdPayTermOpenCM": false,
                        "UpdPayTermOpenTranNotOverride": false,
                        "UpdMinOrderHoldAmtOpenSO": false,
                        "HomeBranch": "",
                        "SetNonSalableWithOpen": false,
                        "ReleaseOrdersUponCreditChange": false,
                        "ActivateBasedOnHBOrgHierLevel": false,
                        "HomeBranchOrgHierLevel": "",
                        "ActivateBasedOnHBDistance": false,
                        "AccountType": ""
                    }
                ]
            }
        }
    }
}
```

## CustomerShiptoLaserControls
`POST /Customer/CustomerShiptoLaserControls`

Purpose
Creates or updates ship-to customer laser controls
Required Inputs

CustomerID

ShiptoSequence

FormType

PrinterSequence

LaserControlJSON

Optional Inputs

N/A

Notes

The sold-to and ship-to customers must exist

Any fields not included in the LaserControlJSON assume the default values of the new or existing customer ship-to laser control record

DMSi strongly recommends reviewing dsAuditResults regardless of the ReturnCode value

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v534

**Request body:**
```json
{
    "request": {
        "CustomerID": "",
        "ShiptoSequence": 1,
        "FormType": "",
        "PrinterSequence": 1,
        "LaserControlJSON": {
            "dsCustomerShiptoLaserControls": {
                "dtCustomerShiptoLaserControls": [
                    {
                        "PrinterName": "",
                        "FaxEmailToSource": "",
                        "Fax": "",
                        "Email": "",
                        "Copies": 0,
                        "FormFooter": ""
                    }
                ]
            }
        }
    }
}
```

## CustomerShiptoRoutesList
`POST /Customer/CustomerShiptoRoutesList`

Purpose
Returns a list of routes associated with customer ship-to records
Required Inputs

N/A

Optional Inputs

CustomerID

ShiptoSequence

ChunkStartPointer

RecordFetchLimit

Notes
This method allows a user to request a specific number of records. Please see the Chunking topic for more information
Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Valid values for CustomerID come from CustomersList or CustomerShiptoList

Valid values for ShiptoSequence come from CustomerShiptoList

Version Deployed
v539

**Request body:**
```json
{
    "request": {
        "SearchBy": "",
        "SearchValue": "",
        "CustomerID": "",
        "ShiptoSequence": 1,
        "StartPointer": "",
        "RecordFetchLimit": ""
    }
}
```

## CustomerShiptoUpdate
`POST /Customer/CustomerShiptoUpdate`

Purpose
Updates a ship-to customer
Required Inputs

CustomerID

ShiptoSequence

ShiptoJSON

Optional Inputs

N/A

Notes

The ship-to customer must exist

Any fields not included in the ShiptoJSON assume the default values of the existing customer ship-to record

DMSi strongly recommends reviewing dsAuditResults regardless of the ReturnCode value

PriceGroupsAction has four valid values:

Add – Adds values from PriceGroups to the end of the existing price groups in rank order

Replace – Replaces all current price groups with the values from PriceGroups. If there are no values in PriceGroups, a warning is given and the price groups are not updated.

Delete – Deletes price groups specified in PriceGroups

Delete all – Deletes all current price groups.

This method includes actions that are performed after the record is updated. When an action updates transaction(s), the field(s) being updated on the transaction must match the original value on the customer record to perform the update.

UpdAddressOnNonOverriddenTrans – Update address for non-overridden transaction. Valid values: Open and invoiced, Open only, Do not update.

During processing of the request, if the 'Release eligible orders upon credit criteria change' field is set to 'Prompt' on the Agility A/R Parameters record and the new ReleaseOrdersUponCreditChange field is set to 'True', the system automatically rechecks credit and releases orders based on credit criteria changes received from the API request for the customer ship-to record.

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v534

**Request body:**
```json
{
    "request": {
        "CustomerID": "",
        "ShiptoSequence": 1,
        "ShiptoJSON": {
            "dsCustomerShipto": {
                "dtCustomerShipto": [
                    {
                        "ActiveInAllBranches": false,
                        "Name": "",
                        "Address1": "",
                        "Address2": "",
                        "Address3": "",
                        "City": "",
                        "State": "",
                        "ZIP": "",
                        "Country": "",
                        "PhoneFormat": "",
                        "Fax": "",
                        "Phone": "",
                        "MobilePhone": "",
                        "EmergencyPhone": "",
                        "Email": "",
                        "County": "",
                        "BilltoSequence": "1",
                        "AllowAsTemplate": false,
                        "UserDefinedKeywords": "",
                        "Active": false,
                        "Prospect": false,
                        "ShipComplete": false,
                        "ShipCompleteWMS": false,
                        "AcceptsBackorders": false,
                        "Nonsaleable": false,
                        "FinanceCharge": false,
                        "OverridePickDelvSortOrder": false,
                        "ApplyPromoPriceDiscount": false,
                        "DisplayPiecePrice": false,
                        "RepriceOrderAtShipment": false,
                        "DefaultShipmentOnHoldInvoicing": false,
                        "RequireOrderAcknowledgment": false,
                        "TrackLinkedReceiptsOrderAck": false,
                        "AcceptsNightDeliveries": false,
                        "DisplayPaymentsOnSOSave": false,
                        "FullPaymentRequired": false,
                        "FullPaymentReqPartialShipment": false,
                        "FullPaymentRequiredOrderTypes": "",
                        "AllowOverpaymentsInvoicing": false,
                        "ApplyOverpaymentType": "",
                        "AllowCreditBalanceAsPayment": false,
                        "ApplyCCSurchargeFee": "",
                        "CCSurchargeDiscountPercent": 0.0,
                        "DefaultShipmentStatus": "",
                        "OrderEntryBranchOption": "",
                        "BranchOptionDefaultBranch": "",
                        "BranchOptionPromptDefaultBranch": false,
                        "MinOrderHoldAmount": null,
                        "MinOrderHoldForceShipComplete": false,
                        "ApplyWMSPickThreshold": false,
                        "WMSUnderPickThresholdPercent": 0.0,
                        "CallForAppointment": false,
                        "StartLoadHours": "",
                        "EndLoadHours": "",
                        "AllowAddonChargeCost": "",
                        "EDIOrgID": "",
                        "EDISOCreatedInBranch": "",
                        "EDIItemActivityCreatedInBranch": "",
                        "EDISpecialOrdersCreatedInBranch": "",
                        "ShippingTrackingInsuranceReq": false,
                        "ShippingTrackingSaturdayDelivery": false,
                        "ShippingTrackingSundayDelivery": false,
                        "ShippingTrackingDelvInstructions": "",
                        "LienRequired": false,
                        "LienDaysFromFirstShipment": 0,
                        "LienDaysFromLastShipment": 0,
                        "LienDaysFromLastInvoice": 0,
                        "LienShipmentAmtGreaterThan": 0.0,
                        "LienStatus": "",
                        "LienDateOption": "",
                        "LienDaysToFile": 0,
                        "LienMinAmountToFile": 0.0,
                        "PriceGroupsAction": "",
                        "PriceGroups": "",
                        "FreightTerms": "",
                        "ShipVia": "",
                        "SaleType": "",
                        "ECommerceSaleType": "",
                        "Zone": "",
                        "Priority": 0,
                        "Taxable": false,
                        "TaxCode": "",
                        "SetTaxCategoryOrderEntryOnly": false,
                        "TaxCategory": "",
                        "SalesAgent1": "",
                        "SalesAgent1PctOfOrder": 0.0,
                        "SalesAgent2": "",
                        "SalesAgent2PctOfOrder": 0.0,
                        "SalesAgent3": "",
                        "SalesAgent3PctOfOrder": 0.0,
                        "PaymentTermsCode": "",
                        "CMPaymentTermsCode": "",
                        "ApplyPayTermsFromPayMethod": false,
                        "OrderedByRequired": false,
                        "AuthToChargeRequired": false,
                        "ShipViaRequired": false,
                        "ShipViaRequiredOrderTypes": "",
                        "PORequired": false,
                        "PORequiredOrderTypes": "",
                        "POCheckDuplicatesBy": "",
                        "POCheckDuplicatesNumMonths": 0,
                        "PORule": "",
                        "POBlanketValue": "",
                        "POValidationCode": "",
                        "JobNumberRequired": false,
                        "JobNumberRequiredOrderTypes": "",
                        "JobNumberRule": "",
                        "JobNumberBlanketValue": "",
                        "JobValidationCode": "",
                        "ReferenceRequired": false,
                        "ReferenceRequiredOrderTypes": "",
                        "ReferenceValidationCode": "",
                        "PickDelvPricedTicket": false,
                        "PickPrintDetailPrices": false,
                        "PickPrintPriceAsNet": false,
                        "PickPrintExtendedPrice": false,
                        "PickPrintDimExtendedPrice": false,
                        "DelvPrintDetailPrices": false,
                        "DelvPrintPriceAsNet": false,
                        "DelvPrintExtendedPrice": false,
                        "DelvPrintDimExtendedPrice": false,
                        "AdditionalCODBasis": "",
                        "CODAmount": 0.0,
                        "CODNotToExceedBasis": "",
                        "CODNotToExceedFixedAmount": 0.0,
                        "PrintBOMLabels": false,
                        "BOMLabelFormat": "",
                        "PrintStockLabels": false,
                        "StockLabelFormat": "",
                        "PrintNonStockLabels": false,
                        "NonstockLabelFormat": "",
                        "PrintOrderLabels": true,
                        "OrderLabelFormat": "",
                        "QuotePrintPriceAsNet": false,
                        "QuotePrintPriceOnly": false,
                        "QuotePrintExtendedPrice": false,
                        "QuotePrintDimExtendedPrice": false,
                        "OrderAckFormTitle": "",
                        "OrdAckPrintDetailPrices": false,
                        "OrdAckPrintPriceAsNet": false,
                        "OrdAckPrintExtendedPrice": false,
                        "OrdAckPrintDimExtendedPrice": false,
                        "OrdAckPrintTotals": false,
                        "OrdAckDispGroupOptions": false,
                        "OrdAckGroupDefault": "",
                        "ASNPrintDefault": "",
                        "ASNAutoSendWithWMS": false,
                        "ASNAutoSendWithEDIS856ASN": false,
                        "ASNShiptoStopPrintOptions": "",
                        "InvPrintDetailPrices": false,
                        "InvPrintPriceAsNet": false,
                        "InvPrintExtendedPrice": false,
                        "InvPrintDimExtendedPrice": false,
                        "InvPrintPayTerm": false,
                        "InvPrintADFAmount": false,
                        "InvDispGroupOptions": false,
                        "InvGroupDefault": "",
                        "StatementPrintDiscDate": false,
                        "StatementPrintDiscAmt": false,
                        "StatementPrintDueDate": false,
                        "StatementPrintInvoices": false,
                        "MiscField1": "",
                        "MiscField2": "",
                        "MiscField3": "",
                        "MiscField4": "",
                        "MiscField5": "",
                        "MiscField6": "",
                        "MiscField7": "",
                        "MiscField8": "",
                        "MiscField9": "",
                        "MiscField10": "",
                        "MiscField11": "",
                        "MiscField12": "",
                        "FederalTaxNum": "",
                        "StateTaxNum": "",
                        "MunicipalTaxNum": "",
                        "MinimumFinanceCharge": 0.0,
                        "FinanceChargeThreshold": 0.0,
                        "IncludeFinanceChargeInvoices": false,
                        "CheckCredit": "",
                        "DontCheckCreditThru": "2023-08-15",
                        "CreditBypassAmt": 0.0,
                        "CreditLimitAmt": 0.0,
                        "OverdueAmt": 0.0,
                        "OverduePercentage": 0.0,
                        "OverdueDays": 0,
                        "CreditLimitExpDate": "2018-05-23",
                        "CreditScore": 0.0,
                        "CreditRating": "",
                        "CreditReviewDate": "2018-05-23",
                        "ReleaseOrdersUponCreditChange": false,
                        "BureauNum1Rating": "",
                        "BureauNum1EffectiveDate": "2018-05-23",
                        "BureauNum2Rating": "",
                        "BureauNum2EffectiveDate": "2018-05-23",
                        "UpdAddressOnNonOverriddenTrans": "",
                        "UpdAddressOnOverriddenTrans": false,
                        "UpdSalesAgentOpenSO": false,
                        "UpdSalesAgentOpenQuote": false,
                        "UpdSalesAgentOpenCM": false,
                        "UpdSalesAgentOpenPOSSO": false,
                        "UpdSalesAgentOpenPOSQuote": false,
                        "UpdSalesAgentOpenPOSCM": false,
                        "UpdSalesAgentOpenTranNotOverride": false,
                        "UpdPayTermOpenSO": false,
                        "UpdPayTermOpenQuote": false,
                        "UpdPayTermOpenCM": false,
                        "UpdPayTermOpenTranNotOverride": false,
                        "UpdMinOrderHoldAmtOpenSO": true,
                        "SetNonSalableWithOpen": false,
                        "HomeBranch": "",
                        "AccountType": ""
                    }
                ]
            }
        }
    }
}
```

## CustomerShiptosList
`POST /Customer/CustomerShiptosList`

Purpose
Returns a list of customer ship-tos available to the user and available in the current branch the user is logged into
Required Inputs

N/A

Optional Inputs

SearchBy

SearchValue

CustomerID

ShiptoSequence

BilltoSequence

FetchOnlyChangedSince

RecordFetchLimit

Notes

This method allows a user to request customer ship-tos that have changed since a particular date and time.

This method allows the user to search for specific customer ship-tos with limited criteria. Please see the Searchby topic for more information

This method allows a user to request a specific number of records. Please see the Chunking topic for more information

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Valid SearchBy values:

Ship-to Name

Ship-to Address 1

Ship-to Address 2

Ship-to City

Ship-to State

Ship-to ZIP

Ship-to Phone

Keyword

Valid values for CustomerID come from CustomersList

Valid values for ShiptoSequence come from CustomerShiptoList

Version Deployed
v539

**Request body:**
```json
{
    "request": {
        "SearchBy": "",
        "SearchValue": "",
        "CustomerID": "",
        "ShiptoSequence": 1,
        "BilltoSequence": null,
        "FetchOnlyChangedSince": null,
        "RecordFetchLimit": ""
    }
}
```

## CustomerShiptosInChunksList
`POST /Customer/CustomerShiptosInChunksList`

Purpose
Returns a list of customer ship-tos available to the user and available in the current branch the user is logged into. This method is basically the same as CustomerShiptosList, but is specifically made for returning larger chunks of information.
Required Inputs

N/A

Optional Inputs

SearchBy

SearchValue

CustomerID

ShiptoSequence

BilltoSequence

FetchOnlyChangedSince

ChunkStartPointer

RecordFetchLimit

Notes

This method allows a user to request customer ship-tos that have changed since a particular date and time.

This method allows a user to request a specific number of records. Please see the Data Chunking topic for more information.

Valid SearchBy values:

Ship-to Name

Ship-to Address 1

Ship-to Address 2

Ship-to City

Ship-to State

Ship-to ZIP

Ship-to Phone

Keyword

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v618

**Request body:**
```json
{
    "request": {
        "SearchBy": "",
        "SearchValue": "",
        "CustomerID": "",
        "ShiptoSequence": null,
        "BilltoSequence": null,
        "FetchOnlyChangedSince": null,
        "ChunkStartPointer": 0,
        "RecordFetchLimit": null
    }
}
```

## CustomerUpdate
`POST /Customer/CustomerUpdate`

Purpose
Updates a sold-to customer
Required Inputs

CustomerID

CustomerJSON

Optional Inputs

N/A

Notes

The sold-to customer must exist

Any fields not included in the CustomerJSON assume the default values of the existing customer record

DMSi strongly recommends reviewing dsAuditResults regardless of the ReturnCode value

This method includes actions that are performed after the record is updated. When an action updates transaction(s), the field(s) being updated on the transaction must match the original value on the customer record to perform the update.

SetShipToBillToAddresses: Update account info on single customer ship-to and bill-to records when customer account info changes. Valid values: Do not update, Update all, Update customer bill-to account info, and Update customer ship-to account info

UpdAddressOnNonOverriddenTrans: Update address for non-overridden transactions. Valid values: Open and invoiced, Open only

UpdAddressOnOverriddenTrans: Update address for overridden transactions

SecondaryGroupAction has four valid values:

Add – Adds values from SecondaryGroups to the end of the existing secondary customer groups in rank order.

Replace – Replaces all current secondary customer groups with the values from SecondaryGroups. If there are no values in SecondaryGroups, all existing secondary customer groups are removed.

Delete – Deletes secondary customer groups specified in SecondaryGroups.

Delete all – Deletes all current secondary customer groups.

Added and replaced secondary groups are assigned a ranking automatically in the order in which they are listed (Ex. “Sec group 1, Sec group 2”). When deleting secondary groups, any lower ranked secondary groups are assigned a higher ranking.

During processing of the request, if the 'Release eligible orders upon credit criteria change' field is set to 'Prompt' on the Agility A/R Parameters record and the new ReleaseOrdersUponCreditChange field is set to 'True', the system automatically rechecks credit and releases orders based on credit criteria changes received from the API request for the customer sold-to record.

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v534

**Request body:**
```json
{
    "request": {
        "CustomerID": "",
        "CustomerJSON": {
            "dsCustomer": {
                "dtCustomer": [
                    {
                        "Name": "",
                        "DivisionID": "",
                        "GroupID": "",
                        "Address1": "",
                        "Address2": "",
                        "Address3": "",
                        "City": "",
                        "State": "",
                        "ZIP": "",
                        "Country": "",
                        "PhoneFormat": "",
                        "Fax": "",
                        "Phone": "",
                        "MobilePhone": "",
                        "Email": "",
                        "Website": "",
                        "DefaultCurrency": "",
                        "PrintCurrency": "",
                        "FormPrefix": "",
                        "FirstInvoiceDate": "",
                        "StartDate": "",
                        "FirstOrderDate": "",
                        "LastInvoiceDate": "",
                        "Active": true,
                        "FinanceCharge": false,
                        "Nonsaleable": false,
                        "Prospect": true,
                        "CopyPriceGroupsFromShiptoSeq": "1",
                        "CreditCardStorageOption": "",
                        "CheckSoldtoCredit": true,
                        "CheckBilltoCredit": false,
                        "CheckShiptoCredit": false,
                        "PrintSoldtoStatement": false,
                        "PrintBilltoStatement": false,
                        "PrintShiptoStatement": false,
                        "StatementType": "",
                        "CycleCode": "",
                        "StatementPrintSummaryOnly": false,
                        "StatementPrintDiscDate": false,
                        "StatementPrintDiscAmt": false,
                        "StatementPrintDueDate": false,
                        "StatementPrintInvoices": false,
                        "TargetCustomer": false,
                        "RequireInvoice": false,
                        "RequireOrderAcknowledgment": false,
                        "ReferenceNum": "",
                        "ParentCustomerID": "",
                        "FederalTaxNum": "",
                        "StateTaxNum": "",
                        "MunicipalTaxNum": "",
                        "CertificateAppliesTo": "",
                        "AllowCashPayments": false,
                        "AllowCheckPayments": false,
                        "AllowCreditCardPayments": false,
                        "DisplayPriceOnCCDevice": "",
                        "CheckCredit": "",
                        "DontCheckCreditThru": "",
                        "CreditBypassAmt": 0.0,
                        "CreditLimitAmt": 0.0,
                        "OverdueAmt": 0.0,
                        "OverduePercentage": 0.0,
                        "OverdueDays": 0,
                        "DUNNNumber": "",
                        "CreditManager": "",
                        "CreditLimitExpDate": "",
                        "CreditScore": 0.0,
                        "CreditRating": "",
                        "CreditReviewDate": "",
                        "ReleaseOrdersUponCreditChange": false,
                        "BureauNum1Rating": "",
                        "BureauNum1EffectiveDate": "",
                        "BureauNum2Rating": "",
                        "BureauNum2EffectiveDate": "",
                        "LastReviewDate": "",
                        "LastApplicationDate": "",
                        "TradeClass": "",
                        "Class": "",
                        "ConsigneeCode": "",
                        "IndustryCode": "",
                        "MiscField1": "",
                        "MiscField2": "",
                        "MiscField3": "",
                        "MiscField4": "",
                        "MiscField5": "",
                        "MiscField6": "",
                        "MiscField7": "",
                        "MiscField8": "",
                        "MiscField9": "",
                        "MiscField10": "",
                        "MiscField11": "",
                        "MiscField12": "",
                        "UpdShiptoActiveWhenSetActive": true,
                        "UpdShiptoProspectWhenSetProspect": true,
                        "SetShipToBillToAddresses": "",
                        "UpdAddressOnNonOverriddenTrans": "",
                        "UpdAddressOnOverriddenTrans": false,
                        "SetAllShiptosNonSalable": false,
                        "SetNonSalableWithOpen": false,
                        "SecondaryGroupsAction": "",
                        "SecondaryGroups": "",
                        "HomeBranch": "",
                        "AccountType": "",
                        "IRS8300POS": false
                    }
                ]
            }
        }
    }
}
```

## CustomersList
`POST /Customer/CustomersList`

Purpose
Returns a list of customers available to the user
Required Inputs

N/A

Optional Inputs

SearchBy

SearchValue

FetchOnlyChangedSince

ChunkStartPointer

RecordFetchLimit

Notes

The FetchOnlyChangedSince parameter allows the user to determine if they would like records returned that have been modified since a particular date/time. This parameter is evaluated against the update date/time on the record.

This method allows a user to request a specific number of records. Please see the Chunking topic for more information

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Valid SearchBy options:

Customer Name

Customer ID

Customer Address 1

Customer Address 2

Customer City

Customer State

Customer ZIP

Customer Phone

Group ID

Secondary Group ID

Version Deployed
v539

**Request body:**
```json
{
    "request": {
        "SearchBy": "",
        "SearchValue": "",
        "FetchOnlyChangedSince": null,
        "ChunkStartPointer": "",
        "RecordFetchLimit": ""
    }
}
```

## DefaultCustomerShipto
`POST /Customer/DefaultCustomerShipto`

Purpose
Returns the default customer and ship-to assigned to the user in Agility
Required Inputs

LoginID

Optional Inputs

N/A

Notes
N/A
Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v539

**Request body:**
```json
{
    "request": {
        "LoginID": ""
    }
}
```

---

# DataFiles Service  (2 methods)

## SaleTypesList
`POST /DataFiles/SaleTypesList`

Purpose
Returns a list of sale types
Required Inputs

N/A

Optional Inputs

N/A

Notes

The AllowInPartnerView setting is shared between PartnerView and the API and indicates whether or not the sale type is a valid input to methods that create orders or quotes. Only those with AllowInPartnerView = true are valid for those methods. Any valid sale type can be used in other methods

Only sale types having the Affects Inventory flag set are returned with this method

Only sale types marked as Active are returned with this method

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v542

## SalesAgentsList
`POST /DataFiles/SalesAgentsList`

Purpose
Returns a list of sales agents
Required Inputs

N/A

Optional Inputs

SearchBy

SearchValue

IncludeInactive

FetchOnlyChangedSince

ChunkStartPointer

RecordFetchLimit

Notes

This method allows the user to search for specific sales agents with limited criteria. Please see the SearchBy topic for more information

Valid SearchBy values:

Sales Agent ID

First Name

Last Name

This method allows a user to request sales agents that have changed since a particular date and time

This method allows a user to request a specific number of records. Please see the Chunking topic for more information

If the input value sent for IncludeInactive is blank or null, the system saves the value as false

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v614

**Request body:**
```json
{
    "request": {
        "SearchBy": "",
        "SearchValue": "",
        "AdditionalSearchCriteriaJSON": {
            "dsSalesAgentsSearchRequest": {
                "dtSalesAgentsSearchRequest": [
                    {
                        "FetchOnlyChangedSince": "",
                        "IncludeInactive": false,
                        "ChunkStartPointer": 0,
                        "RecordFetchLimit": 0
                    }
                ]
            }
        }
    }
}
```

---

# Dispatch Service  (13 methods)

## DispatchCancel
`POST /Dispatch/DispatchCancel`

Purpose
Cancels dispatch header on an existing, open dispatch
Required Inputs

DispatchID

Optional Inputs

N/A

Notes

Dispatch details and dispatch transactions are not removed when the dispatch is cancelled

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v539

**Request body:**
```json
{
    "request": {
        "DispatchID": 0
    }
}
```

## DispatchCostPacketsDelete
`POST /Dispatch/DispatchCostPacketsDelete`

Purpose
Deletes dispatch cost packet information on an existing dispatch with PO transactions
Required Inputs

DispatchID

CostType

Optional Inputs

SupplierID

Notes

For a supplier-specific cross reference to be sent in the CostType field, the related supplier must be specified in the SupplierID field.

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v539

**Request body:**
```json
{
    "request": {
        "DispatchID": 0,
        "DispatchCostPacketsJSON": {
            "dsDispatchCostPacket": {
                "dtDispatchCostPacket": [
                    {
                        "CostType": "",
                        "SupplierID": ""
                    }
                ]
            }
        }
    }
}
```

## DispatchCostPacketsGet
`POST /Dispatch/DispatchCostPacketsGet`

Purpose
Returns dispatch cost packet information on an existing dispatch with PO transactions
Required Inputs

DispatchID

Optional Inputs

N/A

Notes
N/A
Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v539

**Request body:**
```json
{
    "request": {
        "DispatchID": 0
    }
}
```

## DispatchCostPacketsUpdate
`POST /Dispatch/DispatchCostPacketsUpdate`

Purpose
Creates or updates dispatch cost packet information on an existing dispatch with PO transactions
Required Inputs

DispatchID

CostType

Optional Inputs

AllocateBy

AssignAPReconBasedOnPO

Currency

FixedAmount

SupplierID

Notes

Valid values for AssignAPReconBasedOnPO are true and false. If AssignAPReconBasedOnPO is set to false, AP Recon is assigned based on the Dispatch ID. If AssignAPReconBasedOnPO is set to true, AP Recon is assigned based on the Purchase Order ID. If AssignAPReconBasedOnPO is not sent in the request, this defaults to a value of false.

Any fields not included in the DispatchCostPacketsUpdateJSON assume the default values on a creating a new cost type.

Any fields not included in the DispatchCostPacketsUpdateJSON assume the existing values on updating an existing cost type.

For a supplier-specific cross reference to be sent in the CostType field, the related supplier must be specified in the SupplierID field.

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v539

**Request body:**
```json
{
    "request": {
        "DispatchID": 0,
        "DispatchCostPacketsJSON": {
            "dsDispatchCostPacket": {
                "dtDispatchCostPacket": [
                    {
                        "AllocateBy": "",
                        "AssignAPReconBasedOnPO": false,
                        "CostType": "",
                        "Currency": "",
                        "FixedAmount": 0,
                        "SupplierID": ""
                    }
                ]
            }
        }
    }
}
```

## DispatchDetailsCreate
`POST /Dispatch/DispatchDetailsCreate`

Purpose
Create dispatch details and related dispatch tran on an existing dispatch
Required Inputs

DispatchID

OrderID

OrderType

SubID

OrderDetailSequence; Quantity or DispatchAllQuantity

Optional Inputs

ContainerID

PalletID

Quantity

DispatchAllQuantity

Notes

Valid values for DispatchAllQuantity are true and false. If DispatchAllQuantity is set to false, Quantity is required. If DispatchAllQuantity is set to true, all quantity for the OrderDetailSequence is dispatched unless Quantity is specified.

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v539

**Request body:**
```json
{
    "request": {
        "DispatchID": 0,
        "OrderType": "",
        "OrderID": 0,
        "SubID": 0,
        "DispatchDetailJSON": {
            "dsDispatchDetail": {
                "dtDispatchDetail": [
                    {
                        "OrderDetailSequence": "1",
                        "Quantity": 1,
                        "ContainerID": "",
                        "PalletID": "",
                        "DispatchAllQuantity": false
                    }
                ]
            }
        }
    }
}
```

## DispatchDetailsDelete
`POST /Dispatch/DispatchDetailsDelete`

Purpose
Deletes dispatch details on an existing dispatch transaction
Required Inputs

DispatchID

OrderID

OrderType

SubID

OrderDetailSequence

Optional Inputs

ContainerID

PalletID

Notes

If ContainerID and/or PalletID exist on the order detail sequence that is being deleted, you must include the related ContainerID and/or PalletID in the request to delete.

Branch must be the branch of the detail transaction

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v539

**Request body:**
```json
{
    "request": {
        "DispatchID": 0,
        "OrderType": "",
        "OrderID": 0,
        "SubID": 0,
        "DispatchDetailJSON": {
            "dsDispatchDetail": {
                "dtDispatchDetail": [
                    {
                        "OrderDetailSequence": "1",
                        "ContainerID": "",
                        "PalletID": ""
                    }
                ]
            }
        }
    }
}
```

## DispatchGet
`POST /Dispatch/DispatchGet`

Purpose
Returns a list of dispatch fields related to a specific dispatch ID
Required Inputs

DispatchID

Optional Inputs

N/A

Notes
N/A
Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v539

**Request body:**
```json
{
    "request": {
        "DispatchID": 0
    }
}
```

## DispatchHeaderCreate
`POST /Dispatch/DispatchHeaderCreate`

Purpose
Creates dispatch header fields
Required Inputs

CarrierID

ShipFromSequence

Optional Inputs

N/A

Notes

Any fields not included in the DispatchHeaderCreateJSON assume the default values.

If EstimatedRate is sent in without EstimatedRateType, EstimatedRateType value defaults as “Total”

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v539

**Request body:**
```json
{
    "request": {
        "CarrierID": "",
        "ShipFromSequence": 1,
        "DispatchHeaderJSON": {
            "dsDispatchHeader": {
                "dtDispatchHeader": [
                    {
                        "AdditionalCost": 0,
                        "CarrierFax": "",
                        "CarrierPhone": "",
                        "CleanDry": "",
                        "Contact": "",
                        "DispatchedBy": "",
                        "DispatcherFax": "",
                        "DispatcherPhone": "",
                        "Driver": "",
                        "EstimatedRate": 0,
                        "EstimatedRateType": "",
                        "FirstPickUpDate": "2019-02-19",
                        "FirstPickUpTime": "08:00",
                        "FinalDeliveryDate": "2019-02-22",
                        "FinalDeliveryTime": "16:45",
                        "PackingSlip": "",
                        "PerRateLabel": "",
                        "PerRateMultiplier": 0,
                        "Reference": "",
                        "Released": "",
                        "SCACCode": "",
                        "STCCCode": "",
                        "Tarp": "",
                        "TarpSize": "",
                        "TotalDistance": 0,
                        "TransportNumber": "",
                        "TransportType": "",
                        "WeightLimit": 0
                    }
                ]
            }
        }
    }
}
```

## DispatchHeaderUpdate
`POST /Dispatch/DispatchHeaderUpdate`

Purpose
Updates dispatch header fields
Required Inputs

DispatchID

Optional Inputs

N/A

Notes

Any fields not included in the DispatchHeaderUpdateJSON assume the default values of the existing dispatch ID

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v539

**Request body:**
```json
{
    "request": {
        "DispatchID": "",
        "DispatchHeaderJSON": {
            "dsDispatchHeader": {
                "dtDispatchHeader": [
                    {
                        "AdditionalCost": 0,
                        "CarrierFax": "",
                        "CarrierID": "",
                        "CarrierPhone": "",
                        "CleanDry": "",
                        "Contact": "",
                        "DispatchedBy": "",
                        "DispatcherFax": "",
                        "DispatcherPhone": "",
                        "Driver": "",
                        "EstimatedRate": 0.0,
                        "EstimatedRateType": "",
                        "FirstPickUpDate": "2019-02-19",
                        "FirstPickUpTime": "08:00",
                        "FinalDeliveryDate": "2019-02-22",
                        "FinalDeliveryTime": "16:45",
                        "PackingSlip": "",
                        "PerRateLabel": "",
                        "PerRateMultiplier": 0,
                        "Reference": "",
                        "Released": "",
                        "SCACCode": "",
                        "ShipFromSequence": 1,
                        "STCCCode": "",
                        "Tarp": "",
                        "TarpSize": "",
                        "TotalDistance": 0,
                        "TransportNumber": "",
                        "TransportType": "",
                        "WeightLimit": 0
                    }
                ]
            }
        }
    }
}
```

## DispatchMessageCreate
`POST /Dispatch/DispatchMessageCreate`

Purpose
Creates a dispatch transaction message in the branch the user is logged into
Required Inputs

TranID

MessageText

MessageType

Optional Inputs

PrintOnForms

Notes

MessageText can send a maximum of 1000 characters

Valid values for MessageType are H, Header, F, and Footer

When PrintOnForms is set to true, all eligible forms are set to print the new message

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v554

**Request body:**
```json
{
    "request": {
        "MessageCreateJSON": {
            "dsMessageCreate": {
                "dtMessageCreate": [
                    {
                        "TranID": "",
                        "ShipmentNum": 1,
                        "TranSeq": 1,
                        "MessageText": "",
                        "MessageType": "",
                        "PrintOnForms": false
                    }
                ]
            }
        }
    }
}
```

## DispatchSendASNToWMS
`POST /Dispatch/DispatchSendASNToWMS`

Purpose
Sends ASN to the WMS for a dispatch with PO transactions that affect inventory
Required Inputs

DispatchID

Optional Inputs

N/A

Notes

The purchase orders on the ASN must be set to affect inventory.

The items must be set to send to WMS.

The dispatch must be in a branch that uses WMS.

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v539

**Request body:**
```json
{
    "request": {
        "DispatchID": 0
    }
}
```

## DispatchTranDelete
`POST /Dispatch/DispatchTranDelete`

Purpose
Deletes a transaction from an existing, open dispatch
Required Inputs

DispatchID

OrderType

OrderID

SubID

Optional Inputs

N/A

Notes

The branch variable for this method is the branch of the dispatch transaction, not the dispatch itself. For example: the dispatch is in Branch A, and it includes a dispatch tran in Branch B. To delete the tran, the branch variable must be specified as Branch B

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v539

**Request body:**
```json
{
    "request": {
        "DispatchID": 0,
        "OrderType": "",
        "OrderID": 0,
        "SubID": 0
    }
}
```

## DispatchTranUpdate
`POST /Dispatch/DispatchTranUpdate`

Purpose
Creates or updates dispatch transaction information on an existing dispatch
Required Inputs

DispatchID

OrderID

OrderType

SubID

Optional Inputs

BillofLading

DeliveryID

DestinationCallAppt,

DestinationEndLoadHours

DestinationID

DestinationSeq

DestinationStartLoadHours

Distance

DispatchAllQuantity

OriginCallAppt

OriginEndLoadHours

OriginID

OriginSeq

OriginStartLoadHours

PickUpID

ProNumber

Reference

ShipmentDeliveryDate

ShipmentDeliveryTime

StopSequence

Notes

Valid values for DispatchAllQuantity are true and false. If DispatchAllQuantity is set to false, dispatch details are not created. If DispatchAllQuantity is set to true, dispatch details are created for remaining quantity not yet dispatched on all related order sequences.

If the dispatch includes dispatch cost packets, only transactions with an OrderType of PO can be added to the dispatch.

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v539

**Request body:**
```json
{
    "request": {
        "DispatchID": 0,
        "OrderType": "",
        "OrderID": 0,
        "SubID": 0,
        "DispatchTranJSON": {
            "dsDispatchTran": {
                "dtDispatchTran": [
                    {
                        "BillofLading": "",
                        "DeliveryID": "",
                        "DestinationCallAppt": "",
                        "DestinationEndLoadHours": "16:00",
                        "DestinationID": "",
                        "DestinationSeq": 1,
                        "DestinationStartLoadHours": "08:00",
                        "Distance": 0,
                        "DispatchAllQuantity": "",
                        "OriginCallAppt": "",
                        "OriginEndLoadHours": "12:00",
                        "OriginID": "",
                        "OriginSeq": 1,
                        "OriginStartLoadHours": "07:00",
                        "PickUpID": "",
                        "ProNumber": "",
                        "Reference": "",
                        "ShipmentDeliveryDate": "2019-03-15",
                        "ShipmentDeliveryTime": "12:00",
                        "StopSequence": 1
                    }
                ]
            }
        }
    }
}
```

---

# Inventory Service  (23 methods)

## BranchInventoryList
`POST /Inventory/BranchInventoryList`

Purpose
Returns various quantity totals by branch for a specific item/dimension; similar to what is displayed in stock status
Required Inputs

ItemCode

Optional Inputs

Thickness

Width

Length

Notes

The initial branch returned with the Login method indicates which branch that context is originally positioned in

Once changed, the branch associated with the context is changed and all subsequent calls using that context are positioned in the new branch

If Thickness, Width, and/or Length are excluded from the request, the system assumes a value of zero (0)

Relationships

ContextId and Branch come from Login

Valild values for ItemCode, Thickness, Width, and Length come from ItemsList or ItemsInChunksList

Version Deployed
v554

**Request body:**
```json
{
    "request": {
        "ItemCode": "",
        "Thickness": 0,
        "Width": 0,
        "Length": 0
    }
}
```

## CatalogImageDocCreate
`POST /Inventory/CatalogImageDocCreate`

Purpose
Creates a new image or document record
Required Inputs

ImageOrDocumentID

ImageFile

Type

Optional Inputs

DisplayText

Notes

Valid values for Type are Document and Image

DisplayText can send a maximum of 100 characters

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v556

**Request body:**
```json
{
    "request": {
        "ImageOrDocumentID": "",
        "CatalogImageDocJSON": {
            "dsCatalogImageDoc": {
                "dtCatalogImageDoc": [
                    {
                        "ImageFile": "",
                        "DisplayText": "",
                        "Type": ""
                    }
                ]
            }
        }
    }
}
```

## CatalogImageDocUpdate
`POST /Inventory/CatalogImageDocUpdate`

Purpose
Updates an image or document record
Required Inputs

ImageOrDocumentID

Optional Inputs

DisplayText

Type

Notes

Valid values for Type are Document and Image

DisplayText can send a maximum of 100 characters

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v556

**Request body:**
```json
{
    "request": {
        "ImageOrDocumentID": "",
        "CatalogImageDocJSON": {
            "dsCatalogImageDoc": {
                "dtCatalogImageDoc": [
                    {
                        "ImageFile": "",
                        "DisplayText": "",
                        "Type": ""
                    }
                ]
            }
        }
    }
}
```

## InventoryCostUpdate
`POST /Inventory/InventoryCostUpdate`

Purpose
Updates average cost of items and/or dimensions
Required Inputs

UpdateCriteria

AdjustType

AdjustValue

ReasonCode

Optional Inputs

Remaining fields in dtInventoryCostUpdateSettings, dtInventoryCostUpdateRequest, and dtInventoryCostDimensionRequest not already referenced

Notes

DMSi strongly recommends reviewing dsAuditResults regardless of the ReturnCode value.

Values provided in irrelevant fields are ignored.

An item’s average cost is updated when the following criteria are met:

Item or dimension has quantity on hand in the branch.

Item type is not sundry or detail group header.

Item is not a sales bill of material (BOM) parent.

Item is not set to standard cost.

Cost carried is set to either Branch or Dimension.

If AllowDuplicateItemUpdates = false and an item would be updated two or more times in the same request, the entire request fails, and no updates are completed.

If AllowZeroCost = false and an item or dimension’s average cost would be updated to 0, the average cost of that item or dimension is not updated.

If IncludeNonStock = false and UpdateCriteria is set to ItemGroup or PriceCode, non-stock items are excluded from the request.

If UpdateCriteria = ItemCode, the IncludeNonStock tag is ignored for the item.

Valid values for UpdateCriteria are ItemCode, ItemGroup, and PriceCode.

ItemCode tag is required when the UpdateCriteria = ItemCode.

ItemGroupMajor and ItemGroupMinor tags are required when the UpdateCriteria = ItemGroup.

PriceCodeMajor and PriceCodeMinor tags are required when the UpdateCriteria = PriceCode.

Valid values for AdjustType are Add/Deduct and Replace

When AdjustType = Add/Deduct and the CostCarriedLevel is set to All or All Dimensions, items that are costed at the Dimension level fail and are not updated. You must set the CostCarriedLevel to Specific Dimensions or Branch and Specific Dimensions and specify which dimension records to update when adding or deducting costs.

Set the AdjustValue to a positive number to add to or replace the average cost. Set the AdjustValue to a negative number to deduct from the average cost.

If an item or dimension’s average cost would be negative, the item or dimension fails.

The adjustment amount is applied to each valid item in the criteria, not spread between all items.

The ReasonCode value must match an active inventory adjustment type reason code in the branch.

CostCarriedLevel has five valid values – if no value is specified, Branch and Specific Dimensions is used.

All – Processes item records with the cost carried level set to Branch or Dimension. Average cost updates for dimensional item types are made to all valid dimensions and all tags in the dtInventoryCostDimensionRequest are ignored.

All Dimensions – Processes only dimensional item records with the cost carried level set to Dimension. Average cost updates for dimensional item types are made to all valid dimensions and all tags in the dtInventoryCostDimensionRequest are ignored.

Branch – Processes item records with the cost carried level set to Branch only. All tags in the dtInventoryCostDimensionRequest are ignored.

Branch and Specific Dimensions – Processes item records with the cost carried level set to Branch or Dimension. Average cost updates for dimensional item types with the cost carried level set to Dimension must specify the dimensions to update in the dtInventoryCostDimensionRequest.

Specific Dimensions – Processes only dimensional item records with the cost carried level set to Dimension. You must specify the dimensions to update in the dtInventoryCostDimensionRequest.

If UseAdjustValuesIfDimEmpty = true and the AdjustType or AdjustValue in the dtInventoryCostDimensionRequest are blank or omitted from the request, then the AdjustType and AdjustValue in the dtInventoryCostUpdateRequest are used.

This method contains a parent/child relationship between the dtInventoryCostDimensionRequest and the UpdateCriteria. Please see Parent/Child relationship topic for more information.

There is a many to one relationship between the dtInventoryCostDimensionRequest and the UpdateCriteria as the method allows you the option to specify multiple dimensions for each item code, product group, or price code.

When replacing cost in a branch set up for multiple branch costing, the ReasonCode value must match an active inventory adjustment type reason code in all branches.

Relationships

ContextId and Branch come from Login

Valid values for ItemCode and related Thickness, Width and Length come from ItemsList or ItemsInChunksList

Valid values for ItemGroupMajor come from ItemGroupMajorList or ItemGroupMinorList

Valid values for ItemGroupMinor come from ItemGroupMinorList

Version Deployed
v615

**Request body:**
```json
{
    "request": {
        "InventoryCostUpdateJSON": {
            "dsInventoryCostUpdateSettings": {
                "dtInventoryCostUpdateSettings": [
                    {
                        "AllowDuplicateItemUpdates": false,
                        "AllowZeroCost": false,
                        "IncludeNonStock": false
                    }
                ]
            },
            "dsInventoryCostUpdateRequest": {
                "dtInventoryCostUpdateRequest": [
                    {
                        "UpdateCriteria": "",
                        "ItemCode": "",
                        "ItemGroupMajor": "",
                        "ItemGroupMinor": "",
                        "PriceCodeMajor": "",
                        "PriceCodeMinor": "",
                        "AdjustType": "",
                        "AdjustValue": 0,
                        "ReasonCode": "",
                        "Explanation": "",
                        "CostCarriedLevel": "",
                        "UseAdjustValuesIfDimEmpty": false,
                        "dtInventoryCostDimensionRequest": [
                            {
                                "Thickness": 0,
                                "Width": 0,
                                "Length": 0,
                                "AdjustType": "",
                                "AdjustValue": 0
                            }
                        ]
                    }
                ]
            }
        }
    }
}
```

## InventoryCostUpdateValidate
`POST /Inventory/InventoryCostUpdateValidate`

Purpose
Validates updating average cost for items and/or dimensions
Required Inputs

UpdateCriteria

AdjustType

AdjustValue

ReasonCode

Optional Inputs

Remaining fields in dtInventoryCostUpdateSettings, dtInventoryCostUpdateRequest, and dtInventoryCostDimensionRequest not already referenced

Notes

Refer to the Notes in the InventoryCostUpdate method.

Review the dsAuditResults to identify changes needed in the request in order for the validation to be successful.

Relationships

ContextId and Branch come from Login

Valid values for ItemCode and related Thickness, Width and Length come from ItemsList or ItemsInChunksList

Valid values for ItemGroupMajor come from ItemGroupMajorList or ItemGroupMinorList

Valid values for ItemGroupMinor come from ItemGroupMinorList

Version Deployed
v615

**Request body:**
```json
{
    "request": {
        "InventoryCostUpdateJSON": {
            "dsInventoryCostUpdateSettings": {
                "dtInventoryCostUpdateSettings": [
                    {
                        "AllowDuplicateItemUpdates": false,
                        "AllowZeroCost": false,
                        "IncludeNonStock": false
                    }
                ]
            },
            "dsInventoryCostUpdateRequest": {
                "dtInventoryCostUpdateRequest": [
                    {
                        "UpdateCriteria": "",
                        "ItemCode": "",
                        "ItemGroupMajor": "",
                        "ItemGroupMinor": "",
                        "PriceCodeMajor": "",
                        "PriceCodeMinor": "",
                        "AdjustType": "",
                        "AdjustValue": 0,
                        "ReasonCode": "",
                        "Explanation": "",
                        "CostCarriedLevel": "",
                        "UseAdjustValuesIfDimEmpty": false,
                        "dtInventoryCostDimensionRequest": [
                            {
                                "Thickness": 0,
                                "Width": 0,
                                "Length": 0,
                                "AdjustType": "",
                                "AdjustValue": 0
                            }
                        ]
                    }
                ]
            }
        }
    }
}
```

## ItemActivate
`POST /Inventory/ItemActivate`

Purpose
Activate an item in one or more branches
Required Inputs

Item

ItemBranchCopyFrom

Optional Inputs

dtItemActivateRequest inputs

dtAssociatedFilesRequest inputs

dtSharedBranchesRequest inputs

Notes

The AllSharedBranches must be set to activate the item across all shared branches. The list of branches provided in dtSharedBranchesRequest is read when AllSharedBranches is false.

The branch entered for ItemBranchCopyFrom must be a branch where the item is already active. "Corporate" is a valid option when you want to copy the item from the main sharing branch.

When the ItemBranchCopyFrom branch shares the Item Maintenance table category with the activate-in branch, the system only copies the settings required to be unique by branch and item-related tables.

When the Stock, NonSaleable, Discontinued, UseItemParameterDefaults, or CopyAllAssociatedFiles fields are not included in request, values default based on Data File Parameter settings in Agility.

Items will not activate in branches the login user does not have access to.

Relationships

ContextId and Branch come from Login

Version Deployed
v616

**Request body:**
```json
{
    "request": {
        "Item": "",
        "ItemBranchCopyFrom": "",
        "ItemActivateJSON": {
            "dsItemActivateRequest": {
                "dtItemActivateRequest": [
                    {
                        "UseTemplateItem": false,
                        "AllSharedBranches": false,
                        "Stock": true,
                        "NonSaleable": true,
                        "Discontinued": true,
                        "UseItemParameterDefaults": true,
                        "CopyAllAssociatedFiles": true
                    }
                ],
                "dtAssociatedFilesRequest": [
                    {
                        "Prices": true,
                        "PriceDiscounts": true,
                        "Costs": true,
                        "CostDiscounts": true,
                        "Suppliers": true,
                        "UOMConversions": true,
                        "ScheduleRules": true,
                        "BOMs": true,
                        "RoughOpening": true,
                        "Notes": true,
                        "Attributes": true,
                        "AlternateItems": true,
                        "ImagesAndDocuments": true,
                        "PhaseAndTaskTemplates": true,
                        "ItemMiscFields": true,
                        "NonStockLocation": true,
                        "MiscCostPrice": true,
                        "MiscCostPriceDescription": true,
                        "MarketCost": true,
                        "StandardCost": true,
                        "RandomLengthCode": true
                    }
                ],
                "dtSharedBranchesRequest": [
                    {
                        "Branch": ""
                    },
                    {
                        "Branch": ""
                    }
                ]
            }
        }
    }
}
```

## ItemCreateFromTemplate
`POST /Inventory/ItemCreateFromTemplate`

Purpose
Creates a single item and associated item_branch record(s)
Required Inputs

CopyFromItem

Optional Inputs

N/A

Notes

The initial branch returned with the Login method indicates which branch that context is originally positioned in

Once changed, the branch associated with the context is changed and all subsequent calls using that context are positioned in the new branch

DMSi strongly recommends reviewing dsAuditResults regardless of the ReturnCode value

Any fields not included in the ItemCreateFromTemplateJSON assume the default values of the copy from item and item_branch record(s)

Exception: The 'Discontinued' field is unset when it is not included in the file

The item type assigned to an item cannot be changed using the API. It is copied from the template item.

The CopyFromItem input is required

The StockingToCostingConvFactor is required when either the StockingUOM or CostingUOM is specified and the assigned Stocking and Costing UOMs are not the same

New UOM conversions are auto created in Agility when the StockingToCostingConvFactor, AlternateUOM1ConvFactor, AlternateUOM2ConvFactor, or AlternateUOM3ConvFactor inputs are not already defined

When the AlternateUOM1, AlternateUOM2, or AlternateUOM3 inputs are assigned to the CopyFromItem with a single conversion factor, the conversion factor is updated per the associated input value.

When the AlternateUOM1, AlternateUOM2, or AlternateUOM3 inputs are assigned to the CopyFromItem with multiple conversion factors, the AlternateUOM and conversion factor inputs are added to the item as new UOM conversions

When creating a new item, the system does not copy BOM, attribute, rough opening, schedule rules, image, or document records from the CopyFromTemplateItem

Upon creation of a new item, reorder fields are cleared regardless of the CopyFromTemplateItem values

Item suppliers are not copied from the template item to the new item

The ItemSupplierCode is always processed as being the primary item supplier assigned to an item.

When creating dimension type items, dimension records assigned to the template item are copied to the new item.

TheEcommerceDescription can be sent in plain text or html

Relationships

ContextId and Branch come from Login

Version Deployed
v548

**Request body:**
```json
{
    "request": {
        "Item": "",
        "CopyFromItem": "",
        "ItemCreateFromTemplateJSON": {
            "dsItemCreateFromTemplate": {
                "dtItemCreateFromTemplate": [
                    {
                        "ItemGroupMajor": "",
                        "ItemGroupMinor": "",
                        "PriceCodeMajor": "",
                        "PriceCodeMinor": "",
                        "StockingUOM": "",
                        "CostingUOM": "",
                        "StockingToCostingConvFactor": 0,
                        "Size": "",
                        "ItemDescription": "",
                        "ExtDescription": "",
                        "PieceReference": "",
                        "StockingToPieceCalculation": "",
                        "StandardThickness": 0,
                        "Thickness": 0,
                        "ThicknessUOM": "",
                        "StandardWidth": 0,
                        "Width": 0,
                        "WidthUOM": "",
                        "LengthUOM": "",
                        "AlternateUOM1": "",
                        "AlternateUOM1ConvFactor": 0,
                        "AlternateUOM2": "",
                        "AlternateUOM2ConvFactor": 0,
                        "AlternateUOM3": "",
                        "AlternateUOM3ConvFactor": 0,
                        "StockItem": 0,
                        "Active": 0,
                        "TemplateForNonStocks": "",
                        "NonSaleable": "",
                        "Discontinued": "",
                        "AllowInPartnerview": "",
                        "AllowInAgilityConfigurator": "",
                        "AllowInMobileApps": "",
                        "AllowInECommerceAndAPI": "",
                        "UserDefinedKeywords": "",
                        "ShippingBOLCode": "",
                        "ShippingMSDS": "",
                        "TaxCategory": "",
                        "ItemSupplierCode": "",
                        "ItemSupplierShipFromSequence": 0,
                        "ItemSupplierPartNumber": "",
                        "ItemSupplierWeight": 0,
                        "ItemSupplierWeightUOM": "",
                        "ItemSupplierLoad": 0,
                        "ItemSupplierLoadUOM": "",
                        "AllowBrokenUOMInCountEntry": true,
                        "BrokenUOM": "",
                        "DisplayUOM": "",
                        "PickingTallyUOM": "",
                        "DWReportUOM": "",
                        "SOQuoteUOM": "",
                        "CMUOM": "",
                        "PickingUOM": "",
                        "DeliveryUOM": "",
                        "InvoiceUOM": "",
                        "UpdateTranFormUOMs": true,
                        "CountUOM": "",
                        "AllowDescOverride": true,
                        "TaxableForSales": true,
                        "TaxableForTaxCost": true,
                        "DisplayMarket": true,
                        "PrintItemExtDesc": true,
                        "EcommerceDesc": ""
                    }
                ]
            }
        }
    }
}
```

## ItemCustomFieldsList
`POST /Inventory/ItemCustomFieldsList`

Purpose
Returns the custom fields for a specified set of items/dimensions
Required Inputs

ItemCode for each input record

Optional Inputs

Thickness

Width

Length

Notes

The DataType returned indicates which related Data field should be used to find the appropriate value. For example, if the DataType = Text, the appropriate value is in the CharacterData

For data types of decimal, integer or logical, a default value of 0.0, 0 or false is returned if there is no data. This result does not necessarily mean this represents the data entered in the system, but is what users would see in the Agility application if there was no entry as well

All custom fields available for the item requested are returned regardless of whether the custom field has a value entered

For dimension specific item custom fields, you must include the appliable Thickness, Width, and Length

For the main item record, set the Thickness, Width, and Length to 0 to return the main item record for a dimension item

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Valid values for ItemCode and related Thickness, Width and Length come from ItemsList or ItemsInChunksList

Version Deployed
v542

**Request body:**
```json
{
    "request": {
        "dsItemCustomFieldsListRequest": {
            "dtItemCustomFieldsListRequest": [
                {
                    "ItemCode": "",
                    "Thickness": 0,
                    "Width": 0,
                    "Length": 0
                }
            ]
        }
    }
}
```

## ItemCustomFieldsUpdate
`POST /Inventory/ItemCustomFieldsUpdate`

Purpose
Updates custom field values associated for a set of items and/or dimensions
Required Inputs

ItemCode

Optional Inputs

DataTypeCharacterData

DateData

DecimalData

IntegerData

LogicalData

Thickness

Width

Length

Notes

The data type associated with the custom field in Agility dictates which of the Data fields should contain the data to be saved to the record. Please see Relationship notes below

Values provided in irrelevant fields are ignored

To update custom fields for a dimension, Thickness, Width and Length fields based on item type are necessary inputs

To update the main record for a dimension item, set the Thickness, Width, and Length to zero

If there are failures or warnings due to business logic, the method will have a ReturnCode = 0, but will also return dtItemCustomFieldResults. dtItemCustomFieldResults is returned as an output for the method IF the Failures and/or Warnings field are/is not empty. Those fields contain more information about what may not have processed as expected

To update an item across all shared branches, the item must be active and valid in the login branch

Relationships

ContextId and Branch come from Login

Valid values for FieldLabel for each come from ItemCustomFieldsList, including the current value associated

Version Deployed
v543

**Request body:**
```json
{
    "request": {
        "UpdateCustomFieldsJSON": {
            "dsItemCustomFieldsRequest": {
                "dtItemCustomFieldsRequest": [
                    {
                        "ItemCode": "",
                        "AllSharedBranches": true,
                        "Thickness": null,
                        "Width": null,
                        "Length": null,
                        "FieldLabel": "",
                        "DataType": "",
                        "CharacterData": "",
                        "DateData": null,
                        "DecimalData": 0.0,
                        "IntegerData": 0,
                        "LogicalData": false
                    }
                ]
            }
        }
    }
}
```

## ItemGroupMajorList
`POST /Inventory/ItemGroupMajorList`

Purpose
Returns a list of item/product group majors
Required Inputs

N/A

Optional Inputs

N/A

Notes

N/A

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v542

## ItemGroupMinorList
`POST /Inventory/ItemGroupMinorList`

Purpose
Returns a list of item/product group minors associated with a specified item/product group major
Required Inputs

ItemGroupMajor

Optional Inputs

N/A

Notes

N/A

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Valid values for ItemGroupMajor come from ItemGroupMajorList

Version Deployed
v542

**Request body:**
```json
{
    "request": {
        "ItemGroupMajor": ""
    }
}
```

## ItemImageDocCreate
`POST /Inventory/ItemImageDocCreate`

Purpose
Assigns an image or document to an item record
Required Inputs

ImageOrDocumentID

Item

Optional Inputs

N/A

Notes

N/A

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v556

**Request body:**
```json
{
    "request": {
        "ImageOrDocumentID": "",
        "Item": "",
        "ItemImageDocCreateJSON": {
            "dsItemImageDocCreate": {
                "dtItemImageDocCreate": [
                    {
                        "Primary": ""
                    }
                ]
            }
        }
    }
}
```

## ItemImageDocDelete
`POST /Inventory/ItemImageDocDelete`

Purpose
Deletes the assignment of an image or document to an item record
Required Inputs

ImageOrDocumentID

Item

Optional Inputs

N/A

Notes

N/A

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v556

**Request body:**
```json
{
    "request": {
        "ImageOrDocumentID": "",
        "Item": ""
    }
}
```

## ItemPriceAndAvailabilityList
`POST /Inventory/ItemPriceAndAvailabilityList`

Purpose
Returns specific price information for an item or set of items based on a specific customer and sale type with related quantities
Required Inputs

CustomerID

dtItemToProcessRequest and dtItemDimensionToProcessReq information

Optional Inputs

ShiptoSequence

SaleType

DateToCalculatePriceFor

Notes

If DateToCalculatePriceFor is left blank, the current date is used

DMSi strongly recommends reviewing the ItemAuditResults regardless of the ReturnCode value

If requesting dimension information, the ItemCode and PartNumber in the dtItemDimensionToProcessReq must be identical to those sent in the dtItemToProcessRequest

The system does not search dimension specific cross reference records when locating an item when a PartNumber is included in the request

The method returns item information in the Display UOM defined on the item record, with the following exceptions:

For the main item record of dimension type items where the display UOM is set to the piece reference UOM, the system returns item information in the stocking UOM, since the piece reference is invalid for the main item record.

For sheet good and specific length lumber items with a display UOM of UNIT, the system returns item information in the stocking UOM, since various piece counts may apply

The system includes quantities for alternate items assigned to component items when calculating the MaxProductionUnits value for a BOM Parent item when all of the following conditions are met:

Branch Parameter Include alternates when calculating maximum production units on the Inventory tab is set.

If the alternate item has the Applies to work orders from sales orders option set and the Auto order option is set to ‘Auto order at work order entry’ in Alternates Maintenance.

If the Stocking UOM on the component item and alternate item are not the same, there must be a UOM conversion setup on the alternate item to get back to the stocking UOM on the component item.

If the component is a dimension type item, the alternate item must be setup for the overall 00x00x00 record.

The PriceMargin, PriceMultiplier, and PriceAdditionalAmount tags return a 0 if the price is not calculated using the margin percent, multiplier, or additional amount formula, respectively.

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Valid values for ItemCode come from ItemsList or ItemsInChunksList. Additionally, Width and Length come from ItemsList or ItemsInChunksList

Version Deployed
v542

**Request body:**
```json
{
    "request": {
        "dsItemPriceAndAvailRequest": {
            "dtPriceAndAvailRequest": [
                {
                    "CustomerID": "",
                    "ShiptoSequence": 1,
                    "SaleType": "",
                    "DateToCalculatePriceFor": "2019-08-15",
                    "UseOrderRestrictions": true
                }
            ],
            "dtItemToProcessRequest": [
                {
                    "ItemCode": "",
                    "PartNumber": "",
                    "OrderQuantity": 0,
                    "UOM": ""
                }
            ],
            "dtItemDimensionToProcessReq": [
                {
                    "ItemCode": "",
                    "PartNumber": "",
                    "Thickness": 0,
                    "Width": 0,
                    "Length": 0,
                    "OrderQuantity": 0,
                    "UOM": ""
                }
            ]
        }
    }
}
```

## ItemsInChunksList
`POST /Inventory/ItemsInChunksList`

Purpose
Returns item related information for a group of items; optionally, results can include quantity and price information; this method is basically the same as ItemsList, but is specifically made for returning larger chunks of items
Required Inputs

N/A

Optional Inputs

SearchBy

SearchValue

ChunkStartPointer

IncludeNonStock

IncludeNonsaleable

IncludePriceData

IncludeQuantityData

RecordFetchLimit

Notes

The method allows the user to search for and select items based on SearchBy or to request the information for all items.

Valid SearchBy option is Item Code

This method allows a user to request a specific number of records. Please see the Data Chunking topic for more information

The method returns item information in the Display UOM and Stocking UOM defined on the item record, with the following exceptions:

For the main item record of dimension type items where the display UOM is set to the piece reference UOM, the system returns item information in the stocking UOM, since the piece reference is invalid for the main item record.

For sheet good and specific length lumber items with a display UOM of UNIT, the system returns item information in the stocking UOM, since various piece counts may apply.

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

For dimensional item types, the main item will be represented in dtItemResponse with the related dimensions represented in dtItemDimensionResponse. The relationship between the tables is found with the ItemCode. There can be a one to many relationship between dtItemResponse and dtItemDimensionResponse with the Thickness, Width, Length fields distinguishing between records in dtItemDimensionResponse

Version Deployed
v542

**Request body:**
```json
{
    "request": {
        "dsItemsInChunksListRequest": {
            "dtItemsInChunksListRequest": [
                {
                    "SearchBy": "",
                    "SearchValue": "",
                    "ChunkStartPointer": 0,
                    "IncludeNonStock": true,
                    "IncludeNonSaleable": true,
                    "IncludePriceData": true,
                    "IncludeQuantityData": true,
                    "RecordFetchLimit": 1
                }
            ]
        }
    }
}
```

## ItemsList
`POST /Inventory/ItemsList`

Purpose
Returns item related information for a group of items; optionally, results can include quantity and price information
Required Inputs

N/A

Optional Inputs

SearchBy

SearchValue

ItemGroupMajor

ItemGroupMinor

IncludeNonStock

IncludeNonsaleable

IncludePriceData

IncludeQuantityData

RecordFetchLimit

Notes

The method allows the user to search for and select items based on ItemGroupMajor, ItemGroupMajor and ItemGroupMinor combination, SearchBy, or to request the information for all items.

Valid SearchBy options are Item Code, Size, Description, Ext. Description Contains, and Keyword Search

This method allows a user to request a specific number of records. Please see the Data chunking topic for more information

The method returns item information in the Display UOM defined on the item record, with the following exceptions:

For the main item record of dimension type items where the display UOM is set to the piece reference UOM, the system returns item information in the stocking UOM, since the piece reference is invalid for the main item record.

For sheet good and specific length lumber items with a display UOM of UNIT, the system returns item information in the stocking UOM, since various piece counts may apply.

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Valid values for ItemGroupMajor come from ItemGroupMajorList or ItemGroupMinorList

Valid values for ItemGroupMinor come from ItemGroupMinorList

For dimensional item types, the main item will be represented in dtItemResponse with the related dimensions represented in dtItemDimensionResponse. The relationship between the tables is found with the ItemCode. There can be a one to many relationship between dtItemResponse and dtItemDimensionResponse with the Thickness, Width, Length fields distinguishing between the records in dtItemDimensionResponse

Version Deployed
v542

**Request body:**
```json
{
    "request": {
        "dsItemsListRequest": {
            "dtItemsListRequest": [
                {
                    "SearchBy": "",
                    "SearchValue": "",
                    "ItemGroupMajor": "",
                    "ItemGroupMinor": "",
                    "IncludeNonStock": true,
                    "IncludePriceData": true,
                    "IncludeQuantityData": true,
                    "IncludeNonSaleable": true,
                    "RecordFetchLimit": 1
                }
            ]
        }
    }
}
```

## ItemTalliesList
`POST /Inventory/ItemTalliesList`

Purpose
Returns tally information
Required Inputs

ItemCode

LevelOfInformation

Optional Inputs

Location

Lot

Tag

Content

Width

Length

Notes

Valid values for LevelOfInformation are Branch, Location, Lot, Tag, and Content and are directly related to the Quantity Carried on the item

Enter values for Location, Lot, Tag and/or Content to refine the results to be more specific as needed

The method returns item information in the Display UOM defined on the item record, with the following exceptions:

For the main item record of dimension type items where the display UOM is set to the piece reference UOM, the system returns item information in the stocking UOM, since the piece reference is invalid for the main item record.

For sheet good and specific length lumber items with a display UOM of UNIT, the system returns item information in the stocking UOM, since various piece counts may apply

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Valid values for ItemCode come from ItemsList or ItemsInChunksList. Additionally, Width and Length come from ItemsList or ItemsInChunksList

Version Deployed
v542

**Request body:**
```json
{
    "request": {
        "dsItemTalliesListRequest": {
            "dtItemTalliesListRequest": [
                {
                    "ItemCode": "",
                    "Location": "",
                    "Lot": "",
                    "Tag": "",
                    "Content": "",
                    "Width": 0,
                    "Length": 0,
                    "LevelOfInformation": ""
                }
            ]
        }
    }
}
```

## ItemUOMsList
`POST /Inventory/ItemUOMsList`

Purpose
Returns UOM information for a specified set of items
Required Inputs

ItemCode

Optional Inputs

N/A

Notes

N/A

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Valid values for ItemCode come from ItemsList or ItemsInChunksList.

There can be more than one record in the dtItemUOMResponse for each ItemCode requested

Version Deployed
v542

**Request body:**
```json
{
    "request": {
        "dsItemUOMsListRequest": {
            "dtItemUOMsListRequest": [
                {
                    "ItemCode": ""
                }
            ]
        }
    }
}
```

## ItemUpdate
`POST /Inventory/ItemUpdate`

Purpose
Updates a single item and associated item_branch record(s)
Required Inputs

Item

Optional Inputs

N/A

Notes

DMSi strongly recommends reviewing dsAuditResults regardless of the ReturnCode value

Any fields not included in the ItemUpdateJSON will not be updated

The AllSharedBranches must be set for updates across all shared branches. New item branch records are not created when performing updates across shared branches.

When including the SharedBranchesRequest data table in the request the AllSharedBranches input cannot be set to ‘true’.

The item type assigned to an item cannot be changed using the API.

When performing updates across shared branches, the update must be successfully performed in the login branch before being applied to any shared branches. An existing item code cannot be activated in a shared branch using this API.

The StockingToCostingConvFactor is required if changing either the StockingUOM or CostingUOM and the assigned Stocking and Costing UOMs are not the same

New UOM conversions are auto created in Agility when the StockingToCostingConvFactor, AlternateUOM1ConvFactor, AlternateUOM2ConvFactor, or AlternateUOM3ConvFactor inputs are not already defined

When the AlternateUOM1, AlternateUOM2, or AlternateUOM3 inputs are already assigned to the item with a single conversion factor, the conversion factor is updated per the associated input value.

When the AlternateUOM1, AlternateUOM2, or AlternateUOM3 inputs are already assigned to the item with multiple conversion factors, the AlternateUOM# and conversion factor inputs are added to the item as new UOM conversions

When inactivating an item (Active value = “NO”), the TemplateForNonStocks field is not processed.

The ItemSupplierCode is always processed as being the primary item supplier assigned to an item. Any pre-existing item supplier assigned to an item is auto unset as being the primary supplier.

The ItemSupplierCode and ItemSupplierShipFromSequence are required to update any of the associated item supplier fields.

The EcommerceDescription can be sent in plain text or html.

Relationships

ContextId and Branch come from Login

Version Deployed
v548

**Request body:**
```json
{
    "request": {
        "Item": "",
        "ItemUpdateJSON": {
            "dsItemUpdate": {
                "dtItemUpdate": [
                    {
                        "AllSharedBranches": 0,
                        "ApplyToAllDimensions": 0,
                        "ItemGroupMajor": "",
                        "ItemGroupMinor": "",
                        "PriceCodeMajor": "",
                        "PriceCodeMinor": "",
                        "StockingUOM": "",
                        "CostingUOM": "",
                        "StockingToCostingConvFactor": 0,
                        "Size": "",
                        "ItemDescription": "",
                        "ExtDescription": "",
                        "ManufacturerID": "",
                        "PieceReference": "",
                        "StockingToPieceCalculation": "",
                        "StandardThickness": 0,
                        "Thickness": 0,
                        "ThicknessUOM": "",
                        "StandardWidth": 0,
                        "Width": 0,
                        "WidthUOM": "",
                        "LengthUOM": "",
                        "AlternateUOM1": "",
                        "AlternateUOM1ConvFactor": 0,
                        "AlternateUOM2": "",
                        "AlternateUOM2ConvFactor": 0,
                        "AlternateUOM3": "",
                        "AlternateUOM3ConvFactor": 0,
                        "HandlingCode": "",
                        "DefaultLocation": "",
                        "DefaultSublocation": "",
                        "BuyerID": "",
                        "OverallABC": "",
                        "HistoryStartDate": "",
                        "DoOrderCalculations": 0,
                        "StockItem": 0,
                        "Weight": 0,
                        "WeightUOM": "",
                        "Load": 0,
                        "LoadUOM": "",
                        "UpdOverriddenItemSuppWeightLoad": false,
                        "Active": 0,
                        "TemplateForNonStocks": "",
                        "NonSaleable": "",
                        "Discontinued": "",
                        "AllowInPartnerview": "",
                        "AllowInAgilityConfigurator": "",
                        "AllowInMobileApps": "",
                        "AllowInECommerceAndAPI": "",
                        "UserDefinedKeywords": "",
                        "ShippingBOLCode": "",
                        "ShippingMSDS": "",
                        "TaxCategory": "",
                        "ItemSupplierCode": "",
                        "ItemSupplierShipFromSequence": 0,
                        "ItemSupplierPartNumber": "",
                        "ItemSupplierWeight": 0,
                        "ItemSupplierWeightUOM": "",
                        "ItemSupplierLoad": 0,
                        "ItemSupplierLoadUOM": "",
                        "ItemSupplierUpdateLead": 0,
                        "ItemSupplierMostRecent": 0,
                        "ItemSupplierSecondRecent": 0,
                        "ItemSupplierThirdRecent": 0,
                        "ItemSupplierFourthRecent": 0,
                        "ItemSupplierFifthRecent": 0,
                        "AllowBrokenUOMInCountEntry": true,
                        "BrokenUOM": "",
                        "DisplayUOM": "",
                        "PickingTallyUOM": "",
                        "DWReportUOM": "",
                        "SOQuoteUOM": "",
                        "CMUOM": "",
                        "PickingUOM": "",
                        "DeliveryUOM": "",
                        "InvoiceUOM": "",
                        "UpdateTranFormUOMs": true,
                        "CountUOM": "",
                        "AllowDescOverride": true,
                        "StandardCostItem": 0,
                        "UpdateInventoryStandardCostChg": 0,
                        "ConsignmentInventory": "",
                        "TaxableForSales": true,
                        "TaxableForTaxCost": true,
                        "DisplayMarket": true,
                        "PrintItemExtDesc": true,
                        "EcommerceDesc": "",
                        "MarketCostFormula": "",
                        "MarketCost": 0,
                        "MarketCostFixed": 0,
                        "StandardCost": 0,
                        "LastPOCost": 0,
                        "LastPOCostFixed": 0,
                        "UpdateLastPOCostPrimarySupplier": 0,
                        "UpdateLastPOCostDoesNotAffectInv": 0,
                        "POCostDefault": "",
                        "MiscCost1": 0,
                        "MiscCost1Description": "",
                        "MiscCost2": 0,
                        "MiscCost2Description": "",
                        "MiscCost3": 0,
                        "MiscCost3Description": "",
                        "MiscCost4": 0,
                        "MiscCost4Description": "",
                        "MiscCost5": 0,
                        "MiscCost5Description": "",
                        "MiscField1": "",
                        "MiscField2": "",
                        "MiscField3": "",
                        "MiscField4": "",
                        "MiscField5": "",
                        "MiscField6": "",
                        "MiscField7": "",
                        "MiscField8": "",
                        "MiscField9": "",
                        "MiscField10": "",
                        "MiscField11": "",
                        "MiscField12": "",
                        "MiscField13": "",
                        "MiscField14": "",
                        "MiscField15": "",
                        "MiscField16": "",
                        "MiscField17": "",
                        "MiscField18": "",
                        "MiscField19": "",
                        "MiscField20": ""
                    }
                ],
                "dtSharedBranchesRequest": [
                    {
                        "Branch": ""
                    },
                    {
                        "Branch": ""
                    }
                ]
            }
        }
    }
}
```

## PreReceiptSave
`POST /Inventory/PreReceiptSave`

Purpose
Allows pre-receipt records to be saved for purchase orders and reman orders
Required Inputs

FileSequence

TranType

TranID

ItemSeqence

TranSequence

ItemCode

ActivateItemsNotInBranch

AddItem

MarkTagsAsPrinted

DeleteRemaining

Location

Quantity

UOM

Optional Inputs

Remaining fields in dtPreReceiptItem

Remaining items in dtPreReceiptStorage

Notes

Valid values for TranType are PO and RM

When ActivateItemsNotInBranch is true the system will activate the item being added to the transaction that is currently not active or will create the item branch record if one does not exist

For system-generated tags leave the Tag field blank

Content field is optional for dimensional items

Leave Location, Lot, or Content fields blank when defaults are setup and that’s the value to be used

ShipmentNum is an optional field that can be used for TranType PO to adjust prereceicpts on transfer purchase orders`

Relationships

ContextId and Branch come from Login

Version Deployed
v600

**Request body:**
```json
{
    "request": {
        "PreReceiptSaveJSON": {
            "dsPreReceiptSave": {
                "dtPreReceiptHeader": [
                    {
                        "FileSequence": 1,
                        "TranType": "",
                        "TranID": "",
                        "ShipmentNum": 0,
                        "dtPreReceiptItem": [
                            {
                                "FileSequence": 1,
                                "ItemSequence": 1,
                                "TranSequence": 0,
                                "ItemCode": "",
                                "ItemXREF": "",
                                "ItemSpecies": "",
                                "ItemGrade": "",
                                "ItemSubGrade": "",
                                "ItemThickness": "",
                                "ItemSurface": "",
                                "ItemDryness": "",
                                "ActivateItemsNotInBranch": false,
                                "AddItem": false,
                                "MarkTagsAsPrinted": false,
                                "DefaultRMKey": "",
                                "DeleteRemaining": false,
                                "dtPreReceiptStorage": [
                                    {
                                        "FileSequence": 1,
                                        "ItemSequence": 1,
                                        "StorageSequence": 1,
                                        "Location": "",
                                        "Lot": "",
                                        "Tag": "",
                                        "Content": "",
                                        "Thickness": 0,
                                        "Width": 0,
                                        "Length": 0,
                                        "NominalLength": 0,
                                        "PieceCount": 0,
                                        "Comments": "",
                                        "Comments2": "",
                                        "Quantity": 0,
                                        "UOM": ""
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }
    }
}
```

## TagInfoGet
`POST /Inventory/TagInfoGet`

Purpose
Returns the information related to a specified inventory tag or tags
Required Inputs

Tag

Optional Inputs

N/A

Notes

N/A

Relationships

N/A

Version Deployed
v545

**Request body:**
```json
{
    "request": {
        "Tag": ""
    }
}
```

## TagValuesList
`POST /Inventory/TagValuesList`

Purpose
Returns the next available inventory tag sequences
Required Inputs

NumberOfTagSequences

Optional Inputs

N/A

Notes

Use inventory tagging must be set in Branch Parameters for the branch you are sending in the header

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v545

**Request body:**
```json
{
    "request": {
        "dsTagValuesListRequest": {
            "dtTagValuesListRequest": [
                {
                    "NumberOfTagSequences": 1
                }
            ]
        }
    }
}
```

## TagsPrint
`POST /Inventory/TagsPrint`

Purpose
Prints inventory tags to a specified printer
Required Inputs

Tag

Optional Inputs

Sequence

PrinterID

Notes

When printing multiple tags, you can include an optional print sequence, Sequence, in the request

If PrinterID is not specified, the tag prints to the Forms Assignment default printer for Inventory Tags

Relationships

N/A

Version Deployed
v545

**Request body:**
```json
{
    "request": {
        "dsTagsPrintRequest": {
            "dtTagsPrintRequest": [
                {
                    "Sequence": 1,
                    "Tag": "",
                    "PrinterID": ""
                }
            ]
        }
    }
}
```

---

# Orders Service  (40 methods)

## CreditMemoCreateFromHistory
`POST /Orders/CreditMemoCreateFromHistory`

Purpose
Creates a new credit memo from an invoiced shipment, which can include BOM parent items and dimensional items with tallies specified.
Required Inputs

OriginalSOID

OriginalShipmentNumber

OriginalSequence

OrderQty

UOM

ReasonCode

Optional Inputs

Remaining fields in the dtOrderHeaderRequest, dtOrderItemRequest, dtOrderItemDimensionRequest not already referenced

Notes

This method allows parent items to be returned on a credit memo. You must specify the WorkOrderID and CompletionSeq tags in the dtOrderItemRequest to successfully add a BOM parent item to the credit memo.

At least one item or dimension must be sent in.

When adding a dimensional item, the Thickness, Width and/or Length are required based on item type. In addition, the OrderQty and UOM must be specified at the dimension level.

Relationships

ContextId and Branch come from Login

Valid values for OriginalSOID, OriginalShipmentNumber, OriginalSequence, OrderQty, and UOM come from ShipmentList.

The NewOrderID returned from this method can be used in conjunction with the CreditMemoList to verify the new credit memo was created as expected

When PlaceOnHold is set to true, the transaction is created with a Hold approval status. When PlaceOnHold is set to false, the transaction is created with a Does Not Apply approval status.

The ReasonCode determines whether the item detail is a debit or a credit, regardless of the positive or negative value sent in the OrderQty tag.

This method contains a parent/child relationship between the dtOrderItemRequest and dtOrderItemDimensionRequest. Please see the Parent/Child relationship topic for more information.

When the RMAFlag is set to true, the system creates an RMA Credit Memo with a status type of RMA. When the RMAFlag is sent to false, the system creates a Credit Memo with a status type of CM.

Version Deployed
v554

**Request body:**
```json
{
    "request": {
        "OriginalSOID": 0,
        "OriginalShipmentNumber": 0,
        "OrderHeaderJSON": {
            "dsOrderHeaderRequest": {
                "dtOrderHeaderRequest": [
                    {
                        "ExpectedPickUp": "",
                        "RMAFlag": true,
                        "OrderedBy": "",
                        "OrderMessage": "",
                        "PlaceOnHold": true,
                        "MiscField1": "",
                        "MiscField2": "",
                        "MiscField3": "",
                        "MiscField4": "",
                        "MiscField5": "",
                        "MiscField6": "",
                        "MiscField7": "",
                        "MiscField8": "",
                        "MiscField9": "",
                        "MiscField10": "",
                        "MiscField11": "",
                        "MiscField12": "",
                        "MiscDate1": "",
                        "MiscDate2": "",
                        "ShipmentTrackingNumber": "",
                        "ShipmentTrackingDate": ""
                    }
                ]
            }
        },
        "OrderItemJSON": {
            "dsOrderItemRequest": {
                "dtOrderItemRequest": [
                    {
                        "OriginalSequence": 0,
                        "OrderQty": 0,
                        "UOM": "",
                        "ReasonCode": "",
                        "PurchaseOrderID": 0,
                        "ItemMessage": "",
                        "PrintMsgOnForms": true,
                        "PrintMsgOnFormsOverride": true,
                        "WorkOrderID": 0,
                        "CompletionSeq": 0,
                        "UseDefaultLocation": false,
                        "dtOrderItemDimensionRequest": [
                            {
                                "OriginalSequence": 0,
                                "Thickness": 0,
                                "Width": 0,
                                "Length": 0,
                                "PieceCount": 0,
                                "OrderQty": 0,
                                "UOM": ""
                            }
                        ]
                    },
                    {
                        "OriginalSequence": 0,
                        "OrderQty": 0,
                        "UOM": "",
                        "ReasonCode": "",
                        "PurchaseOrderID": 0,
                        "ItemMessage": "",
                        "PrintMsgOnForms": true,
                        "PrintMsgOnFormsOverride": true,
                        "WorkOrderID": 0,
                        "CompletionSeq": 0,
                        "UseDefaultLocation": true,
                        "dtOrderItemDimensionRequest": [
                            {
                                "OriginalSequence": 0,
                                "Thickness": 0,
                                "Width": 0,
                                "Length": 0,
                                "PieceCount": 0,
                                "OrderQty": 0,
                                "UOM": ""
                            },
                            {
                                "OriginalSequence": 0,
                                "Thickness": 0,
                                "Width": 0,
                                "Length": 0,
                                "PieceCount": 0,
                                "OrderQty": 0,
                                "UOM": ""
                            }
                        ]
                    },
                    {
                        "OriginalSequence": 0,
                        "OrderQty": 0,
                        "UOM": "",
                        "ReasonCode": "",
                        "PurchaseOrderID": 0,
                        "ItemMessage": "",
                        "PrintMsgOnForms": false,
                        "PrintMsgOnFormsOverride": false,
                        "WorkOrderID": 0,
                        "CompletionSeq": 0,
                        "UseDefaultLocation": false
                    }
                ]
            }
        }
    }
}
```

## CreditMemoList
`POST /Orders/CreditMemoList`

Purpose
Returns a list of credit memos for a specified customer
Required Inputs

CustomerID

Value Required

The following inputs require a value due to data type:

OrderDateRangeStart

OrderDateRangeEnd

FetchOnlyChangedSince

IncludeOpenOrders

IncludeInvoicedOrders

IncludeCanceledOrders

ChunkStartPointer

RecordFetchLimit

Optional Inputs

SearchBy

SearchValue

ShipToSequence

Notes

This method can return the list of credit memos at a sold-to or ship-to level depending on the value in ShipToSequence. Specify 0 as the ShipToSequence to return credit memos for the sold-to

The method allows the user to search for and select items based on SearchBy or to request the information for all items. Please see the SearchBy topic for more information

This method allows a user to request a specific number of records. Please see the Data chunking topic for more information

Because the number of records to be returned based on the search criteria could be large, DMSi recommends using the chunking feature, especially when requesting the list at a sold-to level

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Valid values for CustomerID come from CustomersList or CustomerShiptoList

Valid values for ShipToSequence come from GetCustomerShiptos

Valid values for SearchBy are Order ID and Customer PO

This method has a Parent/Child relationship between dtCreditMemo and dtCreditMemoDetail through OrderID. This can be a one-to-many relationship.

A one-to-many Parent/Child relationship exists between dtCreditMemo and dtCreditMemoHeaderNote through OrderID.

A one-to-many Parent/Child relationship exists between dtCreditMemo and dtCreditMemoHeaderMessage through OrderID.

A one-to-many Parent/Child relationship exists between dtCreditMemoDetail and dtCreditMemoDetailMessage through Sequence.

Version Deployed
v539

**Request body:**
```json
{
    "request": {
        "SearchBy": "",
        "SearchValue": "",
        "CustomerID": "",
        "ShipToSequence": 1,
        "OrderDateRangeStart": "2022-06-30",
        "OrderDateRangeEnd": "2022-06-30",
        "FetchOnlyChangedSince": "2022-06-30",
        "IncludeOpenOrders": true,
        "IncludeInvoicedOrders": true,
        "IncludeCanceledOrders": true,
        "ChunkStartPointer": 0,
        "RecordFetchLimit": 0
    }
}
```

## CreditMemoMessageCreate
`POST /Orders/CreditMemoMessageCreate`

Purpose
Creates a credit memo transaction message in the branch the user is logged into
Required Inputs

TranID

MessageText

MessageType

TranSeq (for detail transaction messages)

Optional Inputs

PrintOnForms

Notes

MessageText can send a maximum of 1000 characters

Valid values for MessageType are H, Header, D, Detail, F, and Footer

When PrintOnForms is set to true, all eligible forms are set to print the new message

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v554

**Request body:**
```json
{
    "request": {
        "MessageCreateJSON": {
            "dsMessageCreate": {
                "dtMessageCreate": [
                    {
                        "TranID": 0,
                        "TranSeq": null,
                        "MessageText": "",
                        "MessageType": "",
                        "PrintOnForms": true
                    }
                ]
            }
        }
    }
}
```

## CreditMemoUpdate
`POST /Orders/CreditMemoUpdate`

Purpose
Updates the Expected Pick-Up date for an RMA credit memo
Required Inputs

OrderID

Optional Inputs

ExpectedPickUp

Notes

This method allows the Expected Pick-Up date to be updated on credit memos flagged as RMA. The OrderID and ExpectedPickUp tags must be supplied to successfully update the Expected Pick-Up date on a credit memo.

API will fail if OrderID is not flagged as an RMA or if OrderID is cancelled or invoiced.

A warning will be returned if the ExpectedPickUp value is a past date.

If a blank value is sent for the ExpectedPickUp tag, the existing date will be cleared on the credit memo.

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v613

**Request body:**
```json
{
    "request": {
        "OrderID": 0,
        "CreditMemoUpdateJSON": {
            "dsCreditMemoHeaderUpdate": {
                "dtCreditMemoHeaderUpdate": [
                    {
                        "ExpectedPickUp": "2024-12-24"
                    }
                ]
            }
        }
    }
}
```

## CustomerOrderPadAdd
`POST /Orders/CustomerOrderPadAdd`

Purpose
Creates a new OrderPad detail; if no OrderPad exists for the customer/ship-to, also creates the main OrderPad record
Required Inputs

CustomerID

ItemCode

UOM

PriceUOM for each detail

ShipToSequence

Optional Inputs

Remaining fields dtCustomerOrderPadItems

Notes

ShipToSequence may be required if system is set to allow OrderPad at the ship-to level only.

OrderPad details can be created with 0 OrderQty.

Sequence value can be 0 for each line being added. Processing logic will assign the proper sequence to each line as it is created.

If adding a dimension record, values for Thickness, Width, and/or Length are required based on item type.

ShipToSequence may be required if system is set to allow OrderPad at the ship-to level only. You can enter zero for the ShipToSequence to add records at the sold-to level.

OrderPad details can be created with 0 OrderQty.

Sequence value can be 0 for each line being added. Processing logic will assign the proper sequence to each line as it is created.

The E-commerce sale type defined for the ship-to record is assigned to the OrderPad. You can override this by entering a different sale type in the SaleType field.

The price level defined for the related bill-to record is assigned. You can override with by entering a different value in the PriceLevel field.

Inventory Selling Min Pack and Min Pak Violation settings do not apply. Quantities do not automatically adjust to the selling min pack and the broken min pack flag is not set.

You can override prices and price UOMs on detail lines. Only the UOMs associated with an item can be entered. For dimensional items with unique pricing by dimension, the overridden price is entered on the dimension and each dimension must be on a separate line. Add-on charges included in the price and discounts will not be applied to the overridden price. The price and price UOM are flagged as overridden once the OrderPad is submitted.

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Valid values for CustomerID come from CustomersList or CustomerShiptoList.

Valid values for ShipToSequence come from CustomerShiptoList.

After adding details to an OrderPad, use the CustomerOrderPadList method with the CustomerID and ShipToSequence, as required, to see the full OrderPad.

Version Deployed
v539

**Request body:**
```json
{
    "request": {
        "CustomerID": "",
        "ShipToSequence": 1,
        "dsOrderPadItemsRequest": {
            "dtOrderPadItemsRequest": [
                {
                    "Sequence": 1,
                    "ItemCode": "",
                    "Thickness": 0,
                    "Width": 0,
                    "Length": 0,
                    "OrderQty": 0,
                    "UOM": "",
                    "Price": 0,
                    "PriceUOM": "",
                    "PriceLevel": 0,
                    "SaleType": "",
                    "ItemMessage": "",
                    "OrderedBy": ""
                }
            ]
        }
    }
}
```

## CustomerOrderPadDelete
`POST /Orders/CustomerOrderPadDelete`

Purpose
Deletes an existing OrderPad detail; if this is the only OrderPad detail remaining on this OrderPad, the main OrderPad record is also deleted
Required Inputs

CustomerID

Sequence for each detail to delete

Optional Inputs

ShipToSequence

Notes

ShipToSequence may be required if system is set to allow OrderPad at the ship-to level only. You can enter zero for the ShipToSequence to add records at the sold-to level.

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

To get the list of valid Sequences available for deleting, use CustomerOrderPadList to see the Sequence values used and which ItemCode each is tied to. Sequence is the output that matches the Sequence input. DMSi recommends carefully choosing the Sequence to delete by reviewing related data for each Sequence detail as an ItemCode can exist on an OrderPad multiple times, including individual entries for dimensions.

After deleting details from an OrderPad, use the CustomerOrderPadList method with the CustomerID and ShipToSequence, if necessary, to see the full OrderPad

Version Deployed
v539

**Request body:**
```json
{
    "request": {
        "CustomerID": "",
        "ShipToSequence": 1,
        "dsOrderPadItemsRequest": {
            "dtOrderPadItemsRequest": [
                {
                    "Sequence": 1
                }
            ]
        }
    }
}
```

## CustomerOrderPadList
`POST /Orders/CustomerOrderPadList`

Purpose
Returns an existing OrderPad for a specific customer
Required Inputs

CustomerID

ShipToSequence

Optional Inputs

N/A

Notes

ShipToSequence may be required if system is set to allow OrderPad at the ship-to level only. You can enter zero for the ShipToSequence to add records at the sold-to level.

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Valid values for CustomerID come from CustomersList or CustomerShiptoList

Valid values for ShipToSequence come from CustomerShiptoList

This method should be used to find the correct inputs for and to verify the processing of the other CustomerOrderPad methods available in this service

Version Deployed
v539

**Request body:**
```json
{
    "request": {
        "CustomerID": "",
        "ShipToSequence": 1
    }
}
```

## CustomerOrderPadUpdate
`POST /Orders/CustomerOrderPadUpdate`

Purpose
Updates an existing OrderPad detail
Required Inputs

CustomerID

Sequence

ItemCode for each detail to update

ShipToSequence

Optional Inputs

Remaining fields dtCustomerOrderPadItems (depending on what needs to be updated)

Notes

ShipToSequence may be required if system is set to allow OrderPad at the ship-to level only

Setting the ShipToSequence for zero updates the OrderPad at the sold-to level

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

After updating details from an OrderPad, use the CustomerOrderPadList method with the CustomerID and ShipToSequence, if necessary, to see the full OrderPad

To get the list of valid Sequences available for updating, use CustomerOrderPadList to see the Sequence values used and which ItemCode each is tied to. DMSi recommends carefully choosing the Sequence to update by reviewing related data for each Sequence detail as an ItemCode can exist on an OrderPad multiple times, including individual entries for dimensions

Version Deployed
v539

**Request body:**
```json
{
    "request": {
        "CustomerID": "",
        "ShipToSequence": 1,
        "OrderPadUpdateJSON": {
            "dsCustomerOrderPadItemsRequest": {
                "dtCustomerOrderPadItemsRequest": [
                    {
                        "Sequence": 1,
                        "ItemCode": "",
                        "Thickness": 0,
                        "Width": 0,
                        "Length": 0,
                        "OrderQty": 0,
                        "UOM": "",
                        "Price": 0,
                        "PriceUOM": "",
                        "SaleType": "",
                        "ItemMessage": "",
                        "OrderedBy": ""
                    }
                ]
            }
        }
    }
}
```

## QuicklistList
`POST /Orders/QuicklistList`

Purpose
Returns existing quick lists with a quicklist type of 'Sales' for a specific customer
Required Inputs

CustomerID

ShipToSequence

Optional Inputs

N/A

Notes

Quicklists can be created at the sold-to (ShipToSequence = 0) or ship-to (ShipToSequence <> 0) level for a customer

BOM parent items are excluded from the quicklist response, unless set as an Auto complete WO

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

There is a Parent/Child relationship in this method. dtQuickListHeader is tied to dtQuickListItem via the QuickList field. There can be a one to many relationship between these outputs

Valid values for CustomerID come from CustomersList or CustomerShiptoList

Valid values for ShipToSequence come from CustomerShiptoList

Version Deployed
v539

**Request body:**
```json
{
    "request": {
        "CustomerID": "",
        "ShipToSequence": 1
    }
}
```

## QuicklistPriceandAvailList
`POST /Orders/QuicklistPriceandAvailList`

Purpose
Returns existing quick lists with a quicklist type of 'Sales' for a specific customer with price and availability information
Required Inputs

CustomerID

ShipToSequence

Optional Inputs

N/A

Notes

Quicklists can be created at the sold-to (ShipToSequence = 0) or ship-to (ShipToSequence <> 0) level for a customer

BOM parent items are excluded from the quicklist response, unless set as an Auto complete WO

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

The QuickList field reflects to which quick list the items returned are related

The difference between this method and QuicklistList is in the data returned. The structure is a bit difference and this method returns price and availability information for the quick list items

Valid values for CustomerID come from CustomersList or CustomerShiptoList

Valid values for ShipToSequence come from CustomerShiptoList

Version Deployed
v539

**Request body:**
```json
{
    "request": {
        "CustomerID": "",
        "ShipToSequence": 1
    }
}
```

## QuoteCreate
`POST /Orders/QuoteCreate`

Purpose
Creates a new quote
Required Inputs

CustomerID

ShiptoSequence

ItemCode

OrderQty

UOM for each detail record

Optional Inputs

Remaining fields in the dtQuoteHeaderRequest, dtOrderItemRequest, or dtOrderItemDimensionRequest not already referenced

Notes

ContextId comes from Login

Valid values for SaleType come from SaleTypesList

Valid values for ItemCode and related Thickness, Width and Length come from ItemsList or ItemsInChunksList

Valid values for CustomerID come from CustomersList or CustomerShiptoList

Valid values for ShiptoSequence come from CustomerShiptoList

RequestedDeliveryDate in the QuoteCreate request can be seen in ExpectedDate from the QuoteList response

This method contains a parent/child relationship between dtOrderItemRequest and dtOrderItemDimensionRequest. Please see the Parent/Child relationship topic for more information

dtOrderItemDimensionRequest must be included in the request even if the item is not a dimensional item

If any of the ship-to address tags are sent in with a value, the system clears out the other ship-to address fields instead of using the default values. For example, if you send in a value in only the ShipToAddress1 tag, the city and state on the newly created Quote will be blank. If you override a ship-to address, you must send in all relevant ship-to address tags. The tags included in the ship-to address fields are as follows: ShipToName, ShipToAddress1, ShipToAddress2, ShipToAddress3, ShipToCity, ShipToState, ShipToZip, ShipToCountry, ShipToPhone.

If all ship-to address tags have a value of blank, or none of them are sent in the request, then the system uses the default ship-to address values.

If UseItemConvertPriceAndUOM = true, the process converts the price and price UOM to the order qty UOM if all the following criteria are met:

PriceOverride = false

Convert price/price UOM to match order field on the item record is set in Agility

The UOM sent in the dtOrderItemRequest does not match the SO/Quote UOM on the item record in Agility

This method allows customer charges and order costs to be added to the quote. If either Charge = True or OrderCost = True in the dtOrderItemRequest, then the ItemCode value must correspond to a valid Charge type or Cost type in Agility, and the Price is the amount applied to the order. All other tags in the dtOrderItemRequest are ignored.

You can only add customer charges and order costs with the record type of header charge, header charge allocated to detail, header charge calculated by item detail, or header cost.

The customer charge or order cost is added with a fixed amount basis.

If the Price is greater than or equal to 0, then the customer charge or order cost applies as a Charge or Cost, respectively.

If the Price is less than 0, then the customer charge or order cost applies as a Refund or Cost Reduction, respectively.

The AddPermanentDetailGroupID tag determines if a permanent detail group record is created for the detail group received in the request.

DepartmentName, DepartmentNumber, APIPriceSourceType, and APIPriceSourceRef, while displayed as inputs, are not operational for this method and are reserved for future use.

The ‘Require Template for Non-Stock’ security action will not be read

If a value is sent in both the ItemCode and TemplateItemCode tags

ItemCode value will not be read

TemplateItemCode value will be read and used to create a non-stock item

TemplateItemCode value must be active, saleable, no order restrictions, and not a BOM parent item

If any of the following tags are not sent or sent with a blank value, values assigned to the TemplateItemCode sent in the API will be used when creating the non-stock item

NonStockSize

NonStockDescription

NonStockExtDescription

NonStockProductGroupMajor

NonStockProductGroupMinor

NonStockPriceCodeMajor

NonStockPriceCodeMinor

NonStockCost

NonStockCostUOM

If a value is sent for the NonStockProductGroupMajor tag, then a value must also be sent for the NonStockProductGroupMinor tag; the reciprocal is also true

If a value is sent for the NonStockPriceCodeMajor tag, then a value must also be sent for the NonStockPriceCodeMinor tag; the reciprocal is also true

If a value is sent for the NonStockCost tag, then a value must also be sent for the NonStockCostUOM tag; the reciprocal is also true

A Quotation form for the created quote is sent to the emails provided in the AcknowledgementEmailAddress and AcknowledgementEmailAddress2 tags or the fax number provided in the AcknowledgementFaxNumber tag. If none of the tags are populated, a Quotation form is not sent.

Relationships

ContextId and Branch come from Login

Version Deployed
v552

**Request body:**
```json
{
    "request": {
        "QuoteHeaderJSON": {
            "dsQuoteHeaderRequest": {
                "dtQuoteHeaderRequest": [
                    {
                        "CustomerID": "",
                        "ShipToSequence": 1,
                        "SaleType": "",
                        "RequestedDeliveryDate": "",
                        "TransactionReference": "",
                        "TransactionJob": "",
                        "OrderedBy": "",
                        "CustomerPO": "",
                        "AcknowledgementEmailAddress": "",
                        "AcknowledgementEmailAddress2": "",
                        "AcknowledgementFaxNumber": "",
                        "ShipToName": "",
                        "ShipToAddress1": "",
                        "ShipToAddress2": "",
                        "ShipToAddress3": "",
                        "ShipToCity": "",
                        "ShipToState": "",
                        "ShipToZip": "",
                        "ShipToCountry": "",
                        "ShipToPhone": "",
                        "OrderMessage": "",
                        "ShipVia": "",
                        "ActivationDate": "",
                        "CloseDate": "",
                        "ExternalSource": "",
                        "ExternalProjectID": "",
                        "SourceLogin": ""
                    }
                ],
                "dtQuoteHeaderNotesRequest": [
                    {
                        "OrderNote": "",
                        "HotNote": true
                    },
                    {
                        "OrderNote": "",
                        "HotNote": false
                    }
                ]
            }
        },
        "OrderItemJSON": {
            "dsOrderItemRequest": {
                "dtOrderItemRequest": [
                    {
                        "Sequence": 1,
                        "ItemCode": "",
                        "OrderQty": 0,
                        "UOM": "",
                        "Charge": false,
                        "Price": 0,
                        "PriceUOM": "",
                        "PriceOverride": false,
                        "UseItemConvertPriceAndUOM": false,
                        "OrderCost": false,
                        "CustomerPOLineNumber": "",
                        "DepartmentName": "",
                        "DepartmentNumber": "",
                        "PartNumber": "",
                        "SKU": "",
                        "UPCCode": "",
                        "ItemMessage": "",
                        "PrintMsgOnForms": false,
                        "PrintMsgOnFormsOverride": false,
                        "SendMsgToWMS": false,
                        "SendMsgToWMSOverride": false,
                        "APIPriceSourceType": "",
                        "APIPriceSourceRef": "",
                        "ShippingBranch": "",
                        "DetailGroupID": "",
                        "AddPermanentDetailGroupID": false,
                        "UseGroupAsDefaultNewItems": false,
                        "TemplateItemCode": "",
                        "NonStockSize": "",
                        "NonStockDescription": "",
                        "NonStockExtDescription": "",
                        "NonStockCopyCustomFields": true,
                        "NonStockSupplierID": "",
                        "NonStockSupplierShipFromSequence": 1,
                        "NonStockSupplierPartNumber": "",
                        "NonStockProductGroupMajor": "",
                        "NonStockProductGroupMinor": "",
                        "NonStockPriceCodeMajor": "",
                        "NonStockPriceCodeMinor": "",
                        "NonStockCost": 0,
                        "NonStockCostUOM": ""
                    },
                    {
                        "ItemCode": "",
                        "Charge": true,
                        "Price": 0
                    },
                    {
                        "ItemCode": "",
                        "OrderCost": true,
                        "Price": 0,
                        "OrderCostSupplierID": ""
                    }
                ],
                "dtOrderItemDimensionRequest": [
                    {
                        "Sequence": 0,
                        "Thickness": 0,
                        "Width": 0,
                        "Length": 0,
                        "OrderQty": 0,
                        "UOM": "",
                        "Price": 0,
                        "PriceUOM": "",
                        "PriceOverride": false
                    }
                ]
            }
        }
    }
}
```

## QuoteCreateValidate
`POST /Orders/QuoteCreateValidate`

Purpose
Validates the creation of a new quote order and new items
Required Inputs

CustomerID

ShiptoSequence

ItemCode

OrderQty

Optional Inputs

Remaining fields in the dtQuoteHeaderRequest, dtQuoteHeaderNotesRequest, dtOrderItemRequest, or dtOrderItemDimensionRequest not already referenced

Notes

When the following tags are included in the request a value is required.

Charge

PriceOverride

OrderCost

SendMsgToWMS

SendMsgToWMSOverride

Refer to the Notes in the QuoteCreate method.

Review the dsAuditResults to identify changes needed in the request in order for the validation to be successful.

The ‘Require Template for Non-Stock’ security action will not be read

If a value is sent in both the ItemCode and TemplateItemCode tags

ItemCode value will not be read

TemplateItemCode value will be read and used to create a non-stock item

TemplateItemCode value must be active, saleable, no order restrictions, and not a BOM parent item

If any of the following tags are not sent or sent with a blank value, values assigned to the TemplateItemCode sent in the API will be used when creating the non-stock item

NonStockSize

NonStockDescription

NonStockExtDescription

NonStockProductGroupMajor

NonStockProductGroupMinor

NonStockPriceCodeMajor

NonStockPriceCodeMinor

NonStockCost

NonStockCostUOM

If a value is sent for the NonStockProductGroupMajor tag, then a value must also be sent for the NonStockProductGroupMinor tag; the reciprocal is also true

If a value is sent for the NonStockPriceCodeMajor tag, then a value must also be sent for the NonStockPriceCodeMinor tag; the reciprocal is also true

If a value is sent for the NonStockCost tag, then a value must also be sent for the NonStockCostUOM tag; the reciprocal is also true

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Refer to the relationships section in the QuoteCreate method

Version Deployed
v609

**Request body:**
```json
{
    "request": {
        "dsQuoteHeaderRequest": {
            "dtQuoteHeaderRequest": [
                {
                    "CustomerID  ": "",
                    "ShipToSequence": 1,
                    "SaleType": "",
                    "RequestedDeliveryDate": "",
                    "TransactionReference": "",
                    "TransactionJob ": "",
                    "OrderedBy": "",
                    "CustomerPO": "",
                    "AcknowledgementEmailAddress": "",
                    "AcknowledgementEmailAddress2": "",
                    "AcknowledgementFaxNumber": "",
                    "ShipToName ": "",
                    "ShipToAddress1": "",
                    "ShipToAddress2": "",
                    "ShipToAddress3": "",
                    "ShipToCity ": "",
                    "ShipToState": "",
                    "ShipToZip": "",
                    "ShipToCountry": "",
                    "ShipToPhone": "",
                    "OrderMessage": "",
                    "ShipVia": "",
                    "ActivationDate": "",
                    "CloseDate": "",
                    "ExternalSource": "",
                    "ExternalProjectID": "",
                    "SourceLogin": ""
                }
            ],
            "dtQuoteHeaderNotesRequest": [
                {
                    "OrderNote": "",
                    "HotNote": true
                },
                {
                    "OrderNote": "",
                    "HotNote": false
                }
            ]
        },
        "dsOrderItemRequest": {
            "dtOrderItemRequest": [
                {
                    "Sequence": 1,
                    "ItemCode": "",
                    "OrderQty": 0,
                    "UOM": "",
                    "Charge": false,
                    "Price": 0,
                    "PriceUOM": "",
                    "PriceOverride": false,
                    "OrderCost": false,
                    "CustomerPOLineNumber": "",
                    "DepartmentName": "",
                    "DepartmentNumber": "",
                    "PartNumber": "",
                    "SKU": "",
                    "UPCCode": "",
                    "ItemMessage": "",
                    "PrintMsgOnForms": false,
                    "PrintMsgOnFormsOverride": false,
                    "SendMsgToWMS": false,
                    "SendMsgToWMSOverride": false,
                    "APIPriceSourceType": "",
                    "APIPriceSourceRef": "",
                    "DetailGroupID": "",
                    "AddPermanentDetailGroupID": true,
                    "UseGroupAsDefaultNewItems": true,
                    "TemplateItemCode": "",
                    "NonStockSize": "",
                    "NonStockDescription": "",
                    "NonStockExtDescription": "",
                    "NonStockCopyCustomFields": true,
                    "NonStockSupplierID": "",
                    "NonStockSupplierShipFromSequence": 1,
                    "NonStockSupplierPartNumber": "",
                    "NonStockProductGroupMajor": "",
                    "NonStockProductGroupMinor": "",
                    "NonStockPriceCodeMajor": "",
                    "NonStockPriceCodeMinor": "0",
                    "NonStockCost": 0,
                    "NonStockCostUOM": ""
                },
                {
                    "Sequence": 2,
                    "ItemCode": "",
                    "OrderQty": 0,
                    "UOM": "",
                    "Charge": false,
                    "Price": 0,
                    "PriceUOM": "",
                    "PriceOverride": false,
                    "OrderCost": false,
                    "CustomerPOLineNumber": "",
                    "DepartmentName": "",
                    "DepartmentNumber": "",
                    "PartNumber": "",
                    "SKU": "",
                    "UPCCode": "",
                    "ItemMessage": "",
                    "PrintMsgOnForms": false,
                    "PrintMsgOnFormsOverride": false,
                    "SendMsgToWMS": false,
                    "SendMsgToWMSOverride": false,
                    "APIPriceSourceType": "",
                    "APIPriceSourceRef": "",
                    "DetailGroupID": "",
                    "AddPermanentDetailGroupID": false,
                    "UseGroupAsDefaultNewItems": true
                },
                {
                    "Sequence": 3,
                    "ItemCode": "",
                    "OrderQty": 0,
                    "UOM": "",
                    "Charge": false,
                    "Price": 0,
                    "PriceUOM": "",
                    "PriceOverride": false,
                    "OrderCost": false,
                    "CustomerPOLineNumber": "",
                    "DepartmentName": "",
                    "DepartmentNumber": "",
                    "PartNumber": "",
                    "SKU": "",
                    "UPCCode": "",
                    "ItemMessage": "",
                    "PrintMsgOnForms": false,
                    "PrintMsgOnFormsOverride": false,
                    "SendMsgToWMS": false,
                    "SendMsgToWMSOverride": false,
                    "APIPriceSourceType": "",
                    "APIPriceSourceRef": "",
                    "DetailGroupID": "Foundation",
                    "AddPermanentDetailGroupID": false,
                    "UseGroupAsDefaultNewItems": false
                },
                {
                    "ItemCode": "",
                    "Charge": true,
                    "Price": 0
                },
                {
                    "ItemCode": "",
                    "OrderCost": true,
                    "Price": 0,
                    "OrderCostSupplierID": ""
                }
            ],
            "dtOrderItemDimensionRequest": [
                {
                    "Sequence": 0,
                    "Thickness": 0,
                    "Width": 0,
                    "Length": 0,
                    "OrderQty": 0,
                    "UOM": "",
                    "Price": 0,
                    "PriceUOM": "0",
                    "PriceOverride": false
                }
            ]
        }
    }
}
```

## QuoteDelete
`POST /Orders/QuoteDelete`

Purpose
Deletes an existing quote
Required Inputs

QuoteID

Value Required

The following inputs require a value due to data type:

QuoteDateRangeStart

QuoteDateRangeEnd

IncludeOnlyOpenQuotes

ChunkStartPointer

RecordFetchLimit

Optional Inputs

DeleteReleasedQuote

Notes

If the value for DeleteReleasedQuote is not specified, the default is set to false. The value must be set as true to delete a quote with released line items.

Relationships

ContextId and Branch come from Login

Version Deployed
v549

**Request body:**
```json
{
    "request": {
        "QuoteID": 0,
        "DeleteReleasedQuote": true
    }
}
```

## QuoteDetailsDelete
`POST /Orders/QuoteDetailsDelete`

Purpose
Deletes an existing quote detail record
Required Inputs

OrderID

Sequence

Optional Inputs

N/A

Notes

The value in the DeleteReleasedDetail tag determines if line items with quantity released can be deleted.

Valid values are true and false

If the tag is not sent in the request, details with quantity released will not be deleted

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Quote details come from QuoteList

Version Deployed
v610

**Request body:**
```json
{
    "request": {
        "OrderID": 0,
        "DeleteReleasedDetails": true,
        "QuoteDetailsDeleteJSON": {
            "dsOrderItemRequest": {
                "dtOrderItemRequest": [
                    {
                        "Sequence": 1
                    },
                    {
                        "Sequence": 2
                    }
                ]
            }
        }
    }
}
```

## QuoteDetailsUpdate
`POST /Orders/QuoteDetailsUpdate`

Purpose
Updates an existing quote detail record
Required Inputs

OrderID

Sequence

Optional Inputs

OrderQty

UOM

UseItemConvertPriceAndUOM

Price

PriceUOM

PriceOverride

DetailGroupID

AddPermanentDetailGroupID

UseGroupAsDefaultNewItems

Notes

The item being updated must meet the following criteria in order to be successfully updated:

Item is allowed in the API

Item is not discontinued

Item is not a template item

If updating a dimension on an item, Thickness, Width, and/or Length are required based on the item type. If the existing item has tallies specified, dimension information must be sent in through dtOrderItemDimensionRequest. In addition, the OrderQty and UOM must be specified at the dimension level. Use the PieceCount field when OrderQty has a value of “UNIT”. Sheet Good item types will require the Width and Length to match existing item.

If UseItemConvertPriceAndUOM = 'true', the process converts the price and price UOM to the order qty UOM if all the following criteria are met:

Convert price/price UOM to match order field on the item record is set in Agility

The UOM sent in the dtOrderItemRequest does not match the Quote UOM on the item record in Agility

If PriceOverride = 'false', no updates will be made to the detail price even if Price and PriceUOM values are sent

If PriceSubjectToFurtherDiscounts = 'true', and the detail being updated had discounts applied before, the discounts will continue to be applied after the update; if value = 'false', the discounts will be updated to zero

If the existing detail has pricing by dimension and ApplyPriceToAllDimensions = 'true', the price on the dimensions will be updated with the Price value sent; if value = 'false', the item update will fail

Item update fails if updating Price for a detail group header item with the ‘Price Detail Items only’ option set

Item update fails if updating Price for a non-detail group header item that has a detail group assigned and the group header for that group has the Pricing flag set to ‘Price Header Item only’

If PriceOveride = 'false', no price updates are made to the quote detail even if Price and PriceUOM values are included

DMSi strongly recommends reviewing dsAuditResults regardless of the ReturnCode value

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Quote details come from QuoteList

Valid values for a sequence’s thickness, width, and length come from ItemList or ItemsInChunksList

This method contains a parent/child relationship between the dtOrderItemRequest and dtOrderItemDimensionRequest. Please see Parent/Child relationship topic for more information.

Version Deployed
v610

**Request body:**
```json
{
    "request": {
        "OrderID": 0,
        "QuoteDetailsUpdateJSON": {},
        "dsOrderItemRequest": {
            "dtOrderItemRequest": [
                {
                    "Sequence": 1,
                    "OrderQty": 0,
                    "UOM": "",
                    "UseItemConvertPriceAndUOM": false,
                    "Price": 0,
                    "PriceUOM": "",
                    "ApplyPriceToAllDimensions": true,
                    "PriceSubjectToFurtherDiscounts": false,
                    "PriceOverride": true,
                    "DetailGroupID": "",
                    "AddPermanentDetailGroupID": true,
                    "UseGroupAsDefaultNewItems": false,
                    "dtOrderItemDimensionRequest": [
                        {
                            "Sequence": 1,
                            "Thickness": 0,
                            "Width": 0,
                            "Length": 0,
                            "PieceCount": 0,
                            "OrderQty": 0,
                            "UOM": ""
                        }
                    ]
                }
            ]
        }
    }
}
```

## QuoteList
`POST /Orders/QuoteList`

Purpose
Returns a list of quotes for a specified customer
Required Inputs

CustomerID

Value Required

The following inputs require a value due to data type:

QuoteDateRangeStart

QuoteDateRangeEnd

IncludeOnlyOpenQuotes

ChunkStartPointer

RecordFetchLimit

Optional Inputs

ShipToSequence

Notes

This method can return the list of quotes at a sold-to or ship-to level depending on the value in ShipToSequence. Specify 0 as the ShipToSequence to return quotes orders for the sold-to

A value of < all > can be specified in CustomerID (Note: Do not include spaces between the characters and the word "all" when including this in the request.)

A value must also be specified in SearchBy and SearchValue

Specify 0 as the ShipToSequence

This method allows a user to request a specific number of records. Please see the Chunking topic for more information

Because the number of records to be returned based on the search criteria could be large, DMSi recommends using the chunking feature, especially when requesting the list at a sold-to level

Valid values for SearchBy:

Order ID

Quote ID

Customer PO

Reference #

Job #

External Source

External Project ID

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Valid values for CustomerID come from CustomersList or CustomerShiptoList

Valid values for ShipToSequence come from CustomerShiptoList

A one-to-many Parent/Child relationship exists between dtQuoteResponse and dtQuoteDetailResponse through QuoteID

A one-to-many Parent/Child relationship exists between dtQuoteResponse and dtQuoteHeaderNote through QuoteID

A one-to-many Parent/Child relationship exists between dtQuoteResponse and dtQuoteHeaderMessage through QuoteID

A one-to-many Parent/Child relationship exists between dtQuoteDetailResponse and dtQuoteDetailMessage through Sequence

Version Deployed
v539

**Request body:**
```json
{
    "request": {
        "SearchBy": "",
        "SearchValue": "",
        "CustomerID": "",
        "ShipToSequence": 1,
        "IncludeOnlyOpenQuotes": false,
        "ChunkStartPointer": "",
        "RecordFetchLimit": ""
    }
}
```

## QuoteMessageCreate
`POST /Orders/QuoteMessageCreate`

Purpose
Creates a quote transaction message in the branch the user is logged into
Required Inputs

TranID

MessageText

MessageType

TranSeq (for detail transaction messages)

Optional Inputs

PrintOnForms

SendToWMS

Notes

MessageText can send a maximum of 1000 characters

Valid values for MessageType are H, Header, D, Detail, F, and Footer

When PrintOnForms is set to true, all eligible forms are set to print the new message

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v554

**Request body:**
```json
{
    "request": {
        "MessageCreateJSON": {
            "dsMessageCreate": {
                "dtMessageCreate": [
                    {
                        "TranID": 0,
                        "ShipmentNum": 1,
                        "TranSeq": 1,
                        "MessageText": "",
                        "MessageType": "",
                        "PrintOnForms": true,
                        "SendToWMS": false
                    }
                ]
            }
        }
    }
}
```

## QuotePriceHoldApprove
`POST /Orders/QuotePriceHoldApprove`

Purpose
Removes quote items from price hold; approve items on price hold based of the QuoteID and detail line item Sequence
Required Inputs

QuoteID

Sequence

Optional Inputs

SendNotification

ReviewerID

Comment

Notes

To get the list of valid Sequences available for updating, use QuoteList to see the Sequence values used and which ItemCode each is tied to. DMSi recommends carefully choosing the Sequence to update by reviewing related data for each Sequence detail as an ItemCode can exist multiple times on a Quote, including individual entries for dimensions

A Price Hold Approval/Rejection Notification must be defined in Agility to send a notification

Comment and ReviewerID are populated on the notification

When the ReviewerID value matches a User ID in Agility, the Reviewer User Name on the notification is populated with the User Name value from the user record

If the ReviewerID value does not match a User ID in Agility, the Reviewer User Name on the notification is blank

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Valid values for QuoteID come from QuoteList

Version Deployed
v539

**Request body:**
```json
{
    "request": {
        "QuoteID": 0,
        "QuoteDetailApproveJSON": {
            "dsQuoteDetail": {
                "dtQuoteDetail": [
                    {
                        "Sequence": 1,
                        "SendNotification": "",
                        "ReviewerID": "",
                        "Comment": ""
                    },
                    {
                        "Sequence": 2,
                        "SendNotification": ""
                    },
                    {
                        "Sequence": 3,
                        "SendNotification": "",
                        "ReviewerID": "",
                        "Comment": ""
                    },
                    {
                        "Sequence": 4,
                        "SendNotification": "",
                        "ReviewerID": "",
                        "Comment": ""
                    }
                ]
            }
        }
    }
}
```

## QuotePriceHoldReject
`POST /Orders/QuotePriceHoldReject`

Purpose
Denies removal of quote items from price hold based on the QuoteID and detail line item Sequence and sends a suggested price for approval
Required Inputs

QuoteID

Sequence

Optional Inputs

QuoteID

Sequence

Notes

To get the list of valid Sequences available for updating, use QuoteList to see the Sequence values used and which ItemCode each is tied to. DMSi recommends carefully choosing the Sequence to update by reviewing related data for each Sequence detail as an ItemCode can exist multiple times on a Quote, including individual entries for dimensions

Include a SuggestedPrice that would allow approval of the item

A Price Hold Approval/Rejection Notification must be defined in Agility to send a notification

Comment and ReviewerID are populated on the notification

When the ReviewerID value matches a User ID in Agility, the Reviewer User Name on the notification is populated with the User Name value from the user record

If the ReviewerID value does not match a User ID in Agility, the Reviewer User Name on the notification is blank

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Valid values for QuoteID come from QuoteList

Version Deployed
v550

**Request body:**
```json
{
    "request": {
        "QuoteID": 0,
        "QuoteDetailRejectJSON": {
            "dsQuoteDetail": {
                "dtQuoteDetail": [
                    {
                        "Sequence": 1,
                        "SuggestedPrice": 0,
                        "SuggestedPriceUOM": "",
                        "SendNotification": "",
                        "ReviewerID": "",
                        "Comment": ""
                    },
                    {
                        "Sequence": 2,
                        "SuggestedPrice": 0,
                        "SuggestedPriceUOM": "",
                        "SendNotification": "",
                        "ReviewerID": "",
                        "Comment": ""
                    }
                ]
            }
        }
    }
}
```

## QuoteRelease
`POST /Orders/QuoteRelease`

Purpose
Fully or partially release an active/open quote to a sales order
Required Inputs

OrderID

ReleaseRule - 'Release full quote' or 'Release by item'

Optional Inputs

Remaining fields in dtQuoteReleaseSettingsRequest, dtQuoteReleaseItemRequest, and dtQuoteReleaseDimRequest not already referenced

Notes

Processes not allowed with this method

Releasing by Detail Group ID

Creating separate sales orders for each quote detail

Negative quantities

Security action ‘Release Items From Price Hold’ is read for this method

If granted, price hold items are automatically approved on the sales order

If denied, price hold status is copied from the quote to the sales order

API will fail if sales order value sent in the AppendSalesOrderID tag is invoiced or canceled

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Valid values for OrderID come from QuoteList

Valid values for AppendSalesOrderID come from SalesOrderList

This method contains a parent/child relationship between the dtQuoteReleaseItemRequest and dtQuoteReleaseDimRequest. Please see the Parent/Child relationship topic for more information.

Version Deployed
v610

**Request body:**
```json
{
    "request": {
        "QuoteReleaseJSON": {
            "dsQuoteReleaseSettingsRequest": {
                "dtQuoteReleaseSettingsRequest": [
                    {
                        "OrderID": 0,
                        "ReleaseRule": "",
                        "AppendSalesOrderID": 0,
                        "SaleType": "",
                        "CombineLikeItems": true,
                        "RecalculateOverriddenExpDate": true
                    }
                ]
            },
            "dsQuoteReleaseItemRequest": {
                "dtQuoteReleaseItemRequest": [
                    {
                        "Sequence": 1,
                        "ReleaseQuantity": 2,
                        "ReleaseUOM": "",
                        "dtQuoteReleaseItemDimRequest": [
                            {
                                "Sequence": 1,
                                "Thickness": 0,
                                "Width": 0,
                                "Length": 0,
                                "ReleaseQuantity": 0,
                                "ReleaseUOM": "",
                                "PieceCount": 0
                            },
                            {
                                "Sequence": 1,
                                "Thickness": 0,
                                "Width": 0,
                                "Length": 0,
                                "ReleaseQuantity": 0,
                                "ReleaseUOM": "",
                                "PieceCount": 0
                            }
                        ]
                    },
                    {
                        "Sequence": 2,
                        "ReleaseQuantity": 0,
                        "ReleaseUOM": ""
                    },
                    {
                        "Sequence": 3,
                        "ReleaseQuantity": 0,
                        "ReleaseUOM": ""
                    }
                ]
            }
        }
    }
}
```

## QuoteUpdate
`POST /Orders/QuoteUpdate`

Purpose
Updates header information and/or adds new items to an existing quote
Required Inputs

OrderID

Value Required

The following inputs require a value due to data type:

Charge

PriceOverride

OrderCost

PrintMsgOnForms

PrintMsgOnFormsOverride

SendMsgToWMS

SendMsgToWMSOverride

Optional Inputs

All fields in dtQuoteHeaderUpdateRequest

Remaining fields in the dtOrderItemRequest, or dtOrderItemDimensionRequest not already referenced

Notes

This method allows specific fields on the quote header to be updated

This method allows new items to be added to an existing quote. Existing items may not be updated or deleted by this method.

Each new detail must have OrderQty > 0

If UseItemConvertPriceAndUOM = true, the process converts the price and UOM to the order qty UOM if all the following criteria are met:

PriceOverride = false

Convert price/price UOM to match order field on the item record is set in Agility

The UOM sent in the dtOrderItemRequest does not match the SO/Quote UOM on the item record in Agility

When ordering by dimension, values for Thickness, Width, and/or Length are required based on item type. In addition, the OrderQty and UOM must also be specified at the dimension level

If the ShipVia value sent in is invalid, the entire request fails and no updates are completed

Use the PartNumber field if the item being ordered is a customer part number. When populated the PartNumber is read first before the ItemCode using the following search hierarchy.

Search the item cross reference hierarchy for a match to the PartNumber submitted in the request. If a match is found the quote detail item cross reference field is populated with the PartNumber value.

Search the item cross reference hierarchy for a match to the ItemCode submitted in the API request. If a match is found the sales order detail item cross reference field is populated with the ItemCode value.

Search for a valid Agility item code that matches the ItemCode submitted in the API request.

Search for a valid Agility item code that matches the PartNumber submitted in the API request.

This method allows customer charges and order costs to be added or updated on an existing quote. If either Charge = True or OrderCost = True in the dtOrderItemRequest, then the ItemCode value must correspond to a valid Charge type or Cost type in Agility, and the Price is the amount applied to the quote. All other tags in the dtOrderItemRequest are ignored.

You can only add or update customer charges and order costs with the record type of header charge, header charge allocated to detail, header charge calculated by item detail, or header cost.

The customer charge or order cost is added or updated with a fixed amount basis.

If the Price is greater than or equal to 0, then the customer charge or order cost applies as a Charge or Cost, respectively.

If the Price is less than 0, then the customer charge or order cost applies as a Refund or Cost Reduction, respectively.

The ‘Require Template for Non-Stock’ security action will not be read

If a value is sent in both the ItemCode and TemplateItemCode tags

ItemCode value will not be read

TemplateItemCode value will be read and used to create a non-stock item

TemplateItemCode value must be active, saleable, no order restrictions, and not a BOM parent item

If any of the following tags are not sent or sent with a blank value, values assigned to the TemplateItemCode sent in the API will be used when creating the non-stock item

NonStockSize

NonStockDescription

NonStockExtDescription

NonStockProductGroupMajor

NonStockProductGroupMinor

NonStockPriceCodeMajor

NonStockPriceCodeMinor

NonStockCost

NonStockCostUOM

If a value is sent for the NonStockProductGroupMajor tag, then a value must also be sent for the NonStockProductGroupMinor tag; the reciprocal is also true

If a value is sent for the NonStockPriceCodeMajor tag, then a value must also be sent for the NonStockPriceCodeMinor tag; the reciprocal is also true

If a value is sent for the NonStockCost tag, then a value must also be sent for the NonStockCostUOM tag; the reciprocal is also true

To update header information only, exclude the dtOrderItemRequest and dtOrderItemDimensionRequest data tables from the request

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Valid values for OrderID come from QuoteList or from NewOrderID returned from QuoteCreate

This method contains a parent/child relationship between the dtOrderItemRequest and dtOrderItemDimensionRequest. Please see the Parent/Child relationship topic for more information.

Version Deployed
v609

**Request body:**
```json
{
    "request": {
        "OrderID": 0,
        "QuoteHeaderUpdateJSON": {
            "dsQuoteHeaderUpdateRequest": {
                "dtQuoteHeaderUpdateRequest": [
                    {
                        "TransactionReference": "",
                        "TransactionJob": "",
                        "OrderedBy": "",
                        "CustomerPO": "",
                        "ShipVia": "",
                        "RequestedDeliveryDate": "",
                        "ActivationDate": "",
                        "CloseDate": "",
                        "ExternalSource": "",
                        "ExternalProjectID": ""
                    }
                ]
            }
        },
        "OrderItemUpdateJSON": {
            "dsOrderItemRequest": {
                "dtOrderItemRequest": [
                    {
                        "Sequence": 1,
                        "ItemCode": "",
                        "OrderQty": 0,
                        "UOM": "",
                        "Charge": false,
                        "Price": 0,
                        "PriceUOM": "",
                        "PriceOverride": false,
                        "UseItemConvertPriceAndUOM": false,
                        "OrderCost": false,
                        "CustomerPOLineNumber": "",
                        "DepartmentName": "",
                        "DepartmentNumber": "",
                        "PartNumber": "",
                        "SKU": "",
                        "UPCCode": "",
                        "ItemMessage": "",
                        "PrintMsgOnForms": false,
                        "PrintMsgOnFormsOverride": false,
                        "SendMsgToWMS": false,
                        "SendMsgToWMSOverride": false,
                        "APIPriceSourceType": "",
                        "APIPriceSourceRef": "",
                        "DetailGroupID": "",
                        "AddPermanentDetailGroupID": false,
                        "UseGroupAsDefaultNewItems": true
                    },
                    {
                        "Sequence": 2,
                        "TemplateItemCode": "",
                        "NonStockDescription": " ",
                        "NonStockExtDescription": "",
                        "NonStockCopyCustomFields": true,
                        "NonStockSupplierID": "",
                        "NonStockSupplierShipFromSequence": 0,
                        "NonStockSupplierPartNumber": "",
                        "NonStockProductGroupMajor": "",
                        "NonStockProductGroupMinor": "",
                        "NonStockPriceCodeMajor": "",
                        "NonStockPriceCodeMinor": "",
                        "NonStockCost": 0,
                        "NonStockCostUOM": "",
                        "NonStockSize": "",
                        "OrderQty": 1,
                        "UOM": "",
                        "Charge": false,
                        "Price": 0,
                        "PriceUOM": "",
                        "PriceOverride": false,
                        "UseItemConvertPriceAndUOM": false,
                        "OrderCost": false,
                        "CustomerPOLineNumber": "",
                        "DepartmentName": "",
                        "DepartmentNumber": "",
                        "PartNumber": "",
                        "SKU": "",
                        "UPCCode": "",
                        "ItemMessage": "",
                        "PrintMsgOnForms": false,
                        "PrintMsgOnFormsOverride": false,
                        "SendMsgToWMS": false,
                        "SendMsgToWMSOverride": false,
                        "APIPriceSourceType": "",
                        "APIPriceSourceRef": "",
                        "DetailGroupID": "",
                        "AddPermanentDetailGroupID": false,
                        "UseGroupAsDefaultNewItems": false
                    },
                    {
                        "ItemCode": "",
                        "Charge": true,
                        "Price": 0
                    },
                    {
                        "ItemCode": "",
                        "OrderCost": true,
                        "Price": 0,
                        "OrderCostSupplierID": ""
                    }
                ],
                "dtOrderItemDimensionRequest": [
                    {
                        "Sequence": 0,
                        "Thickness": 0,
                        "Width": 0,
                        "Length": 0,
                        "OrderQty": 0,
                        "UOM": "",
                        "Price": 0,
                        "PriceUOM": "",
                        "PriceOverride": false
                    }
                ]
            }
        }
    }
}
```

## QuoteUpdateValidate
`POST /Orders/QuoteUpdateValidate`

Purpose
Validates updating header information and/or adding new items to an existing quote
Required Inputs

OrderID

Value Required

The following inputs require a value due to data type:

Charge

PriceOverride

OrderCost

PrintMsgOnForms

PrintMsgOnFormsOverride

SendMsgToWMS

SendMsgToWMSOverride

Optional Inputs

All fields in dtQuoteHeaderUpdateRequest

Remaining fields in the dtOrderItemRequest, or dtOrderItemDimensionRequest not already referenced

Notes

Refer to the Notes in the QuoteUpdate method

Review the dsAuditResults to identify changes needed in the request in order for the validation to be successful

The ‘Require Template for Non-Stock’ security action will not be read

If a value is sent in both the ItemCode and TemplateItemCode tags

ItemCode value will not be read

TemplateItemCode value will be read and used to create a non-stock item

TemplateItemCode value must be active, saleable, no order restrictions, and not a BOM parent item

If any of the following tags are not sent or sent with a blank value, values assigned to the TemplateItemCode sent in the API will be used when creating the non-stock item

NonStockSize

NonStockDescription

NonStockExtDescription

NonStockProductGroupMajor

NonStockProductGroupMinor

NonStockPriceCodeMajor

NonStockPriceCodeMinor

NonStockCost

NonStockCostUOM

If a value is sent for the NonStockProductGroupMajor tag, then a value must also be sent for the NonStockProductGroupMinor tag; the reciprocal is also true

If a value is sent for the NonStockPriceCodeMajor tag, then a value must also be sent for the NonStockPriceCodeMinor tag; the reciprocal is also true

If a value is sent for the NonStockCost tag, then a value must also be sent for the NonStockCostUOM tag; the reciprocal is also true

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Refer to the relationships section in the QuoteUpdate method

Version Deployed
v609

**Request body:**
```json
{
    "request": {
        "OrderID": 0,
        "QuoteHeaderUpdateJSON": {
            "dsQuoteHeaderUpdateRequest": {
                "dtQuoteHeaderUpdateRequest": [
                    {
                        "TransactionReference": "",
                        "TransactionJob": "",
                        "OrderedBy": "",
                        "CustomerPO": "",
                        "ShipVia": "",
                        "RequestedDeliveryDate": "",
                        "ActivationDate": "",
                        "CloseDate": "",
                        "ExternalSource": "",
                        "ExternalProjectID": ""
                    }
                ]
            }
        },
        "OrderItemUpdateJSON": {
            "dsOrderItemRequest": {
                "dtOrderItemRequest": [
                    {
                        "Sequence": 1,
                        "ItemCode": "",
                        "OrderQty": 0,
                        "UOM": "",
                        "Charge": false,
                        "Price": 0,
                        "PriceUOM": "",
                        "PriceOverride": false,
                        "UseItemConvertPriceAndUOM": false,
                        "OrderCost": false,
                        "CustomerPOLineNumber": "",
                        "DepartmentName": "",
                        "DepartmentNumber": "",
                        "PartNumber": "",
                        "SKU": "",
                        "UPCCode": "",
                        "ItemMessage": "",
                        "PrintMsgOnForms": false,
                        "PrintMsgOnFormsOverride": false,
                        "SendMsgToWMS": false,
                        "SendMsgToWMSOverride": false,
                        "APIPriceSourceType": "",
                        "APIPriceSourceRef": "",
                        "DetailGroupID": "Driveway",
                        "AddPermanentDetailGroupID": false,
                        "UseGroupAsDefaultNewItems": true
                    },
                    {
                        "Sequence": 2,
                        "TemplateItemCode": "",
                        "NonStockSize": "",
                        "NonStockDescription": "",
                        "NonStockExtDescription": "",
                        "NonStockCopyCustomFields": true,
                        "NonStockSupplierID": "",
                        "NonStockSupplierShipFromSequence": 0,
                        "NonStockSupplierPartNumber": "",
                        "NonStockProductGroupMajor": "",
                        "NonStockProductGroupMinor": "",
                        "NonStockPriceCodeMajor": "",
                        "NonStockPriceCodeMinor": "",
                        "NonStockCost": 0,
                        "NonStockCostUOM": "",
                        "OrderQty": 0,
                        "UOM": "",
                        "Charge": false,
                        "Price": 0,
                        "PriceUOM": "",
                        "PriceOverride": false,
                        "OrderCost": false,
                        "CustomerPOLineNumber": "",
                        "DepartmentName": "",
                        "DepartmentNumber": "",
                        "PartNumber": "",
                        "SKU": "",
                        "UPCCode": "",
                        "ItemMessage": "",
                        "PrintMsgOnForms": false,
                        "PrintMsgOnFormsOverride": false,
                        "SendMsgToWMS": false,
                        "SendMsgToWMSOverride": false,
                        "APIPriceSourceType": "",
                        "APIPriceSourceRef": "",
                        "DetailGroupID": "",
                        "AddPermanentDetailGroupID": "false",
                        "UseGroupAsDefaultNewItems": false
                    },
                    {
                        "ItemCode": "",
                        "OrderCost": true,
                        "Price": 0,
                        "OrderCostSupplierID": ""
                    }
                ],
                "dtOrderItemDimensionRequest": [
                    {
                        "Sequence": 0,
                        "Thickness": 0,
                        "Width": 0,
                        "Length": 0,
                        "OrderQty": 0,
                        "UOM": "",
                        "Price": 0,
                        "PriceUOM": "",
                        "PriceOverride": false
                    }
                ]
            }
        }
    }
}
```

## SalesOrderACHPayment
`POST /Orders/SalesOrderACHPayment`

Purpose
Creates an ACH payment or an ACH pending payment
Required Inputs

Type

BankGUID

TransactionID

AmountTendered

Optional Inputs

PaymentID (only valid for Type of "Payment")

Notes

You can send both Types at once, or one at a time.

Type of Pending creates an SO_PENDING_PAYMENT record to be used for processing the ACH payment later at the time of invoicing in Agility when order details have been finalized. When creating a Pending payment type, the system saves the ‘Alternate pay terms code’ from the payment method applied to the ‘Payment terms code’ field in Sales Order Entry.

Type of Payment applies a deposit to the specified transaction, regardless of how the Ability Payment Method is set to process, and place it on the NACHA file. It will not automatically send the ACH info out to the bank.

The BankGUID input is a system-assigned value that uniquely identifies the Customer Bank record. This is not the bank account.

0.00 AmountTendered for Pending Type defaults to order total amount on the sales order.

PaymentID can be provided for the Payment type if you do not wish the value to be system-assigned.

Overpayments always process as a deposit for the Payment type.

User must have data allocations for the customer assigned to the sales order for which the payment is being applied.

Relationships

ContextId and Branch come from Login

BankGUID comes from CustomerACHBankList

TransactionID comes from SalesOrderList

Version Deployed
v607

**Request body:**
```json
{
    "request": {
        "SalesOrderACHPaymentJSON": {
            "dsPayment": {
                "dtPayment": [
                    {
                        "Type": "Pending",
                        "BankGuid": "",
                        "dtTransaction": [
                            {
                                "TransactionID": 0,
                                "AmountTendered": 0.0
                            }
                        ]
                    },
                    {
                        "Type": "Payment",
                        "BankGuid": "",
                        "dtTransaction": [
                            {
                                "TransactionID": 0,
                                "PaymentID": "",
                                "AmountTendered": 0.0
                            },
                            {
                                "TransactionID": 0,
                                "PaymentID": "",
                                "AmountTendered": 0.0
                            }
                        ]
                    }
                ]
            }
        }
    }
}
```

## SalesOrderCancel
`POST /Orders/SalesOrderCancel`

Purpose
Cancels a specified sales order
Required Inputs

SalesOrderID

Optional Inputs

Remaining fields in the OrderCancelJSON

Notes

The following rules apply in order for a sales order to be successfully canceled:

Header status must either be blank or staged if it has a direct sale type

Transaction cannot be a shipping sales order

No printed work orders are linked to any sales order detail items or work order components on a sales order detail item

No printed remans are linked to any shipping sales order items when the requesting sales order is attempting to be canceled

ReasonCode corresponds to the Cancel Sales Order Reason Code in Agility

Comment allows you to specify a comment for the Reason Code

CancelLinkedTran controls whether to cancel the linked transaction to the sales order. If the sales order sale type is direct, then the linked purchase order is canceled regardless of the value in this field. If this field is not included in the request, the system does not cancel the linked transaction.

AllowLinkedPrintedTran controls whether the sales order can be cancelled based on the print status of the linked transaction. If this field is not included in the request, the system does not cancel the linked transaction if any of the linked transactions have been printed.

SendS855 allows you to transmit an S855 EDI record on cancelling the sales order which was created from the R855 EDI process. If this field is not included in the request, the system does not send the S855.

SendS870 allows you to transmit an S870 EDI record on cancelling the sales order which was created from the R870 EDI process. If this field is not included in the request, the system does not send the S870.

Relationships

ContextId and Branch come from Login

Version Deployed
v553

**Request body:**
```json
{
    "request": {
        "SalesOrderID": 0,
        "OrderCancelJSON": {
            "dsOrderCancel": {
                "dtOrderCancel": [
                    {
                        "ReasonCode": "",
                        "Comment": "",
                        "CancelLinkedTran": true,
                        "AllowLinkedPrintedTran": true,
                        "SendS855": false,
                        "SendS870": false
                    }
                ]
            }
        }
    }
}
```

## SalesOrderCreate
`POST /Orders/SalesOrderCreate`

Purpose
Creates a new sales order, which can include BOM parent items with components, with specified tax rates and a specified sale type, as well as a shipment
Required Inputs

CustomerID

ShipToSequence

ItemCode

OrderQty for each detail

Value Required

PrePaid

ShipComplete

ShipCompleteOverride

CreateShipment

Charge

PriceOverride

OrderCost

SendMsgToWMS

SendMsgToWMSOverride

PrintFlag

SundryCostOverride

Optional Inputs

Remaining fields in the dtOrderHeaderRequest, dtOrderHeaderNotesRequest, dtOrderItemRequest, dtOrderItemDimensionRequest, dtOrderItemComponentRequest not already referenced

dtTaxAuthorityRequest

Notes

This method allows parent items and related components to be added to the sales order. When added successfully, a work order is created for the configured parent item.

At least 1 item or dimension must be sent in.

Each detail must have an OrderQty > 0.

If ordering by dimension:

Values for Thickness, Width, and/or Length are required based on item type. Note: For tally calc type items, you must order by total footage and not by dimension.

The dimension must match an existing dimension record for the item.

The OrderQty and UOM must also be specified at the dimension level.

If there are multiple inputs in the dtOrderItemDimensionRequest for the same Sequence value, the dimensions are added as tally quantities for the same sales order line.

Use the PartNumber field if the item being ordered is a customer part number. When populated the PartNumber is read first before the ItemCode using the following search hierarchy.

Search the item cross reference hierarchy for a match to the PartNumber submitted in the request. If a match is found the sales order detail item cross reference field is populated with the PartNumber value.

Search the item cross reference hierarchy for a match to the ItemCode submitted in the API request. If a match is found, the sales order detail item cross reference field is populated with the ItemCode value.

Search for a valid Agility item code that matches the ItemCode submitted in the API request.

Search for a valid Agility item code that matches the PartNumber submitted in the API request.

An item must be active in the branch to be able to add the item to the order. If the item is not active, the entire order will fail.

This method can be used when integrating with a tax provider to push the correct rates and jurisdictions to Agility. The incoming tax jurisdictions are created in Agility if not already present and a new tax code, if not already present, is built and applied to the order.

If invalid or incomplete inputs are detected in the dtTaxAuthorityRequest, the sales order will be created, but the method will return a ReturnCode = 1 and a MessageText indicating the issue. In this case, the order is marked as taxable, but the tax code will be blank. Blank tax code must be corrected before the order can be invoiced.

If CreateShipment = true, the process attempts to create a shipment for the material ordered. If a shipment could not be created, based on Agility rules, the method will return a ReturnCode = 1 and a MessageText indicating the issue. In this case, the order is still created, but no shipment is created.

This method allows you to save the price from a third-party pricing service when PriceOverride = true. The values from the APIPriceSourceRef field and APIPriceSourceType fields save to the corresponding fields on the sales order and the price history record. The price saves to the Orig price and Price fields on the sales order item detail record. If either the APIPriceSourceRef or APIPriceSourceType field are blank, the system creates two price history records. The first price history record contains the Agility price. The second price history record contains the overridden price from the incoming file. The Agility price saves to the Orig price. The overridden prices saves to the Price field on the item detail record. When PriceOverride = false, the system uses the price from Agility on the transaction.

If UseItemConvertPriceAndUOM = true, the process converts the price and price UOM to the order qty UOM if all the following criteria are met:

PriceOverride = false

Convert price/price UOM to match order field on the item record is set in Agility

The UOM sent in the dtOrderItemRequest does not match the SO/Quote UOM on the item record in Agility

If the sale type in Agility is set to Auto tag items for direct transfer, all items on the order will be set to fill from the branch populated in the ShippingBranch field for the first item sent in the method. If the ShippingBranch field is not sent in the method, the default transfer branch assigned to the first item on the item branch record is used.

If an item is set to fill from BT and the ShippingBranch field is not sent in the method, the default transfer branch is assigned to the item branch record.

When a TemplateItemCode is populated in the dtOrderItemRequest or dtOrderItemComponentRequest, the ItemCode is ignored. The following fields apply to the non-stock item created from the TemplateItemCode value: NonStockSize, NonStockDescription, NonStockExtDescription, NonStockCopyCustomFields. Unless the NonStockCopyCustomFields is set to true the system does not copy custom item fields.

If the SalesAgent tags from the dtOrderHeaderRequest is not sent in, the system uses the sales agent specified in the User Profile and then the default from the customer ship-to.

If the SalesAgentPctOfOrder tags from the dtOrderHeaderRequest are sent in with a value of 0, the system uses the default percentages from the SO Parameter. If the SO parameter Default Percentage is not defined, then the system uses the default percentages from the customer ship-to record.

This method allows you to specify shipping tracking information fields when OverrideShippingTrackingData = true. The values from the following shipping tracking fields save to the corresponding fields on the sales order and bypass any customer ship-to defaults: ShippingTrackingInsuranceReq, ShippingTrackingSignatureReq, ShippingTrackingSaturdayDelivery, ShippingTrackingSundayDelivery, ShippingTrackingDelvInstructions.

If any of the ship-to address tags are sent in with a value, the system clears out the other ship-to address fields instead of using the default values. For example, if you send in a value in only the ShipToAddress1 tag, the city and state on the newly created SO will be blank. If you override a ship-to address, you must send in all relevant ship-to address tags. The tags included in the ship-to address fields are as follows: ShipToAddress1, ShipToAddress2, ShipToAddress3, ShipToCity, ShipToState, ShipToZip, ShipToCountry.

If all ship-to address tags have a value of blank, or none of them are sent in the request, then the system uses the default ship-to address values.

This method allows customer charges and order costs to be added to the sales order. If either Charge = True or OrderCost = True in the dtOrderItemRequest, then the ItemCode value must correspond to a valid Charge type or Cost type in Agility, and the Price is the amount applied to the order. All other tags in the dtOrderItemRequest are ignored.

You can only add customer charges and order costs with the record type of header charge, header charge allocated to detail, header charge calculated by item detail, or header cost.

The customer charge or order cost is added or updated with a fixed amount basis.

If the Price is greater than or equal to 0, then the customer charge or order cost applies as a Charge or Cost, respectively.

If the Price is less than 0, then the customer charge or order cost applies as a Refund or Cost Reduction, respectively.

The ‘Require Template for Non-Stock’ security action will not be read

If a value is sent in both the ItemCode and TemplateItemCode tags

ItemCode value will not be read

TemplateItemCode value will be read and used to create a non-stock item

TemplateItemCode value must be active, saleable, no order restrictions, and not a BOM parent item

If any of the following tags are not sent or sent with a blank value, values assigned to the TemplateItemCode sent in the API will be used when creating the non-stock item

NonStockSize

NonStockDescription

NonStockExtDescription

NonStockProductGroupMajor

NonStockProductGroupMinor

NonStockPriceCodeMajor

NonStockPriceCodeMinor

NonStockCost

NonStockCostUOM

If a value is sent for the NonStockCost tag, then a value must also be sent for the NonStockCostUOM tag

The AddPermanentDetailGroupID tag determines if a permanent detail group record is created for the detail group received in the request

An Order Acknowledgement form for the created sales order is sent to the emails provided in the AcknowledgementEmailAddress and AcknowledgementEmailAddress2 tags or the fax number provided in the AcknowledgementFaxNumber tag. If none of the tags are populated, an Order Acknowledgement form is not sent.

If CommitFromSpecifiedLocation = true, the CommitLocation value is read and used to commit the item at the specified location if sufficient available quantity exists. This functionality should only be used as the exception if there is a specific business reason to override the commit settings on the item record and/or commit rules defined in Tran Criteria.

If the value in the CommitLocation tag corresponds to a location or a location and sublocation that has sufficient quantity to fill the full order, the system reads the 'commit all – do not backorder' flag on the item record and either commits available quantity from the branch level and backorders unavailable quantity or creates negative available quantity.

If a commit location is specified for a parent item, all of the parent's components are committed from that location. The parent item continues to be backordered until the work order is completed in work order completion or when an 'auto-complete' parent is included in a pick file or shipment. At that time, the completed parent is put into stock at the defined default location on the item record.

If CommitFromSpecifiedLocation = false, the system follows the current commit rules.

If CommitFromSpecifiedLocation = true but no valid location or location and sublocation is provided in the CommitLocation tag, the request fails and no order is created.

When entering a location and sublocation value in the CommitLocation tag, follow the format "Location Sublocation".

Relationships

Context ID and Branch come from Login

Valid values for CustomerID come from CustomersList or CustomerShiptoList

Valid values for ShipToSequence come from CustomerShiptosList

Valid values for ItemCode and related Thickness, Width and Length come from ItemsList or ItemsInChunksList

Valid values for ShippingBranch come from BranchList

The NewOrderID returned from this method can be used in conjunction with the SearchBy feature in SalesOrderList to verify the new sales order was created as expected.

This method contains a parent/child relationship between the dtOrderItemRequest and dtOrderItemDimensionRequest. Please see the Parent/Child relationships topic for more information.

This method contains a parent/child relationship between the dtOrderItemRequest and dtOrderItemComponentRequest. Please see the Parent/Child relationships topic for more information.

There is a many to one relationship between the dtTaxAuthorityRequest and the dtOrderHeaderRequest as the method allows the input of tax rates from various taxing jurisdictions to build the resulting tax code to apply to the order.

Version Deployed
v547

**Request body:**
```json
{
    "request": {
        "dsOrderHeaderRequest": {
            "dtOrderHeaderRequest": [
                {
                    "CustomerID  ": "",
                    "ShipToSequence": 0,
                    "TransactionReference": "",
                    "TransactionJob ": "",
                    "OrderedBy": "",
                    "CustomerPurchaseOrder": "",
                    "CheckPORequiredSettings": false,
                    "CheckPODuplicateSettings": false,
                    "AcknowledgementEmailAddress": "",
                    "AcknowledgementEmailAddress2": "",
                    "AcknowledgementFaxNumber": "",
                    "PrePaid": false,
                    "ShipToName ": "",
                    "ShipToAddress1": "",
                    "ShipToAddress2": "",
                    "ShipToAddress3": "",
                    "ShipToCity ": "",
                    "ShipToState": "",
                    "ShipToZip": "",
                    "ShipToCountry": "",
                    "ShipToPhone": "",
                    "TaxCode": "",
                    "SaleType": "",
                    "OrderMessage": "",
                    "OrderHold": true,
                    "ShipVia": "",
                    "ShipComplete": false,
                    "ShipCompleteOverride": false,
                    "CreateShipment": false,
                    "MiscField1": "",
                    "MiscField2": "",
                    "MiscField3": "",
                    "MiscField4": "",
                    "MiscField5": "",
                    "MiscField6": "",
                    "MiscField7": "",
                    "MiscField8": "",
                    "MiscField9": "",
                    "MiscField10": "",
                    "MiscField11": "",
                    "MiscField12": "",
                    "MiscDate1": null,
                    "MiscDate2": null,
                    "APISourceID": "",
                    "SalesAgent1": "",
                    "SalesAgent2": "",
                    "SalesAgent3": "",
                    "SalesAgent4": "",
                    "SalesAgent5": "",
                    "SalesAgent6": "",
                    "SalesAgent1PctOfOrder": 0,
                    "SalesAgent2PctOfOrder": 0,
                    "SalesAgent3PctOfOrder": 0,
                    "SalesAgent4PctOfOrder": 0,
                    "SalesAgent5PctOfOrder": 0,
                    "SalesAgent6PctOfOrder": 0,
                    "RouteID": "",
                    "ExpectedDate": "",
                    "OverrideShippingTrackingData": true,
                    "ShippingTrackingSignatureReq": true,
                    "ShippingTrackingInsuranceReq": false,
                    "ShippingTrackingSaturdayDelivery": true,
                    "ShippingTrackingSundayDelivery": false,
                    "ShippingTrackingDelvInstructions": "",
                    "FreightTerms": "",
                    "PaymentTerms": "",
                    "SourceLogin": ""
                }
            ],
            "dtOrderHeaderNotesRequest": [
                {
                    "OrderNote": "",
                    "HotNote": false
                }
            ]
        },
        "dsOrderItemRequest": {
            "dtOrderItemRequest": [
                {
                    "Sequence": 1,
                    "ItemCode": "",
                    "OrderQty": 0,
                    "UOM": "",
                    "Charge": false,
                    "Price": 0,
                    "PriceUOM": "",
                    "PriceOverride": false,
                    "UseItemConvertPriceAndUOM": false,
                    "OrderCost": false,
                    "CustomerPOLineNumber": "",
                    "DepartmentName": "",
                    "DepartmentNumber": "",
                    "PartNumber": "",
                    "SKU": "",
                    "UPCCode": "",
                    "ItemMessage": "",
                    "PrintMsgOnForms": false,
                    "PrintMsgOnFormsOverride": false,
                    "SendMsgToWMS": false,
                    "SendMsgToWMSOverride": false,
                    "APIPriceSourceType": "",
                    "APIPriceSourceRef": "",
                    "DetailGroupID": "",
                    "AddPermanentDetailGroupID": false,
                    "UseGroupAsDefaultNewItems": false,
                    "Size": "",
                    "Description": "",
                    "CommitFromSpecifiedLocation": false,
                    "CommitLocation": ""
                },
                {
                    "ItemCode": "",
                    "Charge": true,
                    "Price": 0
                },
                {
                    "ItemCode": "",
                    "OrderCost": true,
                    "Price": 0,
                    "OrderCostSupplierID": ""
                }
            ],
            "dtOrderItemDimensionRequest": [
                {
                    "Sequence": 1,
                    "Thickness": 0,
                    "Width": 0,
                    "Length": 0,
                    "OrderQty": 0,
                    "UOM": "",
                    "Price": 0,
                    "PriceUOM": "",
                    "PriceOverride": false
                }
            ]
        },
        "dsOrderItemComponentRequest": {
            "dtOrderItemComponentRequest": [
                {
                    "OrderItemSequence": 3,
                    "ComponentSequence": 1,
                    "BomType": "",
                    "ItemCode": "",
                    "PartNumber": "",
                    "OrderQty": 1,
                    "Price": 0,
                    "PriceOverride": true,
                    "Thickness": 0,
                    "Width": 0,
                    "Length": 0,
                    "PieceCount": 0,
                    "TallyUOM": "",
                    "PrintFlag": false,
                    "SundryCost": 0,
                    "SundryCostOverride": false,
                    "ItemMessage": "",
                    "PrintMsgOnForms": false,
                    "PrintMsgOnFormsOverride": false,
                    "UOM": "",
                    "ShipLoose": true,
                    "Size": "",
                    "Description": ""
                }
            ]
        },
        "dsTaxAuthorityRequest": {
            "dtTaxAuthorityRequest": [
                {
                    "JurisdictionType": "",
                    "State": "",
                    "County": "",
                    "City": "",
                    "Description": "",
                    "SalesTaxRate": 0
                }
            ]
        }
    }
}
```

## SalesOrderCreateValidate
`POST /Orders/SalesOrderCreateValidate`

Purpose
Validates the creation of a new sales order, which can include BOM parent items with components, specified tax rates and a specified sale type, as well as a shipment
Required Inputs

CustomerID

ShipToSequence

ItemCode

OrderQty for each detail

Value Required

PrePaid

ShipComplete

ShipCompleteOverride

CreateShipment

Charge

PriceOverride

OrderCost

SendMsgToWMS

SendMsgToWMSOverride

PrintFlag

SundryCostOverride

Optional Inputs

Remaining fields in the dtOrderHeaderRequest, dtOrderHeaderNotesRequest, dtOrderItemRequest, dtOrderItemDimensionRequest, dtOrderItemComponentRequest not already referenced

dtTaxAuthorityRequest

Notes

Refer to the Notes in the SalesOrderCreate method.

Review the dsAuditResults to identify changes needed in the request in order for the validation to be successful.

Relationships

Context ID and Branch come from Login

Alternate branches come from BranchList

Refer to the Relationships section in the SalesOrderCreate method.

Version Deployed
v547

**Request body:**
```json
{
    "request": {
        "dsOrderHeaderRequest": {
            "dtOrderHeaderRequest": [
                {
                    "CustomerID  ": "",
                    "ShipToSequence": 0,
                    "TransactionReference": "",
                    "TransactionJob ": "",
                    "OrderedBy": "",
                    "CustomerPurchaseOrder": "",
                    "CheckPORequiredSettings": false,
                    "CheckPODuplicateSettings": false,
                    "AcknowledgementEmailAddress": "",
                    "AcknowledgementEmailAddress2": "",
                    "AcknowledgementFaxNumber": "",
                    "PrePaid": false,
                    "ShipToName ": "",
                    "ShipToAddress1": "",
                    "ShipToAddress2": "",
                    "ShipToAddress3": "",
                    "ShipToCity ": "",
                    "ShipToState": "",
                    "ShipToZip": "",
                    "ShipToCountry": "",
                    "ShipToPhone": "",
                    "TaxCode": "",
                    "SaleType": "",
                    "OrderMessage": "",
                    "OrderHold": true,
                    "ShipVia": "",
                    "ShipComplete": false,
                    "ShipCompleteOverride": false,
                    "CreateShipment": false,
                    "MiscField1": "",
                    "MiscField2": "",
                    "MiscField3": "",
                    "MiscField4": "",
                    "MiscField5": "",
                    "MiscField6": "",
                    "MiscField7": "",
                    "MiscField8": "",
                    "MiscField9": "",
                    "MiscField10": "",
                    "MiscField11": "",
                    "MiscField12": "",
                    "MiscDate1": null,
                    "MiscDate2": null,
                    "APISourceID": "",
                    "SalesAgent1": "",
                    "SalesAgent2": "",
                    "SalesAgent3": "",
                    "SalesAgent4": "",
                    "SalesAgent5": "",
                    "SalesAgent6": "",
                    "SalesAgent1PctOfOrder": 0,
                    "SalesAgent2PctOfOrder": 0,
                    "SalesAgent3PctOfOrder": 0,
                    "SalesAgent4PctOfOrder": 0,
                    "SalesAgent5PctOfOrder": 0,
                    "SalesAgent6PctOfOrder": 0,
                    "RouteID": "",
                    "ExpectedDate": "",
                    "OverrideShippingTrackingData": true,
                    "ShippingTrackingSignatureReq": true,
                    "ShippingTrackingInsuranceReq": false,
                    "ShippingTrackingSaturdayDelivery": true,
                    "ShippingTrackingSundayDelivery": false,
                    "ShippingTrackingDelvInstructions": "",
                    "FreightTerms": "",
                    "PaymentTerms": "",
                    "SourceLogin": ""
                }
            ],
            "dtOrderHeaderNotesRequest": [
                {
                    "OrderNote": "",
                    "HotNote": false
                }
            ]
        },
        "dsOrderItemRequest": {
            "dtOrderItemRequest": [
                {
                    "Sequence": 1,
                    "ItemCode": "",
                    "OrderQty": 0,
                    "UOM": "",
                    "Charge": false,
                    "Price": 0,
                    "PriceUOM": "",
                    "PriceOverride": false,
                    "UseItemConvertPriceAndUOM": false,
                    "OrderCost": false,
                    "CustomerPOLineNumber": "",
                    "DepartmentName": "",
                    "DepartmentNumber": "",
                    "PartNumber": "",
                    "SKU": "",
                    "UPCCode": "",
                    "ItemMessage": "",
                    "PrintMsgOnForms": false,
                    "PrintMsgOnFormsOverride": false,
                    "SendMsgToWMS": false,
                    "SendMsgToWMSOverride": false,
                    "APIPriceSourceType": "",
                    "APIPriceSourceRef": "",
                    "DetailGroupID": "",
                    "AddPermanentDetailGroupID": false,
                    "UseGroupAsDefaultNewItems": false,
                    "Size": "",
                    "Description": "",
                    "CommitFromSpecifiedLocation": false,
                    "CommitLocation": ""
                },
                {
                    "ItemCode": "",
                    "Charge": true,
                    "Price": 0
                },
                {
                    "ItemCode": "",
                    "OrderCost": true,
                    "Price": 0,
                    "OrderCostSupplierID": ""
                }
            ],
            "dtOrderItemDimensionRequest": [
                {
                    "Sequence": 1,
                    "Thickness": 0,
                    "Width": 0,
                    "Length": 0,
                    "OrderQty": 0,
                    "UOM": "",
                    "Price": 0,
                    "PriceUOM": "",
                    "PriceOverride": false
                }
            ]
        },
        "dsOrderItemComponentRequest": {
            "dtOrderItemComponentRequest": [
                {
                    "OrderItemSequence": 3,
                    "ComponentSequence": 1,
                    "BomType": "",
                    "ItemCode": "",
                    "PartNumber": "",
                    "OrderQty": 1,
                    "Price": 0,
                    "PriceOverride": true,
                    "Thickness": 0,
                    "Width": 0,
                    "Length": 0,
                    "PieceCount": 0,
                    "TallyUOM": "",
                    "PrintFlag": false,
                    "SundryCost": 0,
                    "SundryCostOverride": false,
                    "ItemMessage": "",
                    "PrintMsgOnForms": false,
                    "PrintMsgOnFormsOverride": false,
                    "UOM": "",
                    "ShipLoose": true,
                    "Size": "",
                    "Description": ""
                }
            ]
        },
        "dsTaxAuthorityRequest": {
            "dtTaxAuthorityRequest": [
                {
                    "JurisdictionType": "",
                    "State": "",
                    "County": "",
                    "City": "",
                    "Description": "",
                    "SalesTaxRate": 0
                }
            ]
        }
    }
}
```

## SalesOrderDetailsDelete
`POST /Orders/SalesOrderDetailsDelete`

Purpose
Deletes an existing sales order detail record
Required Inputs

SalesOrderID

Sequence

Optional Inputs

UpdateLinkedTran

UpdateLinkedPrintedTran

Notes

The following rules apply in order for a sales order detail to be successfully deleted

Item cannot have a locked contract price

Item does not have any quantity that is picked, staged (when the order affects inventory) or invoiced

Item is staged and does not affect inventory

Item is not on a shipping sales order

If item is a BOM parent, the work order status is Not Printed

Item is not on a sales order with a source of EDI set to creates an in process S870 EDI process.

UpdateLinkedTran controls whether to cancel the linked transaction (such as a purchase order, work order or reman) to the sales order item. If the item does not affect inventory, then the linked purchase order is canceled regardless of the value in this field. If this field is not included in the request, the system does not cancel the linked transaction.

UpdateLinkedPrintedTran controls whether to cancel the linked transaction to the item when it has been printed. If this field is not included in the request, the system does not cancel the linked transaction if it has been printed.

If the customer does not allow overpayments and an item deletion would cause an overpayment, the system does not allow the item to be deleted.

Relationships

ContextId and Branch come from Login

Valid sales order details come from SalesOrderList

Version Deployed
v554

**Request body:**
```json
{
    "request": {
        "SalesOrderID": 0,
        "OrderDetailsDeleteJSON": {
            "dsDetailDeleteSettings": {
                "dtDetailDeleteSettings": [
                    {
                        "UpdateLinkedTran": true,
                        "UpdateLinkedPrintedTran": true
                    }
                ]
            },
            "dsOrderItemRequest": {
                "dtOrderItemRequest": [
                    {
                        "Sequence": 2
                    },
                    {
                        "Sequence": 3
                    }
                ]
            }
        }
    }
}
```

## SalesOrderDetailsUpdate
`POST /Orders/SalesOrderDetailsUpdate`

Purpose
Updates an existing sales order detail record
Required Inputs

SalesOrderID

Sequence

OrderQty

UOM

Optional Inputs

Fields within dtDetailUpdateSettings

Notes

The item being updated must be the following criteria in order to be successfully updated:

Item is allowed in the API

Item is not discontinued

Item is not a template item

Item is not a credit memo item

Item is not a BOM parent item

Item is not a ship loose item

Item is not partially or fully invoiced

Item is not partially or fully picked

Item does not have contractor prices locked

If item is staged, the sale type on the order does not affect inventory

If updating a dimension on an item, values for Thickness, Width and/or Length are required based on the item type. If the existing item has tallies specified, dimension information must be sent in through dtOrderItemDimensionRequest. In addition, the OrderQty and UOM must be specified at the dimension level. Use the PieceCount field when the OrderQty has a value of “UNIT”. Sheet Good item types will require the Width and Length to match existing item.

UpdateLinkedTran controls whether to update the linked transaction (such as a purchase order or reman) to the sales order item. If the item does not affect inventory, then the linked purchase order is updated regardless of the value in this field. If this field is not included in the request, the system does not update the linked transaction.

UpdateLinkedPrintedTran controls whether to update the linked transaction to the item when it has been printed. If this field is not included in the request, the system does not update the linked transaction if it has been printed.

If UseItemConvertPriceAndUOM = true, the process converts the price and price UOM to the order qty UOM if all the following criteria are met:

Convert price/price UOM to match order field on the item record is set in Agility

The UOM sent in the dtOrderItemRequest does not match the SO/Quote UOM on the item record in Agility

DMSi strongly recommends reviewing dsAuditResults regardless of the ReturnCode value

The AddPermanentDetailGroupID tag determines if a permanent detail group record is created for the detail group received in the request

Relationships

ContextId and Branch come from Login

Valid sales order details come from SalesOrderList

Valid values for a sequence’s thickness, width and length come from ItemList or ItemsInChunksList

This method contains a parent/child relationship between the dtOrderItemRequest and dtOrderItemDimensionRequest. Please see Parent/Child relationship topic for more information

Version Deployed
v554

**Request body:**
```json
{
    "request": {
        "SalesOrderID": 0,
        "OrderDetailsUpdateJSON": {
            "dsDetailUpdateSettings": {
                "dtDetailUpdateSettings": [
                    {
                        "UpdateLinkedTran": false,
                        "UpdateLinkedPrintedTran": false
                    }
                ]
            },
            "dsOrderItemRequest": {
                "dtOrderItemRequest": [
                    {
                        "Sequence": 1,
                        "OrderQty": 0,
                        "UOM": "",
                        "UseItemConvertPriceAndUOM": false,
                        "DetailGroupID": "",
                        "AddPermanentDetailGroupID": false,
                        "UseGroupAsDefaultNewItems": false,
                        "Size": "",
                        "Description": "",
                        "dtOrderItemDimensionRequest": [
                            {
                                "Sequence": 1,
                                "Thickness": 0,
                                "Width": 0,
                                "Length": 0,
                                "PieceCount": 0,
                                "OrderQty": 0,
                                "UOM": ""
                            }
                        ]
                    }
                ]
            }
        }
    }
}
```

## SalesOrderList
`POST /Orders/SalesOrderList`

Purpose
Returns a list of sales orders for a specified customer
Required Inputs

CustomerID

Value Required
The following inputs require a value due to data type:

FetchOnlyChangedSince

IncludeOpenOrders

IncludeInvoicedOrders

IncludeCanceledOrders

ChunkStartPointer

RecordFetchLimit

Optional Inputs

SearchBy

SearchValue

ShipToSequence

OrderDateRangeStart

OrderDateRangeEnd

ExpectedDateRangeStart

ExpectedDateRangeEnd

Notes

This method can return the list of sales orders at a sold-to or ship-to level depending on the value in ShipToSequence. Specify 0 as the ShipToSequence to return sales orders for the sold-to

The method allows the user to search for and select items based on SearchBy or to request the information for all items. Please see the SearchBy topic for more information

This method allows a user to request a specific number of records. Please see the Chunking topic for more information

Because the number of records to be returned based on the search criteria could be large, DMSi recommends using the chunking feature, especially when requesting the list at a sold-to level

A value of < all > can be specified in CustomerID (Note: Do not include spaces between the characters and the word "all" when including this in the request.)

A value must also be specified in SearchBy and SearchValue

Specify 0 as the ShipToSequence

Valid values for CustomerID come from CustomersList or CustomerShiptoList

Valid values for ShipToSequence come from CustomerShiptoList

Valid values for SearchBy are Order ID, Quote ID, Job #, Reference #, and Customer PO

While this method can be called for any known valid sales order id, the SearchBy and SearchValue inputs allow the method to return a specific sales order

The ItemXrefUsedToOrder displays the item cross reference field from the Sales order detail.

Messages tied to a specific shipment are not included in the response.

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

This method has a Parent/Child relationship between dtOrder and dtOrderDetail through OrderID. This can be a one to many relationship

A one-to-many Parent/Child relationship exists between dtOrderResponse and dtOrderHeaderNote through OrderID

A one-to-many Parent/Child relationship exists between dtOrderResponse and dtOrderHeaderMessage through OrderID

A one-to-many Parent/Child relationship exists between dtOrderDetailResponse and dtOrderDetailMessage through Sequence.

Version Deployed
v539

**Request body:**
```json
{
    "request": {
        "SearchBy": "",
        "SearchValue": "",
        "CustomerID": "",
        "ShipToSequence": 1,
        "OrderDateRangeStart": null,
        "OrderDateRangeEnd": null,
        "ExpectedDateRangeStart": null,
        "ExpectedDateRangeEnd": null,
        "FetchOnlyChangedSince": null,
        "IncludeOpenOrders": true,
        "IncludeInvoicedOrders": false,
        "IncludeCanceledOrders": false,
        "ChunkStartPointer": "",
        "RecordFetchLimit": ""
    }
}
```

## SalesOrderMessageCreate
`POST /Orders/SalesOrderMessageCreate`

Purpose
Creates a sales order transaction message in the branch the user is logged into
Required Inputs

TranID

MessageText

MessageType

TranSeq (for detail transaction messages)

Optional Inputs

PrintOnForms

SendToWMS

ShipmentNum

Notes

MessageText can send a maximum of 1000 characters

Valid values for MessageType are H, Header, D, Detail, F, and Footer

When PrintOnForms is set to true, all eligible forms are set to print the new message

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v554

**Request body:**
```json
{
    "request": {
        "MessageCreateJSON": {
            "dsMessageCreate": {
                "dtMessageCreate": [
                    {
                        "TranID": 0,
                        "ShipmentNum": null,
                        "TranSeq": "",
                        "MessageText": "",
                        "MessageType": "",
                        "PrintOnForms": "",
                        "SendToWMS": ""
                    }
                ]
            }
        }
    }
}
```

## SalesOrderMessageDelete
`POST /Orders/SalesOrderMessageDelete`

Purpose
Deletes existing sales order transaction messages
Required Inputs

TranID

MessageType

TranSeq (for detail transaction messages)

MessageID

Optional Inputs

ShipmentNum

Notes

Valid values for MessageType are H, Header, D, Detail, F and Footer

You must specify the TranSeq value when MessageType is "D" or "Detail"

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Valid sales order message values come from SalesOrderList

Version Deployed
v619

**Request body:**
```json
{
    "request": {
        "TranID": 0,
        "MessageDeleteJSON": {
            "dsMessageDelete": {
                "dtMessageDelete": [
                    {
                        "ShipmentNum": 0,
                        "TranSeq": 0,
                        "MessageType": "",
                        "MessageID": 0
                    }
                ]
            }
        }
    }
}
```

## SalesOrderMessageUpdate
`POST /Orders/SalesOrderMessageUpdate`

Purpose
Updates existing sales order transaction messages
Required Inputs

TranID

ShipmentNum

MessageType

TranSeq (for detail transaction messages)

MessageID

Optional Inputs

MessageText

PrintOnForms

SendToWMS

Notes

Valid values for MessageType are H, Header, D, Detail, F and Footer

You must specify the TranSeq value when MessageType is D or Detail

The following rules apply when you send a MessageText value

If the existing MessageID is a reusable message in the system (indicated by positive MessageID value), the system replaces the existing MessageID value with a custom message ID (indicated by a negative MessageID value)

If the existing MessageID is a custom message, the system replaces the existing MessageText and retains the existing MessageID

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Valid sales order message values come from SalesOrderList

Version Deployed
v619

**Request body:**
```json
{
    "request": {
        "TranID": 0,
        "MessageUpdateJSON": {
            "dsMessageUpdate": {
                "dtMessageUpdate": [
                    {
                        "ShipmentNum": 0,
                        "MessageType": "",
                        "TranSeq": 0,
                        "MessageID": 0,
                        "MessageText": "",
                        "PrintOnForms": true,
                        "SendToWMS": true
                    }
                ]
            }
        }
    }
}
```

## SalesOrderNotesDelete
`POST /Orders/SalesOrderNotesDelete`

Purpose
Deletes existing sales order notes records
Required Inputs

OrderID

OrderNoteSequence

Optional Inputs

N/A

Notes

The OrderNoteSequence input value is associated with the note sequence number for the sales order.

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

OrderNoteSequence comes from SalesOrderList

Version Deployed
v619

**Request body:**
```json
{
    "request": {
        "OrderID": 0,
        "SalesOrderNotesDeleteJSON": {
            "dsSalesOrderNotesDelete": {
                "dtSalesOrderNotesDelete": [
                    {
                        "OrderNoteSequence": 0
                    },
                    {
                        "OrderNoteSequence": 0
                    }
                ]
            }
        }
    }
}
```

## SalesOrderPayment
`POST /Orders/SalesOrderPayment`

Purpose
Sends credit card authorization and/or payment information to Agility to store alongside the order upon Sales Order creation via an Agility customer’s eCommerce site
Required Inputs

Type

PaymentAccountID (Pending and TokenPayment Type)

ProcessorTransactionID(Payment Type)

TransactionID

AmountTendered(Pending and TokenPayment Type)

Optional Inputs

AllowTokenDelete

UseAgilitySurcharge

Surcharge

SurchargeBasis

Notes

Access to the Credit Card Interface must be granted to use this request

You can send all three Types at once or one at a time

Type of Pending stores a token to be used for processing the credit card later at the time of invoicing in Agility when order details have been finalized. When creating a Pending payment type, the system saves the ‘Alternate pay terms code’ from the payment method applied to the ‘Payment terms code’ field in Sales Order Entry

Type of Payment includes any credit card payment information that was processed at the time of order creation via the eCommerce platform so that the credit card payment details are reflected in Agility

ProcessorTransactionID is the TransactionID received from the WorldPay for the payment processed via the eCommerce platform

TokenPayment Type is processed immediately in Agility using the provided token so that the credit card payment details are sent and received via Agility

AllowTokenDelete will not delete the token from WorldPay once a pending payment is closed and can be used on multiple Sales Orders if set to No. This option is used when it’s a saved card on the eCommerce platform

AllowTokenDelete defaults to No for Pending Type when not included

0.00 AmountTendered for Pending Type defaults to order total amount on the sales order

Overpayments always process as a deposit on order for Payment and TokenPayment Type

User must have data allocations granted for the customer assigned to the sales order for which the payment is being applied

If UseAgilitySurcharge is true, Surcharge and SurchargeBasis are ignored.

If UseAgilitySurcharge is false, the surcharge is calculated based on the values in Surcharge and SurchargeBasis. Surcharge discounts set at the bill-to or ship-to level are ignored.

You cannot add a surcharge via the Surcharge and SurchargeBasis fields if either of following are true.

A surcharge is not defined on the payment method.

The applicable bill-to/ship-to record, based on the value of the 'Credit card storage option on the sold-to record, is set to 'Do not calculate'.

Surcharge fields apply only to Token Payments.

Relationships

ContextId and Branch come from Login

TransactionID comes from SalesOrderList

Version Deployed
v551

**Request body:**
```json
{
    "request": {
        "SalesOrderPaymentJSON": {
            "dsPayment": {
                "dtPayment": [
                    {
                        "Type": "Pending",
                        "PaymentAccountID": "",
                        "AllowTokenDelete": "",
                        "dtTransaction": [
                            {
                                "TransactionID": 0,
                                "AmountTendered": 0
                            }
                        ]
                    },
                    {
                        "Type": "Payment",
                        "ProcessorTransactionID": "",
                        "dtTransaction": [
                            {
                                "TransactionID": 0
                            }
                        ]
                    },
                    {
                        "Type": "TokenPayment",
                        "PaymentAccountID": "",
                        "dtTransaction": [
                            {
                                "TransactionID": 0,
                                "AmountTendered": 0,
                                "UseAgilitySurcharge": "",
                                "Surcharge": "",
                                "SurchargeBasis": ""
                            }
                        ]
                    }
                ]
            }
        }
    }
}
```

## SalesOrderPaymentRecord
`POST /Orders/SalesOrderPaymentRecord`

Purpose
Send sales order payment information received and processed by an outside source to Agility
Required Inputs

TransactionID

PaymentMethod

AmountTendered

Optional Inputs

PaymentID

Notes

TransactionID is a valid Agility sales order transaction number

The Agility sales order cannot be invoiced or cancelled

PaymentMethod is a valid Agility Payment Method code

An Agility Payment Method code with a ‘Type’ of ‘Reward’ is invalid for the API

AmountTendered must be > zero

PaymentID is required in the API when the Agility Payment Method is set to require either an Authorization # or Check #

Regardless if set as required on the Agility Payment Method, driver’s license #, credit card #, and expiration date fields are not processed by the method

Multiple payments can be received for a single sales order transaction

Payments (including overpayments) are applied as Deposit on order for the transaction, regardless of how the Agility Payment Method is set to process

The payment will be posted to G/L based on the Use branch cash account for POS setting on the Agility Payment Method

The user running the method must have Data Allocations granted for the applicable customers.

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

TransactionID comes from SalesOrderList or returned in SalesOrderCreate response

Version Deployed
v603

**Request body:**
```json
{
    "request": {
        "TransactionID": "",
        "SalesOrderPaymentRecordJSON": {
            "dsSalesOrderPayment": {
                "dtSalesOrderPayment": [
                    {
                        "PaymentMethod": "",
                        "PaymentID": "",
                        "AmountTendered": 0
                    }
                ]
            }
        }
    }
}
```

## SalesOrderPriceHoldApprove
`POST /Orders/SalesOrderPriceHoldApprove`

Purpose
Removes sales order items from price hold; approve items on price hold based on the OrderID and detail line item Sequence
Required Inputs

OrderID

Sequence

Optional Inputs

SendNotification

ReviewerID

Comment

Notes

To get the list of valid Sequences available for updating, use SalesOrderList to see the Sequence values used and which ItemCode each is tied to. DMSi recommends carefully choosing the Sequence to update by reviewing related data for each Sequence detail as an ItemCode can exist multiple times on a Sales Order, including individual entries for dimensions

A Price Hold Approval/Rejection Notification must be defined in Agility to send a notification

Comment and ReviewerID are populated on the notification

When the ReviewerID value matches a User ID in Agility, the Reviewer User Name on the notification is populated with the User Name value from the user record

If the ReviewerID value does not match a User ID in Agility, the Reviewer User Name on the notification is blank

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Valid values for OrderID come from SalesOrderList

Version Deployed
v550

**Request body:**
```json
{
    "request": {
        "OrderID": 0,
        "SalesOrderDetailApproveJSON": {
            "dsSalesOrderDetail": {
                "dtSalesOrderDetail": [
                    {
                        "Sequence": 1,
                        "SendNotification": "",
                        "ReviewerID": "",
                        "Comment": ""
                    },
                    {
                        "Sequence": 2,
                        "SendNotification": ""
                    }
                ]
            }
        }
    }
}
```

## SalesOrderPriceHoldReject
`POST /Orders/SalesOrderPriceHoldReject`

Purpose
Denies removal of sales order items from price hold based on the OrderID and detail line item Sequence and sends a suggested price for approval
Required Inputs

OrderID

Sequence

Optional Inputs

SendNotification

ReviewerID

Comment

SuggestedPrice

SuggestedPriceUOM

Notes

To get the list of valid Sequences available for updating, use SalesOrderList to see the Sequence values used and which ItemCode each is tied to. DMSi recommends carefully choosing the Sequence to update by reviewing related data for each Sequence detail as an ItemCode can exist multiple times on a Sales Order, including individual entries for dimensions

Include a SuggestedPrice that would allow approval of the item

A Price Hold Approval/Rejection Notification must be defined in Agility to send a notification

Comment and ReviewerID are populated on the notification

When the ReviewerID value matches a User ID in Agility, the Reviewer User Name on the notification is populated with the User Name value from the user record

If the ReviewerID value does not match a User ID in Agility, the Reviewer User Name on the notification is blank

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Valid values for OrderID come from SalesOrderList

Version Deployed
v550

**Request body:**
```json
{
    "request": {
        "OrderID": 0,
        "SalesOrderDetailRejectJSON": {
            "dsSalesOrderDetail": {
                "dtSalesOrderDetail": [
                    {
                        "Sequence": 1,
                        "SuggestedPrice": 0,
                        "SuggestedPriceUOM": "",
                        "SendNotification": "",
                        "ReviewerID": "",
                        "Comment": ""
                    }
                ]
            }
        }
    }
}
```

## SalesOrderUpdate
`POST /Orders/SalesOrderUpdate`

Purpose
Updates header information and/or adds new items to an existing sales order
Required Inputs

OrderID

Value Required
The following inputs require a value due to data type:

Charge

PriceOverride

OrderCost

PrintMsgOnForms

PrintMsgOnFormsOverride

SendMsgToWMS

SendMsgToWMSOverride

PrintFlag

SundryCost

SundryCostOverride

HotNote

OrderNoteSequence

Optional Inputs

All fields in dtOrderHeaderUpdateRequest

Remaining fields in dtOrderHeaderNotesRequest, dtOrderItemRequest, dtOrderItemDimensionRequest, dtOrderItemComponentRequest not already referenced

Notes

This method allows specific fields on the sales order header to be updated

This method allows new items to be added to an existing sales order, including parent items with components work order is created for the configured parent item and non-stock items. Existing items may not be updated or deleted by this method

When creating a note, the OrderNote tag is required in dtOrderHeaderNotesRequest

The OrderNoteSequence tag must not be sent or have a value of 0 to create a new note.

When updating a note, the OrderNoteSequence tag is required in dtOrderHeaderNotesRequest. The following additional rules apply:

If the OrderNote tag is blank or not sent, no update is made to the Order Note value.

If the HotNote tag is not sent, no update is made to the Hot Note setting.

If the ReminderDate tag is not sent, no update is made to the Remind Date.

If the ReminderDate tag is blank, the Remind Date is removed.

Each new detail must have OrderQty > 0

If UseItemConvertPriceAndUOM = true, the process converts the price and price UOM to the order qty UOM if all the following criteria are met:

PriceOverride = false

Convert price/price UOM to match order field on the item record is set in Agility

The UOM sent in the dtOrderItemRequest does not match the SO/Quote UOM on the item record in Agility

When ordering by dimension, values for Thickness, Width, and/or Length are required based on item type. In addition, the OrderQty and UOM must also be specified at the dimension level

When ordering a parent item with components, OrderItemSequence, ComponentSequence, ItemCode, and OrderQty are required in dtOrderItemComponentRequest

If the ShipVia, SaleType, or RouteID values sent in are invalid, the entire request fails and no updates are completed

When a TemplateItemCode is populated in the dtOrderItemRequest, the ItemCode is ignored. The following fields apply to the non-stock item created from the TemplateItemCode value: NonStockSize, NonStockDescription, NonStockExtDescription, NonStockCopyCustomFields. Unless the NonStockCopyCustomFields is set to true the system does not copy custom item fields.

If the SalesAgent tags from the dtOrderHeaderRequest is not sent in, no update is made to the sales agent information on the order.

If the SalesAgentPctOfOrder tags from the dtOrderHeaderRequest are sent in with a value of 0, No update is made to the sales agent information on the order. If any SalesAgentPctOfOrder tags are sent in with a valid value, all other sales agent percentages will be cleared.

Use the PartNumber field if the item being ordered is a customer part number. When populated the PartNumber is read first before the ItemCode using the following search hierarchy.

Search the item cross reference hierarchy for a match to the PartNumber submitted in the request. If a match is found the sales order detail item cross reference field is populated with the PartNumber value.

Search the item cross reference hierarchy for a match to the ItemCode submitted in the API request. If a match is found the sales order detail item cross reference field is populated with the ItemCode value.

Search for a valid Agility item code that matches the ItemCode submitted in the API request.

Search for a valid Agility item code that matches the PartNumber submitted in the API request.

This method allows customer charges and order costs to be added or updated on an existing sales order. If either Charge = True or OrderCost = True in the dtOrderItemRequest, then the ItemCode value must correspond to a valid Charge type or Cost type in Agility, and the Price is the amount applied to the order. All other tags in the dtOrderItemRequest are ignored.

You can only add or update customer charges and order costs with the record type of header charge, header charge allocated to detail, header charge calculated by item detail, or header cost.

The customer charge or order cost is added or updated with a fixed amount basis.

If the Price is greater than or equal to 0, then the customer charge or order cost applies as a Charge or Cost, respectively.

If the Price is less than 0, then the customer charge or order cost applies as a Refund or Cost Reduction, respectively.

The ‘Require Template for Non-Stock’ security action will not be read

If a value is sent in both the ItemCode and TemplateItemCode tags

ItemCode value will not be read

TemplateItemCode value will be read and used to create a non-stock item

TemplateItemCode value must be active, saleable, no order restrictions, and not a BOM parent item

If any of the following tags are not sent or sent with a blank value, values assigned to the TemplateItemCode sent in the API will be used when creating the non-stock item

NonStockSize

NonStockDescription

NonStockExtDescription

NonStockProductGroupMajor

NonStockProductGroupMinor

NonStockPriceCodeMajor

NonStockPriceCodeMinor

NonStockCost

NonStockCostUOM

If a value is sent for the NonStockCost tag, then a value must also be sent for the NonStockCostUOM tag

The AddPermanentDetailGroupID tag determines if a permanent detail group record is created for the detail group received in the request

To update header information only, exclude the dtOrderItemRequest and dtOrderItemDimensionRequest data tables from the request

If CommitFromSpecifiedLocation = true, the CommitLocation value is read and used to commit the item at the specified location if sufficient available quantity exists. This functionality should only be used as the exception if there is a specific business reason to override the commit settings on the item record and/or commit rules defined in Tran Criteria.

If the value in the CommitLocation tag corresponds to a location or a location and sublocation that has insufficient quantity to fill the full order, the system reads the ‘Commit all – do not backorder’ flag on the item record and either commits available quantity from the branch level and backorders unavailable quantity or creates negative available quantity.

If a commit location is specified for a parent item, all of the parent’s components are committed from that location. The parent item continues to be backordered until the work order is completed in work order completion or when an ‘auto-complete’ parent is included in a pick file or shipment. At that time, the completed parent is put into stock at the defined default location on the item record.

If CommitFromSpecifiedLocation = false, the system follows the current commit rules.

If CommitFromSpecifiedLocation = true but no valid location or location and sublocation is provided in the CommitLocation tag, the request fails and no new detail lines are created.

When entering a location and sublocation value in the CommitLocation tag, follow the format "Location Sublocation".

If the sale type is modified, the system applies the default ship via, freight terms, and route ID based on the new sale type or customer settings. Additionally, detail fill-from sources, tax calculations, charges and costs, and other updates are applied automatically based on existing logic. Sale type changes are validated against current business rules, including the sales order status and linked transactions.

If the route ID is modified, including when set automatically based on the new sale type, the system recalculates the expected delivery date based on the new route ID. If the expected delivery date field is modified, the 'Expected delivery date override' field is set automatically.

Repricing for all items on the order, including overridden prices, occurs when the sale type changes and the Reprice tag is set to true. Prices and discounts are adjusted with default settings for all non-invoiced line items on the sales order. This uses customer standard price, the current date for the reprice date, and the sales order price level. If the sale type is not updated or the Reprice tag is set to false or omitted, items are not repriced on the order.

If any of the ship-to address tags are sent in with a value, the system clears out the other ship-to address fields instead of using the default values. For example, if you send in a value in only the ShipToAddress1tag, the city and state on the existing SO will be updated to blank. If you override a ship-to address, you must send in all relevant ship-to address tags. The tags included in the ship-to address fields are as follows: ShipToAddress1, ShipToAddress2, ShipToAddress3, ShipToCity, ShipToState, ShipToZip, ShipToCountry.

If all ship-to address tags have a value of blank, or none of them are sent in the request, then the system retains the existing ship-to address values.

If CreatePermanentShipTo = true, the process attempts to create a new ship-to record and assigns it to the current sales order. If the ship-to name or ship-to address fields are not updated, or the permanent ship-to cannot be created based on Agility rules, the new ship-to will not be created.

Relationships

ContextId comes from Login

Alternate branches come from BranchList

Valid values for OrderID come from SalesOrderList or from NewOrderID returned from SalesOrderCreate

This method contains a parent/child relationship between dtOrderItemRequest and dtOrderitemDimensionRequest. Please see the Parent/Child Relationships topic for more information

Version Deployed
v550

**Request body:**
```json
{
    "request": {
        "OrderID": 0,
        "OrderHeaderUpdateJSON": {
            "dsOrderHeaderUpdateRequest": {
                "dtOrderHeaderUpdateRequest": [
                    {
                        "TransactionReference": "",
                        "TransactionJob": "",
                        "OrderedBy": "",
                        "CustomerPurchaseOrder": "",
                        "ShipVia": "",
                        "SaleType": "",
                        "RouteID": "",
                        "ExpectedDate": null,
                        "APISourceID": "",
                        "Reprice": false,
                        "ShipToName": "",
                        "ShipToAddress1": "",
                        "ShipToAddress2": "",
                        "ShipToAddress3": "",
                        "ShipToCity": "",
                        "ShipToState": "",
                        "ShipToZip": "",
                        "ShipToCountry": "",
                        "ShipToPhone": "",
                        "CreatePermanentShipTo": false,
                        "MiscField1": "",
                        "MiscField2": "",
                        "MiscField3": "",
                        "MiscField4": "",
                        "MiscField5": "",
                        "MiscField6": "",
                        "MiscField7": "",
                        "MiscField8": "",
                        "MiscField9": "",
                        "MiscField10": "",
                        "MiscField11": "",
                        "MiscField12": "",
                        "MiscDate1": null,
                        "MiscDate2": null,
                        "SalesAgent1": "",
                        "SalesAgent2": "",
                        "SalesAgent3": "",
                        "SalesAgent4": "",
                        "SalesAgent5": "",
                        "SalesAgent6": "",
                        "SalesAgent1PctOfOrder": 0,
                        "SalesAgent2PctOfOrder": 0,
                        "SalesAgent3PctOfOrder": 0,
                        "SalesAgent4PctOfOrder": 0,
                        "SalesAgent5PctOfOrder": 0,
                        "SalesAgent6PctOfOrder": 0
                    }
                ],
                "dtOrderHeaderNotesRequest": [
                    {
                        "OrderNoteSequence": 0,
                        "OrderNote": "",
                        "HotNote": false,
                        "ReminderDate": ""
                    }
                ]
            }
        },
        "dsOrderItemRequest": {
            "dtOrderItemRequest": [
                {
                    "Sequence": 1,
                    "ItemCode": "",
                    "OrderQty": 1,
                    "UOM": "",
                    "Charge": false,
                    "Price": 0,
                    "PriceUOM": "",
                    "PriceOverride": false,
                    "UseItemConvertPriceAndUOM": false,
                    "OrderCost": false,
                    "CustomerPOLineNumber": "",
                    "DepartmentName": "",
                    "DepartmentNumber": "",
                    "PartNumber": "",
                    "SKU": "",
                    "UPCCode": "",
                    "ItemMessage": "",
                    "PrintMsgOnForms": false,
                    "PrintMsgOnFormsOverride": false,
                    "SendMsgToWMS": false,
                    "SendMsgToWMSOverride": false,
                    "APIPriceSourceType": "",
                    "APIPriceSourceRef": "",
                    "DetailGroupID": "",
                    "AddPermanentDetailGroupID": false,
                    "UseGroupAsDefaultNewItems": false,
                    "Size": "",
                    "Description": "",
                    "CommitFromSpecifiedLocation": false,
                    "CommitLocation": ""
                },
                {
                    "Sequence": 2,
                    "TemplateItemCode": "",
                    "NonStockSize": "",
                    "NonStockDescription": "",
                    "NonStockExtDescription": "",
                    "NonStockCopyCustomFields": true,
                    "NonStockSupplierID": "",
                    "NonStockSupplierShipFromSequence": 1,
                    "NonStockSupplierPartNumber": "",
                    "NonStockProductGroupMajor": "",
                    "NonStockProductGroupMinor": "",
                    "NonStockPriceCodeMajor": "",
                    "NonStockPriceCodeMinor": "",
                    "NonStockCost": 0,
                    "NonStockCostUOM": "",
                    "OrderQty": 1,
                    "UOM": "",
                    "Charge": false,
                    "Price": 0,
                    "PriceUOM": "",
                    "PriceOverride": false,
                    "UseItemConvertPriceAndUOM": false,
                    "OrderCost": false,
                    "CustomerPOLineNumber": "",
                    "DepartmentName": "",
                    "DepartmentNumber": "",
                    "PartNumber": "",
                    "SKU": "",
                    "UPCCode": "",
                    "ItemMessage": "",
                    "PrintMsgOnForms": false,
                    "PrintMsgOnFormsOverride": false,
                    "SendMsgToWMS": false,
                    "SendMsgToWMSOverride": false,
                    "APIPriceSourceType": "",
                    "APIPriceSourceRef": "",
                    "DetailGroupID": "",
                    "AddPermanentDetailGroupID": false,
                    "UseGroupAsDefaultNewItems": false,
                    "Size": "",
                    "Description": "",
                    "CommitFromSpecifiedLocation": false,
                    "CommitLocation": ""
                },
                {
                    "ItemCode": "",
                    "Charge": true,
                    "Price": 0
                },
                {
                    "ItemCode": "",
                    "OrderCost": true,
                    "Price": 0,
                    "OrderCostSupplierID": ""
                }
            ],
            "dtOrderItemDimensionRequest": [
                {
                    "Sequence": 0,
                    "Thickness": 0,
                    "Width": 0,
                    "Length": 0,
                    "OrderQty": 0,
                    "UOM": "",
                    "Price": 0,
                    "PriceUOM": "",
                    "PriceOverride": false
                }
            ]
        },
        "dsOrderItemComponentRequest": {
            "dtOrderItemComponentRequest": [
                {
                    "OrderItemSequence": 0,
                    "ComponentSequence": 0,
                    "BomType": "",
                    "ItemCode": "",
                    "PartNumber": "",
                    "OrderQty": 0,
                    "Thickness": 0,
                    "Width": 0,
                    "Length": 0,
                    "PieceCount": 0,
                    "TallyUOM": "",
                    "PrintFlag": false,
                    "SundryCost": 0,
                    "SundryCostOverride": false,
                    "ItemMessage": "",
                    "PrintMsgOnForms": false,
                    "PrintMsgOnFormsOverride": false,
                    "UOM": "",
                    "ShipLoose": true,
                    "Size": "",
                    "Description": ""
                }
            ]
        }
    }
}
```

## SalesOrderUpdateValidate
`POST /Orders/SalesOrderUpdateValidate`

Purpose
Validates updating header information and/or adding new items to an existing sales order
Required Inputs

OrderID

Value Required
The following inputs require a value due to data type:

Charge

PriceOverride

OrderCost

PrintMsgOnForms

PrintMsgOnFormsOverride

SendMsgToWMS

SendMsgToWMSOverride

PrintFlag

SundryCost

SundryCostOverride

HotNote

OrderNoteSequence

Optional Inputs

All fields in  dtOrderHeaderUpdateRequest
Remaining fields in dtOrderHeaderNotesRequest, dtOrderItemRequest, dtOrderItemDimensionRequest, dtOrderItemComponentRequest not already referenced

Notes

Refer to the Notes in the SalesOrderUpdate method.

Review the dsAuditResults to identify changes needed in the request in order for the validation to be successful.

Relationships

ContextId comes from Login

Alternate branches come from BranchList

Refer to the Relationships section in the SalesOrderUpdate method

Version Deployed
v553

**Request body:**
```json
{
    "request": {
        "OrderID": 0,
        "OrderHeaderUpdateJSON": {
            "dsOrderHeaderUpdateRequest": {
                "dtOrderHeaderUpdateRequest": [
                    {
                        "TransactionReference": "",
                        "TransactionJob": "",
                        "OrderedBy": "",
                        "CustomerPurchaseOrder": "",
                        "ShipVia": "",
                        "SaleType": "",
                        "RouteID": "",
                        "ExpectedDate": null,
                        "APISourceID": "",
                        "Reprice": false,
                        "ShipToName": "",
                        "ShipToAddress1": "",
                        "ShipToAddress2": "",
                        "ShipToAddress3": "",
                        "ShipToCity": "",
                        "ShipToState": "",
                        "ShipToZip": "",
                        "ShipToCountry": "",
                        "ShipToPhone": "",
                        "CreatePermanentShipTo": false,
                        "MiscField1": "",
                        "MiscField2": "",
                        "MiscField3": "",
                        "MiscField4": "",
                        "MiscField5": "",
                        "MiscField6": "",
                        "MiscField7": "",
                        "MiscField8": "",
                        "MiscField9": "",
                        "MiscField10": "",
                        "MiscField11": "",
                        "MiscField12": "",
                        "MiscDate1": null,
                        "MiscDate2": null,
                        "SalesAgent1": "",
                        "SalesAgent2": "",
                        "SalesAgent3": "",
                        "SalesAgent4": "",
                        "SalesAgent5": "",
                        "SalesAgent6": "",
                        "SalesAgent1PctOfOrder": 0,
                        "SalesAgent2PctOfOrder": 0,
                        "SalesAgent3PctOfOrder": 0,
                        "SalesAgent4PctOfOrder": 0,
                        "SalesAgent5PctOfOrder": 0,
                        "SalesAgent6PctOfOrder": 0
                    }
                ],
                "dtOrderHeaderNotesRequest": [
                    {
                        "OrderNoteSequence": 0,
                        "OrderNote": "",
                        "HotNote": false,
                        "ReminderDate": ""
                    }
                ]
            }
        },
        "dsOrderItemRequest": {
            "dtOrderItemRequest": [
                {
                    "Sequence": 1,
                    "ItemCode": "",
                    "OrderQty": 1,
                    "UOM": "",
                    "Charge": false,
                    "Price": 0,
                    "PriceUOM": "",
                    "PriceOverride": false,
                    "OrderCost": false,
                    "CustomerPOLineNumber": "",
                    "DepartmentName": "",
                    "DepartmentNumber": "",
                    "PartNumber": "",
                    "SKU": "",
                    "UPCCode": "",
                    "ItemMessage": "",
                    "PrintMsgOnForms": false,
                    "PrintMsgOnFormsOverride": false,
                    "SendMsgToWMS": false,
                    "SendMsgToWMSOverride": false,
                    "APIPriceSourceType": "",
                    "APIPriceSourceRef": "",
                    "DetailGroupID": "",
                    "AddPermanentDetailGroupID": false,
                    "UseGroupAsDefaultNewItems": false,
                    "Size": "",
                    "Description": "",
                    "CommitFromSpecifiedLocation": null,
                    "CommitLocation": ""
                },
                {
                    "Sequence": 2,
                    "TemplateItemCode": "",
                    "NonStockSize": "",
                    "NonStockDescription": "",
                    "NonStockExtDescription": "",
                    "NonStockCopyCustomFields": true,
                    "NonStockSupplierID": "",
                    "NonStockSupplierShipFromSequence": 1,
                    "NonStockSupplierPartNumber": "",
                    "NonStockProductGroupMajor": "",
                    "NonStockProductGroupMinor": "",
                    "NonStockPriceCodeMajor": "",
                    "NonStockPriceCodeMinor": "",
                    "NonStockCost": 0,
                    "NonStockCostUOM": "",
                    "OrderQty": 1,
                    "UOM": "",
                    "Charge": false,
                    "Price": 0,
                    "PriceUOM": "",
                    "PriceOverride": false,
                    "OrderCost": false,
                    "CustomerPOLineNumber": "",
                    "DepartmentName": "",
                    "DepartmentNumber": "",
                    "PartNumber": "",
                    "SKU": "",
                    "UPCCode": "",
                    "ItemMessage": "",
                    "PrintMsgOnForms": false,
                    "PrintMsgOnFormsOverride": false,
                    "SendMsgToWMS": false,
                    "SendMsgToWMSOverride": false,
                    "APIPriceSourceType": "",
                    "APIPriceSourceRef": "",
                    "DetailGroupID": "",
                    "AddPermanentDetailGroupID": false,
                    "UseGroupAsDefaultNewItems": false,
                    "Size": "",
                    "Description": "",
                    "CommitFromSpecifiedLocation": null,
                    "CommitLocation": ""
                },
                {
                    "ItemCode": "",
                    "OrderCost": true,
                    "Price": 0,
                    "OrderCostSupplierID": ""
                }
            ],
            "dtOrderItemDimensionRequest": [
                {
                    "Sequence": 0,
                    "Thickness": 0,
                    "Width": 0,
                    "Length": 0,
                    "OrderQty": 0,
                    "UOM": "",
                    "Price": 0,
                    "PriceUOM": "",
                    "PriceOverride": false
                }
            ]
        },
        "dsOrderItemComponentRequest": {
            "dtOrderItemComponentRequest": [
                {
                    "OrderItemSequence": 0,
                    "ComponentSequence": 0,
                    "BomType": "",
                    "ItemCode": "",
                    "PartNumber": "",
                    "OrderQty": 0,
                    "Thickness": 0,
                    "Width": 0,
                    "Length": 0,
                    "PieceCount": 0,
                    "TallyUOM": "",
                    "PrintFlag": false,
                    "SundryCost": 0,
                    "SundryCostOverride": false,
                    "ItemMessage": "",
                    "PrintMsgOnForms": false,
                    "PrintMsgOnFormsOverride": false,
                    "UOM": "",
                    "ShipLoose": true,
                    "Size": "",
                    "Description": ""
                }
            ]
        }
    }
}
```

## WorkOrderMessageCreate
`POST /Orders/WorkOrderMessageCreate`

Purpose
Creates a sales order work order item message in the branch the user is logged into
Required Inputs

TranID

MessageText

MessageType

TranSeq (for detail transactions messages)

Optional Inputs

PrintOnForms

Notes

MessageText can send a maximum of 1000 characters

Valid values for MessageType are H, Header, F, Footer, D, and Detail

When PrintOnForms is set to true, all eligible forms are set to print the new message

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v554

**Request body:**
```json
{
    "request": {
        "MessageCreateJSON": {
            "dsMessageCreate": {
                "dtMessageCreate": [
                    {
                        "TranID": 0,
                        "TranSeq": 1,
                        "MessageText": "",
                        "MessageType": "",
                        "PrintOnForms": true
                    }
                ]
            }
        }
    }
}
```

---

# Pricing Service  (3 methods)

## ApprovedItemsCustomerPricingInChunksList
`POST /Pricing/ApprovedItemsCustomerPricingInChunksList`

Purpose
Returns item specific information as well as the most specific price for the customer and ship-to specified for a group of items approved for sale to the specified customer
Required Inputs

CustomerID

RecordFetchLimit

Optional Inputs

ShipToSequence

SaleType

SearchBy

SearchValue

ItemGroupMajor

ItemGroupMinor

IncludeNonStock

IncludeNonSaleable

ChunkStartPointer

UseOrderRestrictions

Notes

The method allows the user to search for and select items based on ItemGroupMajor, ItemGroupMajor and ItemGroupMinor combination, SearchBy or to request the information for all items based on the customer/ship-to and other input values

Valid SearchBy options are Item Code, Size, Description, Ext. Description Contains, and Keyword Search.

The UseOrderRestrictions field in the API request controls if items with a qualifying order restriction record defined in the Agility Transaction Criteria window are included in the list of items retrieved in the response.

If the field is not included in the request the system default is to exclude items with qualifying order restrictions from being returned in the response.

When the IncludeNonStock field is excluded from the API request, the system excludes items with the Stock field unset in Item Maintenance.

When the IncludeNonSaleable field is excluded from the API request, the system excludes with the Non-saleable field set in Item Maintenance.

This method allows a user to set a RecordFetchLimit in the request. The number of TotalRowsFetched returned in the response is the number of unique items returned. For dimension type items it does not include dimension records in this count. Therefore, when processing includes dimension type records, consideration should be given when setting the RecordFetchLimit as processing time will be affected. Please see the Data chunking topic for more information.

The method returns item information in the Display UOM defined on the item record, with the following exceptions:

For the main item record of dimension type items where the display UOM is set to the piece reference UOM, the system returns item information in the stocking UOM, since the piece reference is invalid for the main item record.

For sheet good and specific length lumber items with a display UOM of UNIT, the system returns item information in the stocking UOM, since various piece counts may apply.

The system includes quantities for alternate items assigned to component items when calculating the MaxProductionUnits value for a BOM Parent item when all of the following conditions are met:

Branch Parameter Include alternates when calculating maximum production units on the Inventory tab is set.

If the alternate item has the Applies to work orders from sales orders option set and the Auto order option is set to ‘Auto order at work order entry’ in Alternates Maintenance.

If the Stocking UOM on the component item and alternate item are not the same, there must be a UOM conversion setup on the alternate item to get back to the stocking UOM on the component item.

If the component is a dimension type item, the alternate item must be setup for the overall 00x00x00 record

Relationships

ContextId and Branch come from Login

Valid values for ItemGroupMajor come from ItemGroupMajorList or ItemGroupMinorList

Valid values for ItemGroupMinor come from ItemGroupMinorList

Valid values for SaleType come from SaleTypesList

Version Deployed
v600

**Request body:**
```json
{
    "request": {
        "CustomerPricingRequestJSON": {
            "dsCustomerPricingRequest": {
                "dtCustomerPricingRequest": [
                    {
                        "CustomerID": "",
                        "ShipToSequence": 1,
                        "SaleType": "",
                        "SearchBy": "",
                        "SearchValue": "",
                        "ItemGroupMajor": "",
                        "ItemGroupMinor": "",
                        "IncludeNonStock": true,
                        "IncludeNonSaleable": true,
                        "RecordFetchLimit": 0,
                        "ChunkStartPointer": 0,
                        "UseOrderRestrictions": true
                    }
                ]
            }
        }
    }
}
```

## ItemCustomerPricingList
`POST /Pricing/ItemCustomerPricingList`

Purpose
Returns item related information as well as the most specific price for the customer and ship-to specified for a group of items
Required Inputs

CustomerID

ShiptoSequence

IncludeNonStock

IncludeNonsaleable

RecordFetchLimit

Optional Inputs

SaleType

SearchBy

SearchValue

ItemGroupMajor

ItemGroupMinor

Notes

The method allows the user to search for and select items based on ItemGroupMajor, ItemGroupMajor and ItemGroupMinor combination, SearchBy or to request the information for all items in sets.  Valid SearchBy options are Item Code, Size, Description, Ext. Description Contains, and Keyword Search

This method allows a user to request a specific number of records. Please see the Data chunking topic for more information

The method returns item information in the Display UOM defined on the item record, with the following exceptions:

For the main item record of dimension type items where the display UOM is set to the piece reference UOM, the system returns item information in the stocking UOM, since the piece reference is invalid for the main item record.

For sheet good and specific length lumber items with a display UOM of UNIT, the system returns item information in the stocking UOM, since various piece counts may apply

Relationships

ContextId and Branch come from Login

Valid values for ItemGroupMajor come from ItemGroupMajorList or ItemGroupMinorList

Valid values for ItemGroupMinor come from ItemGroupMinorList

Valid values for SaleType come from SaleTypesList

Version Deployed
v543

**Request body:**
```json
{
    "request": {
        "CustomerID": "",
        "ShipToSequence": 1,
        "SaleType": "",
        "SearchBy": "",
        "SearchValue": "",
        "ItemGroupMajor": "",
        "ItemGroupMinor": "",
        "IncludeNonStock": true,
        "IncludeNonSaleable": true,
        "RecordFetchLimit": 0
    }
}
```

## PriceInfoList
`POST /Pricing/PriceInfoList`

StartFragment
Purpose
Returns all pricing and discount records from the specified level in the hierarchy for the customer and items/dimensions specified
Required Inputs

CustomerID

ShiptoSequence

ItemCode for each record in the set of items to process

Optional Inputs

PriceTypeOption

SaleType

OrderQty

UOM in set of items to process; all fields in the set of dimensions to process

Notes

Valid values for PriceTypeOption are All, All Comb, Customer Pricing Comb, Customer Pricing, Standard Pricing Comb, Standard Pricing, Most Specific Comb, Most Specific, Special Pricing Comb and Special Pricing

Options that include Comb in the name return the net price as the gross price less any applicable discounts and do not return the discount records as separate records

Options that do not include Comb in the name return any applicable discount records as separate records and only return net price as 0 to indicate the net price was not calculated

When requesting for a dimensional item without specifying a dimension, the pricing records for the item and all dimensions are returned. When requesting for a dimensional item and specifying the dimension, the pricing records for that specific dimension only are returned. The values in Thickness, Width and Length returned identify which dimension the request was made for

When including a SaleType, only price records that apply to that SaleType (or the SaleType) are returned

DMSi strongly recommends reviewing the ItemAuditResults regardless of the ReturnCode value

The PriceInfoList method returns price record information in the Pricing UOM defined on the price record

For the main item record of dimension type items where the price UOM is set to the piece reference UOM, the method returns item information in the pricing UOM, since the piece reference is invalid for the main item record.

The PriceInfoList method returns a blank QtyBreakUOM when the pricing or discount record returned is Fixed for the Pricing Group or Customer

Relationships

Context ID and Branch come from Login

Valid values for ItemCode come from ItemsList or ItemsInChunksList. Additionally, the Thickness, Width and Length values also come from ItemsList or ItemsInChunksList for applicable item

Valid values for CustomerID come from CustomersList or CustomerShiptosList

Valid values for ShipToSequence come from CustomerShiptosList

Valid values for SaleType come from SaleTypesList

Version Deployed
v544

**Request body:**
```json
{
    "request": {
        "CustomerID": "",
        "ShiptoSequence": 1,
        "SaleType": "",
        "PriceTypeOption": "",
        "dsItemToProcessRequest": {
            "dtItemToProcessRequest": [
                {
                    "ItemCode": "",
                    "OrderQty": 0,
                    "UOM": ""
                }
            ],
            "dtItemDimensionToProcessRequest": [
                {
                    "ItemCode": "",
                    "Thickness": 0,
                    "Width": 0,
                    "Length": 0,
                    "OrderQty": 0,
                    "UOM": ""
                }
            ]
        }
    }
}
```

---

# Purchasing Service  (18 methods)

## PurchaseOrderCostPacketsDelete
`POST /Purchasing/PurchaseOrderCostPacketsDelete`

Purpose
Deletes cost packets from a specific purchase order
Required Inputs

PurchaseOrderID

CostType

Optional Inputs

SupplierID

Notes

For a cross reference to be sent in the CostType field, the related supplier must be specified in the SupplierID field.

If the SupplierID is invalid for the CostType cross reference, the deletion will fail.

The system ignores the SupplierID if a valid, non-cross reference CostType is sent in the request.

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v539

**Request body:**
```json
{
    "request": {
        "PurchaseOrderID": 0,
        "PurchaseOrderCostPacketsDeleteJSON": {
            "dsPurchaseOrderCostPacket": {
                "dtPurchaseOrderCostPacket": [
                    {
                        "CostType": "",
                        "SupplierID": ""
                    }
                ]
            }
        }
    }
}
```

## PurchaseOrderCostPacketsGet
`POST /Purchasing/PurchaseOrderCostPacketsGet`

Purpose
Returns a cost packet information for a specific purchase order
Required Inputs

PurchaseOrderID

Optional Inputs

N/A

Notes
N/A
Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v539

**Request body:**
```json
{
    "request": {
        "PurchaseOrderID": ""
    }
}
```

## PurchaseOrderCostPacketsUpdate
`POST /Purchasing/PurchaseOrderCostPacketsUpdate`

Purpose
Creates or updates purchase order cost packets
Required Inputs

PurchaseOrderID

CostType

PurchaseOrderCostPacketsUpdateJSON

Optional Inputs

N/A

Notes

Any fields not included in the PurchaseOrderCostPacketsUpdateJSON assume the default values of the existing cost packet.

To create a new cost packet on a purchase order, in addition to the required inputs, the following fields must be included: CostBasis, BasisAmount or FixedAmount.

When a cost packet is updated on a parent PO, the system reallocates the cost to the child purchase order(s).

When a SupplierID value matches more than one dispatch the system does not assign a dispatch ID based on the supplier.

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v539

**Request body:**
```json
{
    "request": {
        "PurchaseOrderID": "",
        "PurchaseOrderCostPacketsUpdateJSON": {
            "dsPurchaseOrderCostPacket": {
                "dtPurchaseOrderCostPacket": [
                    {
                        "CostType": "",
                        "CostBasis": "",
                        "BasisAmount": 0,
                        "FixedAmount": 0,
                        "SupplierID": "",
                        "AllocateBy": "",
                        "ApplyPerReceiving": true,
                        "PrintOnForm": false,
                        "DispatchID": 0,
                        "AssignDispatchIDBasedOnSupplier": true
                    }
                ]
            }
        }
    }
}
```

## PurchaseOrderCreate
`POST /Purchasing/PurchaseOrderCreate`

Purpose
Creates a new purchase order
Required Inputs

SupplierID

ItemCode for each detail

OrderQty for each detail

ShipFromSequence

PurchaseType

SendPOVia

Optional Inputs

Remaining fields in the dtPurchaseOrderHeader, PurchaseOrderHeaderNotes, dtPurchaseOrderItemRequest, and dtPurchaseOrderItemDimension not already referenced

Notes

At least 1 item must be sent in.

Each detail must have an OrderQty > 0.

An item must be active in the branch to be able to add the item to the purchase order.

If ordering by dimension, values for Thickness, Width, and/or Length are required based on item type. In addition, the OrderQty and UOM must also be specified at the dimension level.

If set on the Item Supplier record, the ‘Minimum order qty’ and ‘Min pack’ are not required to be met to create an item on a purchase order.

A value is required for inputs ShipFromSequence and PurchaseType when the branch supplier record does not have a default value defined.

A value is required for the input SendPOVia when included in the request. Valid values are Normal, EDI, and Don’t Send. A Supplier Reference record must exist to send the EDI value in the request.

When the input SendPOVia is not included in the request, this value defaults to EDI if a Supplier Reference record exists. Otherwise, it defaults to Normal.

Inputs for dtPurchaseOrderHeader set as required in Purchasing Parameters without a default defined value on the branch supplier record requires the purchase order to be updated.

The Purchasing Parameters flag ‘Display proposed sell price in detail entry’ must be enabled for the ProposedSellPrice input to create a record on the purchase order detail.

The Purchasing Parameters flag ‘Display supplier quoted cost in detail entry’ must be enabled for the SupplierQuotedCost and SupplierQuotedID inputs to create records on the purchase order detail.

A blank value sent in the request for character and date inputs results in that field on the Purchase Order being blank. The default value for a field, if applicable, does not get applied. Default values apply when an input is not included in the request.

To create a requesting purchase order for a branch transfer the following criteria are required:

The SupplierID input value must already be assigned as the shipping branch for the requesting branch in Branch Transfer Parameters.

The PurchaseType input value must affect inventory.

At least one item detail with a valid UOM in both branches is sent in the request.

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Valid values for SupplierID come from SupplierList

Valid values for ShipFromSequence come from SupplierShipfromsList

Valid values for ItemCode come from ItemsList

The NewOrderID returned from this method can be used in conjunction with PurchaseOrderGet to verify the new purchase order was created as expected

Version Deployed
v612

**Request body:**
```json
{
    "request": {
        "SupplierID": "",
        "PurchaseOrderJSON": {
            "dsPurchaseOrderHeader": {
                "dtPurchaseOrderHeader": [
                    {
                        "ShipFromSequence": 1,
                        "PurchaseType": "",
                        "OrderDate": "",
                        "CustomerID": "",
                        "ShipToSequence": 1,
                        "PaymentTermsCode": "",
                        "FreightTerms": "",
                        "PODescription": "",
                        "VerbalPO": "",
                        "Reference": "",
                        "POLabel": "",
                        "SendPOVia": "",
                        "Buyer1": "",
                        "Buyer2": "",
                        "ExpectedShipDate": "2024-11-01",
                        "ExpectedReceiptDate": "2024-11-08",
                        "ExpectedReceiptTime": "09:30",
                        "ExcludefromNetQtyUntil": "",
                        "UpdateLead": true,
                        "ShipVia": "",
                        "PickUpID": "",
                        "TrackingDate": "",
                        "ConfirmedBy": "",
                        "AllowChanges": true,
                        "AllowChangesUntilDate": "",
                        "AllowChangesUntilTime": "",
                        "APISourceID": ""
                    }
                ],
                "dtPurchaseOrderHeaderNotes": [
                    {
                        "OrderNote": "",
                        "HotNote": true,
                        "ReminderDate": "2025-01-02"
                    }
                ]
            },
            "dsPurchaseOrderItem": {
                "dtPurchaseOrderItem": [
                    {
                        "Sequence": 1,
                        "ItemCode": "",
                        "OrderQty": 0,
                        "UOM": "",
                        "Cost": 0,
                        "CostUOM": "",
                        "DueDate": "",
                        "ExpectedShipDate": "",
                        "ExpectedReceiptDate": "",
                        "Discount1": 0,
                        "Discount2": 0,
                        "Discount3": 0,
                        "GroupID": "",
                        "AddPermanentDetailGroupID": false,
                        "Description": "",
                        "ProposedSellPrice": 0,
                        "SellPriceUOM": "",
                        "Size": "",
                        "SupplierQuotedCost": false,
                        "SupplierQuoteID ": ""
                    },
                    {
                        "Sequence": 2,
                        "ItemCode": "",
                        "OrderQty": 0,
                        "UOM": "",
                        "Cost": 0,
                        "CostUOM": "",
                        "DueDate": "",
                        "ExpectedShipDate": "2024-11-01",
                        "ExpectedReceiptDate": "2024-11-08",
                        "Discount1": 0,
                        "Discount2": 0,
                        "Discount3": 0,
                        "GroupID": "",
                        "AddPermanentDetailGroupID": false,
                        "Description": "",
                        "ProposedSellPrice": 0,
                        "SellPriceUOM": "",
                        "Size": "",
                        "SupplierQuotedCost": false,
                        "SupplierQuoteID ": ""
                    }
                ],
                "dtPurchaseOrderItemDimension": [
                    {
                        "Sequence": 2,
                        "OrderQty": 0,
                        "UOM": "",
                        "Thickness": 0,
                        "Width": 0,
                        "Length": 0,
                        "PieceCount": 0,
                        "Cost": 0,
                        "CostUOM": ""
                    }
                ]
            }
        }
    }
}
```

## PurchaseOrderCreateValidate
`POST /Purchasing/PurchaseOrderCreateValidate`

Purpose
Validates the creation of a new purchase order
Required Inputs

SupplierID

ItemCode for each detail

OrderQty for each detail

ShipFromSequence

PurchaseType

SendPOVia

Optional Inputs

Remaining fields in the dtPurchaseOrderHeader, PurchaseOrderHeaderNotes, dtPurchaseOrderItemRequest, and dtPurchaseOrderItemDimension not already referenced

Notes

Refer to the Notes in the PurchaseOrderCreate method.

Review the dsAuditResults to identify changes in the request in order for the validation to be successful.

A value is required for inputs ShipFromSequence and PurchaseType when the branch supplier record does not have a default value defined.

A value is required for the input SendPOVia when included in the request. Valid values are Normal, EDI, and Don’t Send. A Supplier Reference record must exist to send the EDI value in the request.

When the input SendPOVia is not included in the request, this value defaults to EDI if a Supplier Reference record exists. Otherwise, it defaults to Normal.

Inputs for dtPurchaseOrderHeader set as required in Purchasing Parameters without a default defined value on the branch supplier record requires the purchase order to be updated.

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Refer to the relationships section in the PurchaseOrderCreate method

Version Deployed
v612

**Request body:**
```json
{
    "request": {
        "SupplierID": "",
        "PurchaseOrderJSON": {
            "dsPurchaseOrderHeader": {
                "dtPurchaseOrderHeader": [
                    {
                        "ShipFromSequence": 1,
                        "PurchaseType": "",
                        "OrderDate": "",
                        "CustomerID": "",
                        "ShipToSequence": 1,
                        "PaymentTermsCode": "",
                        "FreightTerms": "",
                        "PODescription": "",
                        "VerbalPO": "",
                        "Reference": "",
                        "POLabel": "",
                        "SendPOVia": "",
                        "Buyer1": "",
                        "Buyer2": "",
                        "ExpectedShipDate": "2024-11-01",
                        "ExpectedReceiptDate": "2024-11-08",
                        "ExpectedReceiptTime": "09:30",
                        "ExcludefromNetQtyUntil": "",
                        "UpdateLead": true,
                        "ShipVia": "",
                        "PickUpID": "",
                        "TrackingDate": "",
                        "ConfirmedBy": "",
                        "AllowChanges": true,
                        "AllowChangesUntilDate": "",
                        "AllowChangesUntilTime": "",
                        "APISourceID": ""
                    }
                ],
                "dtPurchaseOrderHeaderNotes": [
                    {
                        "OrderNote": "",
                        "HotNote": true,
                        "ReminderDate": "2025-01-02"
                    }
                ]
            },
            "dsPurchaseOrderItem": {
                "dtPurchaseOrderItem": [
                    {
                        "Sequence": 1,
                        "ItemCode": "",
                        "OrderQty": 0,
                        "UOM": "",
                        "Cost": 0,
                        "CostUOM": "",
                        "DueDate": "",
                        "ExpectedShipDate": "",
                        "ExpectedReceiptDate": "",
                        "Discount1": 0,
                        "Discount2": 0,
                        "Discount3": 0,
                        "GroupID": "",
                        "AddPermanentDetailGroupID": false,
                        "Description": "",
                        "ProposedSellPrice": 0,
                        "SellPriceUOM": "",
                        "Size": "",
                        "SupplierQuotedCost": false,
                        "SupplierQuoteID ": ""
                    },
                    {
                        "Sequence": 2,
                        "ItemCode": "",
                        "OrderQty": 0,
                        "UOM": "",
                        "Cost": 0,
                        "CostUOM": "",
                        "DueDate": "",
                        "ExpectedShipDate": "2024-11-01",
                        "ExpectedReceiptDate": "2024-11-08",
                        "Discount1": 0,
                        "Discount2": 0,
                        "Discount3": 0,
                        "GroupID": "",
                        "AddPermanentDetailGroupID": false,
                        "Description": "",
                        "ProposedSellPrice": 0,
                        "SellPriceUOM": "",
                        "Size": "",
                        "SupplierQuotedCost": false,
                        "SupplierQuoteID ": ""
                    }
                ],
                "dtPurchaseOrderItemDimension": [
                    {
                        "Sequence": 2,
                        "OrderQty": 0,
                        "UOM": "",
                        "Thickness": 0,
                        "Width": 0,
                        "Length": 0,
                        "PieceCount": 0,
                        "Cost": 0,
                        "CostUOM": ""
                    }
                ]
            }
        }
    }
}
```

## PurchaseOrderDetailsCreate
`POST /Purchasing/PurchaseOrderDetailsCreate`

Purpose
Creates a new detail record on an existing purchase order
Required Inputs

PurchaseOrderID

ItemCode for each detail

OrderQty for each detail

Optional Inputs

Remaining fields in the PurchaseOrderItem and PurchaseOrderItemDimension not already referenced

Notes

At least 1 item must be sent in.

Each detail must have an OrderQty > 0.

An item must be active in the branch to be able to add the item to the purchase order.

If ordering by dimension, values for Thickness, Width, and/or Length are required based on item type. In addition, the OrderQty and UOM must also be specified at the dimension level.

If set on the Item Supplier record, the ‘Minimum order qty’ and ‘Min pack’ are not required to be met to create an item on a purchase order.

A blank value sent in the request for character and date inputs results in that field on the Purchase Order Detail being blank. The default value for a field, if applicable, does not get applied. Default values apply when an input is not included in the request.

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Valid values for ItemCode come from ItemsList

Version Deployed
v613

**Request body:**
```json
{
    "request": {
        "PurchaseOrderID": 0,
        "PurchaseOrderDetailsCreateJSON": {
            "dsPurchaseOrderItem": {
                "dtPurchaseOrderItem": [
                    {
                        "Sequence": 1,
                        "ItemCode": "",
                        "OrderQty": 0,
                        "UOM": "",
                        "Cost": 0,
                        "CostUOM": "",
                        "DueDate": "",
                        "ExpectedShipDate": "",
                        "ExpectedReceiptDate": "",
                        "Discount1": 0,
                        "Discount2": 0,
                        "Discount3": 0,
                        "GroupID": "",
                        "AddPermanentDetailGroupID": false,
                        "Description": "",
                        "ProposedSellPrice": 0,
                        "SellPriceUOM": "",
                        "Size": "",
                        "SupplierQuotedCost": false,
                        "SupplierQuoteID ": ""
                    },
                    {
                        "Sequence": 2,
                        "ItemCode": "",
                        "OrderQty": 0,
                        "UOM": "",
                        "Cost": 0,
                        "CostUOM": "",
                        "DueDate": "",
                        "ExpectedShipDate": "",
                        "ExpectedReceiptDate": "",
                        "Discount1": 0,
                        "Discount2": 0,
                        "Discount3": 0,
                        "GroupID": "",
                        "AddPermanentDetailGroupID": false,
                        "Description": "",
                        "ProposedSellPrice": 0,
                        "SellPriceUOM": "",
                        "Size": "",
                        "SupplierQuotedCost": false,
                        "SupplierQuoteID ": ""
                    }
                ],
                "dtPurchaseOrderItemDimension": [
                    {
                        "Sequence": 2,
                        "OrderQty": 0,
                        "UOM": "",
                        "Thickness": 0,
                        "Width": 0,
                        "Length": 0,
                        "PieceCount": 0,
                        "Cost": 0,
                        "CostUOM": ""
                    }
                ]
            }
        }
    }
}
```

## PurchaseOrderDetailsCreateValidate
`POST /Purchasing/PurchaseOrderDetailsCreateValidate`

Purpose
Validates the creation of a new detail record on an existing purchase order
Required Inputs

PurchaseOrderID

ItemCode for each detail

OrderQty for each detail

Optional Inputs

Remaining fields in the PurchaseOrderItem and PurchaseOrderItemDimension not already referenced

Notes

Refer to the Notes in the PurchaseOrderDetailsCreate method.

Review the dsAuditResults to identify changes in the request in order for validation to be successful.

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Refer to the relationships section in the PurchaseOrderCreate method

Version Deployed
v613

**Request body:**
```json
{
    "request": {
        "PurchaseOrderID": 0,
        "PurchaseOrderDetailsCreateJSON": {
            "dsPurchaseOrderItem": {
                "dtPurchaseOrderItem": [
                    {
                        "Sequence": 1,
                        "ItemCode": "",
                        "OrderQty": 0,
                        "UOM": "",
                        "Cost": 0,
                        "CostUOM": "",
                        "DueDate": "",
                        "ExpectedShipDate": "",
                        "ExpectedReceiptDate": "",
                        "Discount1": 0,
                        "Discount2": 0,
                        "Discount3": 0,
                        "GroupID": "",
                        "AddPermanentDetailGroupID": false,
                        "Description": "",
                        "ProposedSellPrice": 0,
                        "SellPriceUOM": "",
                        "Size": "",
                        "SupplierQuotedCost": false,
                        "SupplierQuoteID ": ""
                    },
                    {
                        "Sequence": 2,
                        "ItemCode": "",
                        "OrderQty": 0,
                        "UOM": "",
                        "Cost": 0,
                        "CostUOM": "",
                        "DueDate": "",
                        "ExpectedShipDate": "",
                        "ExpectedReceiptDate": "",
                        "Discount1": 0,
                        "Discount2": 0,
                        "Discount3": 0,
                        "GroupID": "",
                        "AddPermanentDetailGroupID": false,
                        "Description": "",
                        "ProposedSellPrice": 0,
                        "SellPriceUOM": "",
                        "Size": "",
                        "SupplierQuotedCost": false,
                        "SupplierQuoteID ": ""
                    }
                ],
                "dtPurchaseOrderItemDimension": [
                    {
                        "Sequence": 2,
                        "OrderQty": 0,
                        "UOM": "",
                        "Thickness": 0,
                        "Width": 0,
                        "Length": 0,
                        "PieceCount": 0,
                        "Cost": 0,
                        "CostUOM": ""
                    }
                ]
            }
        }
    }
}
```

## PurchaseOrderDetailsDelete
`POST /Purchasing/PurchaseOrderDetailsDelete`

Purpose
Deletes an existing detail record on an existing purchase order
Required Inputs

PurchaseOrderID

DeleteDetails

KeepTranDetailTaggedForPO

Optional Inputs

N/A

Notes

The DeleteDetails input determines if the purchase order item detail is deleted or canceled. When the input value is ‘true’, the item detail is removed from the purchase order. When the input value is ‘false’, the item detail remains on the purchase order with a status of ‘Canceled’. The DeleteDetails input defaults to ‘false’ when not included in the request.

The KeepTranDetailTaggedForPO input determines if the item detail on the linked transaction remains tagged to fill from a purchase order. When the input value is ‘true’, the item detail on the linked transaction remains tagged to fill from a purchase order. When the input value is ‘false’, the item detail on the linked transaction is no longer tagged to fill from a purchase order.

The Sequence input value is associated with the sequence number in the ‘Tran seq #’ column on the purchase order.

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v613

**Request body:**
```json
{
    "request": {
        "PurchaseOrderID": 0,
        "PurchaseOrderDetailsDeleteJSON": {
            "dsDetailDeleteSettings": {
                "dtDetailDeleteSettings": [
                    {
                        "DeleteDetails": true,
                        "KeepTranDetailTaggedForPO": true
                    }
                ]
            },
            "dsPurchaseOrderItem": {
                "dtPurchaseOrderItem": [
                    {
                        "Sequence": 1
                    }
                ]
            }
        }
    }
}
```

## PurchaseOrderDetailsUpdate
`POST /Purchasing/PurchaseOrderDetailsUpdate`

Purpose
Updates purchase order detail expected receipt dates and expected ship dates
Required Inputs

PurchaseOrderID

PurchaseOrderDetailSequence

Optional Inputs

Remaining fields in the dtPurchaseOrderDetail and dtPurchaseOrderDetailDimension not already referenced

Notes

When a purchase order detail Expected Ship Date or an Expected Receipt Date is updated, the purchase order header Expected Ship Date or Expected Receipt Date is recalculated.

The item being updated must meet the following criteria in order to be successfully updated:

Item is allowed in the API

Item is not closed on the purchase order

Item is not canceled on the purchase order

If updating a dimension on an item, values for Thickness, Width and/or Length are required based on the item type. If the existing item has tallies specified, dimension information must be sent in through dtPurchaseOrderDetailDimension. In addition, the OrderQty and UOM must be specified at the dimension level. Use the PieceCount field when the OrderQty has a value of "UNIT". Sheet Good item types will require the Width and Length to match existing item.

The OrderQty input value updates the remaining on order quantity for an item.

To zero out an item's remaining quantity on order use the PurchaseOrderDetailsDelete method.

The AddPermanentDetailGroupID input determines if a permanent detail group record is created for the detail group received in the request.

The AllowQtyDecreaseBelowLinkedTran input value determines if the quantity for an item linked to a transaction can be reduced below the original quantity when the Purchasing Parameters field 'Decrease quantity change options'. When the parameter is set to auto update or not to update the system ignores the AllowQtyDecreaseBelowLinkedTran input value and follows the parameter's setting.

The AllowQtyIncreaseLinkedNonStock input value determines if the quantity for a non-stock item linked to a transaction can be increased above the original quantity when the Sales Order Parameters field 'Update linked SO with PO qty increase' and the Reman Parameters field 'Update linked RM with PO qty increase for non-stocks' are set to question the update. When the parameters are set to auto update or not to update the system ignores the AllowQtyIncreaseLinkedNonStock input value and follows the parameter's setting.

The AllowQtyDecreaseSOStagedInvoiced input value determines if an item's quantity on a requesting purchase order linked to a staged or invoiced shipping sales order can be decreased.

The AllowQtyDecreasePreReceipt input value determines if the quantity for an item can be reduced when a pre-receipt record exists.

The ApplyCostUpdatesToParentPO input value determines if updates to the quantity, UOM, cost, or cost UOM on a child or balance purchase order also affects the parent purchase order.

The ApplyCostUpdatesToChildPO input value determines if updates to the quantity, UOM, cost, or cost UOM on a parent purchase order also affects the child purchase order.

The ApplyDiscountsToOverriddenCost input value determines if the existing discounts applied to the item will be reduced to zero when the cost is overridden. This input is ignored when discounts are specified in the request.

The ClearLinkedSOCostOverride input value determines if the item's cost on a linked purchase order that does not affect inventory can be updated when the item on the sales order has an overridden cost.

The OverrideDimensionCosts input value determines if the detail cost is allowed to be overridden when there are different costs assigned by dimension.

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Valid values for a sequence's thickness, width and length come from ItemList or ItemsInChunksList

This method contains a parent/child relationship between dtPurchaseOrderDetail and dtPurchaseOrderDetailDimension. Please see Parent/Child relationship topic for more information

Version Deployed
v538

**Request body:**
```json
{
    "request": {
        "PurchaseOrderID": 0,
        "PurchaseOrderDetailsUpdateJSON": {
            "dsPurchaseOrderDetail": {
                "dtPurchaseOrderDetail": [
                    {
                        "PurchaseOrderDetailSequence": 1,
                        "OrderQty": 0,
                        "UOM": "",
                        "Cost": "0",
                        "CostUOM": "",
                        "Discount1": 0,
                        "Discount2": 0,
                        "Discount3": 0,
                        "ExpectedReceiptDate": "",
                        "ExpectedShipDate": "",
                        "ProposedSellPrice": 0,
                        "SellPriceUOM": "",
                        "SupplierQuotedCost": true,
                        "SupplierQuoteID": "",
                        "GroupID": "",
                        "AddPermanentDetailGroupID": true,
                        "CopyGroupIDToLinkedSO": true,
                        "AllowQtyDecreaseBelowLinkedTran": true,
                        "AllowQtyIncreaseLinkedNonStock": true,
                        "AllowQtyDecreaseSOStagedInvoiced": true,
                        "AllowQtyDecreasePreReceipt": true,
                        "ApplyCostUpdatesToParentPO": true,
                        "ApplyCostUpdatesToChildPO": true,
                        "ApplyDiscountsToOverriddenCost": true,
                        "ClearLinkedSOCostOverride": true,
                        "OverrideDimensionCosts": true
                    },
                    {
                        "PurchaseOrderDetailSequence": 2,
                        "OrderQty": 0,
                        "UOM": "",
                        "Cost": "0",
                        "CostUOM": "",
                        "Discount1": 0,
                        "Discount2": 0,
                        "Discount3": 0,
                        "ExpectedReceiptDate": "",
                        "ExpectedShipDate": "",
                        "ProposedSellPrice": 0,
                        "SellPriceUOM": "",
                        "SupplierQuotedCost": true,
                        "SupplierQuoteID": "",
                        "GroupID": "",
                        "AddPermanentDetailGroupID": true,
                        "CopyGroupIDToLinkedSO": true,
                        "AllowQtyDecreaseBelowLinkedTran": true,
                        "AllowQtyIncreaseLinkedNonStock": true,
                        "AllowQtyDecreaseSOStagedInvoiced": true,
                        "AllowQtyDecreasePreReceipt": true,
                        "ApplyCostUpdatesToParentPO": true,
                        "ApplyCostUpdatesToChildPO": true,
                        "ApplyDiscountsToOverriddenCost": true,
                        "ClearLinkedSOCostOverride": true,
                        "OverrideDimensionCosts": true
                    }
                ],
                "dtPurchaseOrderDetailDimension": [
                    {
                        "PurchaseOrderDetailSequence": 2,
                        "OrderQty": 0,
                        "UOM": "",
                        "Thickness": 0,
                        "Width": 0,
                        "Length": 0,
                        "PieceCount": 0,
                        "Cost": 0,
                        "CostUOM": ""
                    },
                    {
                        "PurchaseOrderDetailSequence": 2,
                        "OrderQty": 0,
                        "UOM": "",
                        "Thickness": 0,
                        "Width": 0,
                        "Length": 0,
                        "PieceCount": 0,
                        "Cost": 0,
                        "CostUOM": ""
                    }
                ]
            }
        }
    }
}
```

## PurchaseOrderGet
`POST /Purchasing/PurchaseOrderGet`

Purpose
Returns a specific purchase order, including header and detail information
Required Inputs

PurchaseOrderID

Optional Inputs

N/A

Notes
N/A
Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

A one-to-many Parent/Child relationship exists between dtPurchaseOrderHeader and dtPurchaseOrderHeaderNote through OrderID.

A one-to-many Parent/Child relationship exists between dtPurchaseOrderHeader and dtPurchaseOrderHeaderMessage through OrderID.

A one-to-many Parent/Child relationship exists between dtPurchaseOrderDetail and dtPurchaseOrderDetailMessage through Sequence.

Version Deployed
v539

**Request body:**
```json
{
    "request": {
        "PurchaseOrderID": ""
    }
}
```

## PurchaseOrderHeaderUpdate
`POST /Purchasing/PurchaseOrderHeaderUpdate`

Purpose
Updates purchase order header fields
Required Inputs

PurchaseOrderID

Optional Inputs

ExpectedShipDate

ExpectedReceiptDate

ExpectedReceiptTime

PODescription

Buyer1

Buyer2

Reference

VerbalPO

POLabel

PickUpID

ShipVia

FreightTerms

PaymentTermsCode

AllowChanges

AllowChangesUntilDate

AllowChangesUntilTime

TrackingDate

SendPOVia

UpdateLead

ConfirmedBy

All fields in dtPurchaseOrderHeaderNotes

Notes

The related fields on the child purchase order(s) are updated when the following fields on the parent purchase order are changed:

PODescription

VerbalPO

Reference

Buyer1

Buyer2

ShipVia

PaymentTermsCode

FreightTerms

TrackingDate

When the Expected Ship Date and Expected Receipt Dates are updated on the header, the purchase order detail sequences that do not have overridden Expected Ship Dates or Expected Receipt Dates are automatically updated.

ShipFromSequence valid values are read and updated if

PO is the Parent PO

Supplier Ship from is valid for the branch

PO is not partially received, completely received, or cancelled

PO is not in the process of being received

PO is not a transfer PO

Supplier Ship from is not a branch transfer supplier

User has necessary security

The following fields are only read when the ShipFromSequence field is populated with a valid value

OverriddenCostDiscShipFromUpdate

ApplyOrderMinShipFromUpdate

ApplyMinPackShipFromUpdate

UseInactiveShipFromUpdate

When creating a note, the OrderNote tag is required in dtPurchaseOrderHeaderNotes

The OrderNoteSequence tag must not be sent or have a value of 0 to create a new note

When updating a note, the OrderNoteSequence tag is required in dtPurchaseOrderHeaderNotes. The following additional rules apply:

If the OrderNote tag is blank or not sent, no update is made to the Order Note value.

If the HotNote tag is not sent, no update is made to the Hot Note setting.

If the ReminderDate tag is not sent, no update is made to the Remind Date.

If the ReminderDate tag is blank, the Remind Date is removed.

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v538

**Request body:**
```json
{
    "request": {
        "PurchaseOrderID": 0,
        "PurchaseOrderHeaderUpdateJSON": {
            "dsPurchaseOrderHeader": {
                "dtPurchaseOrderHeader": [
                    {
                        "ExpectedShipDate": "",
                        "ExpectedReceiptDate": "",
                        "ExpectedReceiptTime": "",
                        "PODescription": "",
                        "Buyer1": "",
                        "Buyer2": "",
                        "Reference": "",
                        "VerbalPO": "",
                        "POLabel": "",
                        "PickUpID": "",
                        "ShipVia": "",
                        "FreightTerms": "",
                        "PaymentTermsCode": "",
                        "AllowChanges": "",
                        "AllowChangesUntilDate": "",
                        "AllowChangesUntilTime": "",
                        "TrackingDate": "",
                        "SendPOVia": "",
                        "UpdateLead": "",
                        "ConfirmedBy": "",
                        "ShipFromSequence": 1,
                        "OverriddenCostDiscShipFromUpdate": "",
                        "ApplyOrderMinShipFromUpdate ": "",
                        "ApplyMinPackShipFromUpdate": "",
                        "UseInactiveShipFromUpdate": ""
                    }
                ],
                "dtPurchaseOrderHeaderNotes": [
                    {
                        "OrderNoteSequence": 0,
                        "OrderNote": "0",
                        "ReminderDate": "0",
                        "HotNote": false
                    }
                ]
            }
        }
    }
}
```

## PurchaseOrderMessageCreate
`POST /Purchasing/PurchaseOrderMessageCreate`

Purpose
Creates a purchase order transaction message in the branch the user is logged into
Required Inputs

TranID

MessageText

MessageType

TranSeq (for detail transaction messages)

Optional Inputs

PrintOnForms

SendToWMS

Notes

MessageText can send a maximum of 1000 characters

Valid values for MessageType are H, Header, D, Detail, F, and Footer

When PrintOnForms is set to true, all eligible forms are set to print the new message

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v554

**Request body:**
```json
{
    "request": {
        "MessageCreateJSON": {
            "dsMessageCreate": {
                "dtMessageCreate": [
                    {
                        "TranID": 0,
                        "TranSeq": 1,
                        "MessageText": "",
                        "MessageType": "",
                        "PrintOnForms": false,
                        "SendToWMS": true
                    }
                ]
            }
        }
    }
}
```

## PurchaseOrderMessageDelete
`POST /Purchasing/PurchaseOrderMessageDelete`

Purpose
Deletes existing purchase order transaction messages
Required Inputs

TranID

MessageType

TranSeq (for detail transaction messages)

MessageID

Optional Inputs

N/A

Notes

Valid values for MessageType are H, Header, D, Detail, F and Footer

You must specify the TranSeq value when MessageType is "D" or "Detail"

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Valid purchase order message values come from PurchaseOrderGet

Version Deployed
v619

**Request body:**
```json
{
    "request": {
        "TranID": 0,
        "MessageDeleteJSON": {
            "dsMessageDelete": {
                "dtMessageDelete": [
                    {
                        "MessageType": "",
                        "TranSeq": 0,
                        "MessageID": 0
                    }
                ]
            }
        }
    }
}
```

## PurchaseOrderMessageUpdate
`POST /Purchasing/PurchaseOrderMessageUpdate`

Purpose
Updates existing purchase order transaction messages
Required Inputs

TranID

MessageType

TranSeq (for detail transaction messages)

MessageID

Optional Inputs

MessageText

PrintOnForms

SendToWMS

Notes

Valid values for MessageType are H, Header, D, Detail, F and Footer

You must specify the TranSeq value when MessageType is D or Detail

The following rules apply when you send a MessageText value

If the existing MessageID is a reusable message in the system (indicated by positive MessageID value), the system replaces the existing MessageID value with a custom message ID (indicated by a negative MessageID value)

If the existing MessageID is a custom message, the system replaces the existing MessageText and retains the existing MessageID

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Valid purchase order message values come from PurchaseOrderGet

Version Deployed
v619

**Request body:**
```json
{
    "request": {
        "TranID": 0,
        "MessageUpdateJSON": {
            "dsMessageUpdate": {
                "dtMessageUpdate": [
                    {
                        "MessageType": "",
                        "TranSeq": 0,
                        "MessageID": 0,
                        "MessageText": "",
                        "PrintOnForms": true,
                        "SendToWMS": true
                    }
                ]
            }
        }
    }
}
```

## PurchaseOrderNotesDelete
`POST /Purchasing/PurchaseOrderNotesDelete`

Purpose
Deletes existing purchase order notes records
Required Inputs

PurchaseOrderID

OrderNoteSequence

Optional Inputs

N/A

Notes

The OrderNoteSequence input value is associated with the note sequence for the purchase order.

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

OrderNoteSequence comes from PurchaseOrderGet

Version Deployed
v619

**Request body:**
```json
{
    "request": {
        "PurchaseOrderID": 0,
        "PurchaseOrderNotesDeleteJSON": {
            "dsPurchaseOrderNotesDelete": {
                "dtPurchaseOrderNotesDelete": [
                    {
                        "OrderNoteSequence": 0
                    },
                    {
                        "OrderNoteSequence": 0
                    }
                ]
            }
        }
    }
}
```

## ShippingTrackingUpdateBySupplierReturn
`POST /Purchasing/ShippingTrackingUpdateBySupplierReturn`

Purpose
Stores tracking information for the supplier return on an existing or auto-created dispatch transaction
Required Inputs

SupplierReturnID

Optional Inputs

Remaining fields in the dtShipmentUpdateBySRSettings, dtTrackingDetailBySRRequest, and dtTrackingDetailBySRItemRequest

Notes

This method contains a parent/child relationship between the dsShipmentUpdateBySRSettings and the SupplierReturnID. Please see the Parent/Child relationship topic for more information.

There is a many to one relationship between the dsTrackingDetailBySRRequest and SupplierReturnID as the method allows the input of multiple tracking numbers.

Valid values for ContainerWeightUOM: LB, KG. If this field is not sent, the system defaults to a UOM of LB.

The following rules apply to the ShipVia tag:

If a valid ship via is sent in the request, the supplier return header ship via is updated with this value. If an invalid ship via is sent in the request, a failure occurs.

If a blank value is sent for the ship via, no change occurs to the supplier return header ship via.

If the ShipVia tag is not sent in the request, no change occurs to the supplier return header ship via.

A dispatch transaction, is created for the supplier return if one does not already exist.

When a TrackingNumber is sent in with items specified in the dtTrackingDetailBySRRequest, dispatch details are created only for the supplier return items and quantities received.

When a TrackingNumber is sent without items specified, dispatch details are created for all supplier return items and quantities, with no containers assigned at the item level.

When tracking information is received for a supplier return that has already been dispatched, the existing dispatch transaction is updated.

If a supplier return is assigned to more than one dispatch, the method fails

If the TrackingNumber sent is already assigned to the dispatch, the method fails.

If container information is assigned by detail on the existing dispatch, the request must be sent in with the dtTrackingDetailBySRItemRequest fields.

When a TrackingNumber is sent in with dtTrackingDetailBySRItemRequest fields, the quantity received for an item cannot be more than the accumulated total of what remains to be dispatched plus any dispatched quantities not previously assigned to a container for that supplier return.

This method contains a parent/child relationship between the dtTrackingDetailBySRRequest and the TrackingNumber. Please see the Parent/Child relationship topic for more information.

There is a many to one relationship between the dtTrackingDetailBySRItemRequest and the TrackingNumber as the method allows you the option to specify item(s) for each tracking number.

When multiple TrackingNumbers are sent in without the dtTrackingDetailBySRItemRequest, the tracking information is stored at the supplier return transaction level on the dispatch transaction.

When a single TrackingNumber is sent in without the dtTrackingDetailBySRItemRequest, the tracking information is stored at the item level for all items on the supplier return.

When a TrackingNumber is sent in with dtTrackingDetailBySRItemRequest fields, the tracking information is stored at the supplier return/item level on the dispatch.

When multiple TrackingNumbers are sent in the dtTrackingDetailBySRItemRequest, only items on the supplier return that are specified in the dtTrackingDetailBySRItemRequest are saved with tracking information at the item level.

The following rules apply when sending multiple tracking numbers in a single request

The dtTrackingDetailBySRItemRequest must be excluded from the request to save all tracking numbers at the supplier return level.

The dtTrackingDetailBySRItemRequest must be included for each tracking number to save all tracking numbers at the supplier return/item level.

The system does not allow some tracking numbers to include dtTrackingDetailBySRItemRequest and others to exclude dtTrackingDetailBySRItemRequest tags in a single request.

Relationships

ContextId and Branch come from Login

Version Deployed
v601

**Request body:**
```json
{
    "request": {
        "SupplierReturnID": 0,
        "ShippingTrackingUpdateBySRJSON": {
            "dsShipmentUpdateBySRSettings": {
                "dtShipmentUpdateBySRSettings": [
                    {
                        "ShipVia": "",
                        "ExpectedShipDate": "2022-10-02"
                    }
                ]
            },
            "dsTrackingDetailBySRRequest": {
                "dtTrackingDetailBySRRequest": [
                    {
                        "TrackingNumber": "",
                        "ContainerWeight": 0,
                        "ContainerWeightUOM": "",
                        "ContainerLength": 0,
                        "ContainerWidth": 0,
                        "ContainerHeight": 0,
                        "dtTrackingDetailBySRItemRequest": [
                            {
                                "ItemCode": "",
                                "DetailSequence": 1,
                                "Quantity": 0,
                                "QtyUOM": ""
                            }
                        ]
                    }
                ]
            }
        }
    }
}
```

## SupplierReturnGet
`POST /Purchasing/SupplierReturnGet`

Purpose
Retrieve Supplier Return header and detail information
Required Inputs

SupplierReturnID

Optional Inputs

N/A

Notes

The initial branch returned with the Login method indicates which branch that context is originally positioned in

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

A one-to-many Parent/Child relationship exists between dtSupplierReturnHeader and dtSupplierReturnHeaderNote through OrderID.

A one-to-many Parent/Child relationship exists between dtSupplierReturnHeader and dtSupplierReturnHeaderMessage through OrderID.

A one-to-many Parent/Child relationship exists between dtSupplierReturnDetail and dtSupplierReturnDetailMessage through Sequence.

Version Deployed
v601

**Request body:**
```json
{
    "request": {
        "SupplierReturnID": 0
    }
}
```

## SupplierReturnMessageCreate
`POST /Purchasing/SupplierReturnMessageCreate`

Purpose
Creates a supplier return transaction message in the branch the user is logged into
Required Inputs

TranID

MessageText

MessageType

TranSeq (for detail transaction messages)

Optional Inputs

PrintOnForms

SendToWMS

Notes

MessageText can send a maximum of 1000 characters

Valid values for MessageType are H, Header, D, Detail, F, and Footer

When PrintOnForms is set to true, all eligible forms are set to print the new message

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v554

**Request body:**
```json
{
    "request": {
        "MessageCreateJSON": {
            "dsMessageCreate": {
                "dtMessageCreate": [
                    {
                        "TranID": 0,
                        "TranSeq": 1,
                        "MessageText": "",
                        "MessageType": "",
                        "PrintOnForms": true,
                        "SendToWMS": false
                    }
                ]
            }
        }
    }
}
```

---

# Reman Service  (11 methods)

## RemanHeaderCreate
`POST /Reman/RemanHeaderCreate`

Purpose
Creates a new reman order
Required Inputs

N/A

Optional Inputs

All fields in dtInputRemanHeaderRequest

Notes

This method creates only the Reman Order header record. Other methods in this service allow the creation or maintenance of the related inputs, operations and outputs

If defined, an API Reman Created notification is generated

Relationships

ContextId and Branch come from Login

The NewOrderID returned from this method is used as the OrderID input in all other Reman methods available in this service

Version Deployed
v546

**Request body:**
```json
{
    "request": {
        "dsInputRemanHeaderRequest": {
            "dtInputRemanHeaderRequest": [
                {
                    "BalancingUOM": "",
                    "TransactionDescription": "",
                    "ExpectedDate": "2020-04-15",
                    "TransactionJob": "",
                    "TransactionReference": "",
                    "RemanType": "",
                    "StartDate": "2020-03-25",
                    "SupplierID": 0,
                    "SupplierShipFromSequence": 0
                }
            ]
        }
    }
}
```

## RemanInputsCreate
`POST /Reman/RemanInputsCreate`

Purpose
Creates one or more reman inputs on an existing, open reman order
Required Inputs

OrderID; following fields in dsInputRemanInputRequest: Key, ItemCode, AffectUsage for each record in dtInputRemanInputRequest

Optional Inputs

Remaining fields in dtInputRemanInput

Notes

Non-dimensional inputs can be created with 0 OrderQty

If the input is a dimension, Thickness, Width, Length, OrderQty, and OrderQtyUOM are required inputs

To specify the locations to pull inventory from for the inputs, the dtInputRemanInputComReq requires the Location/Lot/Tag/Content fields depending on how the inventory is carried. Additionally, the OrderQty and OrderQtyUOM are required

The system does not auto tag input items created per settings on the associated item record.

Regardless of the reman type assigned to a reman work order, pass-thru items are not created when adding input items

Auto messages are added to the reman input item based on existing rules for adding them in Agility.

You can specify tally quantities for input items by assigning values to the dtInputRemanInputDimReq or dtInputRemanInputComReq fields. You must provide the Sequence for the associated reman input item as well as the Thickness, Width and Length for dimension items.

When commit records are specified for reman input items, dimension records are not processed with the exception of those created for tally calculator items.

All dimension and commit records for a single reman input item must have the same OrderQtyUOM.

Relationships

ContextId and Branch come from Login

When the input is a dimension, the main item must be represented in dtInputRemanInputRequest. The Sequence used in dtInputRemanInputRequest must also be used as the Sequence in dtInputRemanInputDimReq to tie the item and its dimensions together

When the location for the inventory to be pulled from is supplied, the main item must be represented in dtInputRemanInputRequest. The Sequence used in dtInputRemanInputRequest must also be used as the Sequence in dtInputRemanInputComReq to tie the item and its locations together. Additionally, if the input is a dimensions, the Thickness, Width, Length must be provided in the dtInputRemanInputComReq to tie the dimensions to the inventory locations

There can be a one to many relationship between dtInputRemanInputRequest and dtInputRemanInputDimReq

There can be a one to many relationship between dtInputRemanInputRequest and dtInputRemanInputComReq

There can be a one to many relationship between dtInputRemanInputDimReq and dtInputRemanInputComReq

RemanOrderGet can be run to find the correct Key values to use when the new inputs need to be linked to existing operations or outputs

RemanOrderGet can be run with the OrderID used in this method to verify the inputs were added as expected

Version Deployed
v546

**Request body:**
```json
{
    "request": {
        "OrderID": 0,
        "dsInputRemanInputRequest": {
            "dtInputRemanInputRequest": [
                {
                    "Sequence": 1,
                    "Key": "",
                    "LinkID": "",
                    "ItemCode": "",
                    "ItemSize": "",
                    "ItemDescription": "",
                    "OrderQty": 0,
                    "OrderQtyUOM": "",
                    "AffectUsage": false
                }
            ],
            "dtInputRemanInputDimReq": [
                {
                    "Sequence": 0,
                    "Thickness": 0,
                    "Width": 0,
                    "Length": 0,
                    "PieceCount": 0,
                    "OrderQty": 0,
                    "OrderQtyUOM": ""
                }
            ],
            "dtInputRemanInputComReq": [
                {
                    "Sequence": 1,
                    "Location": "",
                    "Lot": "",
                    "Tag": "",
                    "Content": "",
                    "Thickness": 0,
                    "Width": 0,
                    "Length": 0,
                    "PieceCount": 0,
                    "OrderQty": 0,
                    "OrderQtyUOM": ""
                }
            ]
        }
    }
}
```

## RemanInputDelete
`POST /Reman/RemanInputDelete`

Purpose
Deletes one or more inputs from an existing, open reman order
Required Inputs

OrderID; following fields in dsInputRemanInputRequest: Sequence for each input to be deleted, AffectUsage

Optional Inputs

Remaining fields in dsInputRemanInputRequest

Notes

Method deletes inputs for the Sequences specified including any related dimension or inventory locations associated. For this reason, values are not needed in dtInputRemanInputDimReq or dtInputRemanInputComReq when deleting

Relationships

ContextId and Branch come from Login

RemanOrderGet can be run to find the correct Sequence values to use when deleting inputs

RemanOrderGet can be run with the OrderID used in this method to verify the inputs were deleted as expected

Version Deployed
v546

**Request body:**
```json
{
    "request": {
        "OrderID": 0,
        "dsInputRemanInputRequest": {
            "dtInputRemanInputRequest": [
                {
                    "Sequence": 1,
                    "Key": "",
                    "LinkID": "",
                    "ItemCode": "",
                    "ItemSize": "",
                    "ItemDescription": "",
                    "OrderQty": 0,
                    "OrderQtyUOM": "",
                    "AffectUsage": false
                }
            ],
            "dtInputRemanInputDimReq": [
                {
                    "Sequence": 0,
                    "Thickness": 0,
                    "Width": 0,
                    "Length": 0,
                    "PieceCount": 0,
                    "OrderQty": 0,
                    "OrderQtyUOM": ""
                }
            ],
            "dtInputRemanInputComReq": [
                {
                    "Sequence": 1,
                    "Location": "",
                    "Lot": "",
                    "Tag": "",
                    "Content": "",
                    "Thickness": 0,
                    "Width": 0,
                    "Length": 0,
                    "PieceCount": 0,
                    "OrderQty": 0,
                    "OrderQtyUOM": ""
                }
            ]
        }
    }
}
```

## RemanMessageCreate
`POST /Reman/RemanMessageCreate`

Purpose
Creates a reman transaction message in the branch the user is logged into
Required Inputs

TranID

TranType

MessageText

MessageType

TranSeq (for detail transaction messages)

Optional Inputs

PrintOnForms

Notes

Valid values for TranType are RM, Reman header, RM-input, Reman input, RM-output, Reman output, RM-operation, and Reman operation

MessageText can send a maximum of 1000 characters

Valid values for MessageType are H, Header, D, Detail, F, and Footer

When PrintOnForms is set to true, all eligible forms are set to print the new message

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v554

**Request body:**
```json
{
    "request": {
        "MessageCreateJSON": {
            "dsMessageCreate": {
                "dtMessageCreate": [
                    {
                        "TranID": 0,
                        "TranType": "",
                        "TranSeq": 0,
                        "MessageText": "",
                        "MessageType": "",
                        "PrintOnForms": true
                    }
                ]
            }
        }
    }
}
```

## RemanOperationsCreate
`POST /Reman/RemanOperationsCreate`

Purpose
Creates one or more operations on an existing, open reman order
Required Inputs

OrderID; following fields in dsInputRemanOperationRequest: CostType, OrderQty, SupplierID, SupplierShipFromSequence for each input, PrintOnWO

Optional Inputs

Remaining fields in dtInputRemanOperationRequest

Notes

Key, while not required, is used to tie the operations to a specific input and/or output

CostType is the operation to be added

CostType can be added with 0 OrderQty

Relationships

ContextId comes from Login

RemanOrderGet can be run to find the correct Key values to use when the operations need to be linked to existing inputs or outputs

RemanOrderGet can be run with the OrderID used in this method to verify the operations were added as expected

Version Deployed
v546

**Request body:**
```json
{
    "request": {
        "OrderID": 0,
        "dsInputRemanOperationRequest": {
            "dtInputRemanOperationRequest": [
                {
                    "Sequence": 0,
                    "Key": "",
                    "CostType": "",
                    "OperationDescription": "",
                    "OrderQty": 0,
                    "Cost": 0,
                    "PrintOnWO": false,
                    "SupplierID": 0,
                    "SupplierShipFromSequence": 0,
                    "ExpectedStartDate": "2020-04-03",
                    "ExpectedCompletionDate": "2020-04-04"
                }
            ]
        }
    }
}
```

## RemanOperationDelete
`POST /Reman/RemanOperationDelete`

Purpose
Deletes one or more operations from an existing, open reman order
Required Inputs

OrderID; following fields in dsInputRemanOperationRequest: Sequence for each operation to be deleted, PrintOnWO

Optional Inputs

Remaining fields in dsInputRemanOperationRequest

Notes

N/A

Relationships

ContextId and Branch come from Login

RemanOrderGet can be run to find the correct Sequence values to use when deleting operations

RemanOrderGet can be run with the OrderID used in this method to verify the operations were deleted as expected

Version Deployed
v546

**Request body:**
```json
{
    "request": {
        "OrderID": 0,
        "dsInputRemanOperationRequest": {
            "dtInputRemanOperationRequest": [
                {
                    "Sequence": 0,
                    "Key": "",
                    "CostType": "",
                    "OperationDescription": "",
                    "OrderQty": 0,
                    "Cost": 0,
                    "PrintOnWO": false,
                    "SupplierID": 0,
                    "SupplierShipFromSequence": 0,
                    "ExpectedStartDate": "2020-04-03",
                    "ExpectedCompletionDate": "2020-04-04"
                }
            ]
        }
    }
}
```

## RemanOrderGet
`POST /Reman/RemanOrderGet`

Purpose
Returns a specific reman order, including its inputs, operations and outputs
Required Inputs

OrderID

Optional Inputs

N/A

Notes

This method does not return specified commit locations for inputs or specified storage locations for outputs

Relationships

ContextId and Branch come from Login

While this method can be called for any known, valid reman order id, often it is used in conjunction with the other Reman methods found in this service. For example, the response from a valid RemanHeaderCreate request is OrderID. The OrderID can be used as input to this method to fetch the reman order for review. Additionally, after using a method such as RemanInputsCreate to add inputs to the reman, the RemanOrderGet method can be used to verify the inputs added to an existing reman

Version Deployed
v546

**Request body:**
```json
{
    "request": {
        "OrderID": 0
    }
}
```

## RemanOutputsCreate
`POST /Reman/RemanOutputsCreate`

Purpose
Creates one or more reman outputs on an existing, open reman order
Required Inputs

OrderID; following fields in dsInputRemanOutputRequest: Key, ApplyNegativeUsage, ItemCode, OrderQtyUOM ; following fields in dtInputRemanOutputStorageReq: OrderQty, OrderQtyUOM, Location/Lot/Tag/Content depending on how the inventory is carried

Optional Inputs

Remaining fields in dsInputRemanOutputRequest

Notes

Non-dimensional outputs can be created with 0 OrderQty

If the output is a dimension, Thickness, Width, Length, OrderQty and OrderQtyUOM are required inputs in dtInputRemanOutputDimReq

Method requires the storage locations specified for each output. To specify, dtInputRemanOutputStorageReq requires the Location, Lot, Tag, Content fields depending on how the inventory is carried as well as OrderQty and OrderQtyUOM are required

Auto messages are added to the reman output item based on existing rules for adding them in Agility

All dimenstion and storage records for a single reman output item must have the same OrderQtyUOM

Relationships

ContextId and Branch come from Login

When the output is a dimension, the main item must be represented in dtInputRemanOutputRequest. The Sequence used in dtInputRemanOutputRequest must also be used as the Sequence in dtInputRemanOutputDimReq to tie the item and its dimensions together

When specifying the storage locations for the inventory, the main item must be represented in dtInputRemanOutputRequest. The Sequence used in dtInputRemanOutputRequest must also be used as the Sequence in dtInputRemanOutputStorageReq to tie the item and its locations together. Additionally, if the input is a dimensions the Sequence, Thickness, Width, Length must be provided in the dtInputRemanOutputStorageReq to tie the dimensions to the storage locations

There can be a one to many relationship between dtInputRemanOutputRequest and dtInputRemanOutputDimReq

There can be a one to many relationship between dtInputRemanOutputRequest and dtInputRemanOutputStorageReq

There can be a one to many relationship between dtInputRemanOutputDimReq and dtInputRemanOutputStorageReq

RemanOrderGet can be run to find the correct Key values to use when the outputs need to be linked to existing operations or inputs

RemanOrderGet can be run with the OrderID used in this method to verify the outputs were added as expected

Version Deployed
v546

**Request body:**
```json
{
    "request": {
        "OrderID": 0,
        "dsInputRemanOutputRequest": {
            "dtInputRemanOutputRequest": [
                {
                    "Sequence": 0,
                    "Key": "",
                    "LinkID": "",
                    "Cull": "",
                    "ItemCode": "",
                    "ItemSize": "",
                    "ItemDescription": "",
                    "OrderQty": 0,
                    "OrderQtyUOM": "",
                    "ApplyNegativeUsage": true
                }
            ],
            "dtInputRemanOutputDimReq": [
                {
                    "Sequence": 0,
                    "Thickness": 0,
                    "Width": 0,
                    "Length": 0,
                    "PieceCount": 0,
                    "OrderQty": 0,
                    "OrderQtyUOM": ""
                }
            ],
            "dtInputRemanOutputStorageReq": [
                {
                    "Sequence": 0,
                    "Location": "",
                    "Lot": "",
                    "Tag": "",
                    "Content": "",
                    "Thickness": 0,
                    "Width": 0,
                    "Length": 0,
                    "PieceCount": 0,
                    "OrderQty": 0,
                    "OrderQtyUOM": ""
                }
            ]
        }
    }
}
```

## RemanOutputDelete
`POST /Reman/RemanOutputDelete`

Purpose
Deletes one or more outputs from an existing, open reman order
Required Inputs

OrderID; following fields in dsInputRemanOutputRequest: ApplyNegativeUsage, Sequence for each output to be deleted

Optional Inputs

Remaining fields in dsInputRemanOutputRequest

Notes

dtInputRemanOutputDimReq and dtInputRemanOutputStorageReq are restricted for future use

Method deletes outputs for the Sequences specified including any related dimension or storage locations associated. For this reason, values are not needed in dtInputRemanOutputDimReq or dtInputRemanOutputStorageReq when deleting

Relationships

ContextId and Branch come from Login

RemanOrderGet can be run used to find the correct Sequence values to use when deleting outputs

RemanOrderGet can be run with the OrderID used in this method to verify the outputs were deleted as expected

Version Deployed
v546

**Request body:**
```json
{
    "request": {
        "OrderID": 0,
        "dsInputRemanOutputRequest": {
            "dtInputRemanOutputRequest": [
                {
                    "Sequence": 0,
                    "Key": "",
                    "LinkID": "",
                    "Cull": "",
                    "ItemCode": "",
                    "ItemSize": "",
                    "ItemDescription": "",
                    "OrderQty": 0,
                    "OrderQtyUOM": "",
                    "ApplyNegativeUsage": true
                }
            ],
            "dtInputRemanOutputDimReq": [
                {
                    "Sequence": 0,
                    "Thickness": 0,
                    "Width": 0,
                    "Length": 0,
                    "PieceCount": 0,
                    "OrderQty": 0,
                    "OrderQtyUOM": ""
                }
            ],
            "dtInputRemanOutputStorageReq": [
                {
                    "Sequence": 0,
                    "Location": "",
                    "Lot": "",
                    "Tag": "",
                    "Content": "",
                    "Thickness": 0,
                    "Width": 0,
                    "Length": 0,
                    "PieceCount": 0,
                    "OrderQty": 0,
                    "OrderQtyUOM": ""
                }
            ]
        }
    }
}
```

## RemanSpecifyTagsToCommit
`POST /Reman/RemanSpecifyTagsToCommit`

Purpose
Commits inventory tags to input items on reman work orders in the branch the user is logged into
Required Inputs

OrderID; following fields in dsInputRemanTagsToCommitRequest: Tag

Optional Inputs

N/A

Notes

When the specified tag is not for an existing input item, the item is added to the reman work order and the tag is committed

When an item is added to a reman work order, any associated operations assigned to the item are also added

When the specified tag is for an existing input item, the item quantity and tally is updated to reflect the additional inventory commit being made

Relationships

ContextId and Branch come from Login

Version Deployed
v546

**Request body:**
```json
{
    "request": {
        "OrderID": 0,
        "dsInputRemanTagsToCommitRequest": {
            "dtInputRemanTagsToCommitRequest": [
                {
                    "Tag": ""
                }
            ]
        }
    }
}
```

## RemanStorageReplace
`POST /Reman/RemanStorageReplace`

Purpose
Deletes one or more outputs from an existing, open reman order
Required Inputs

OrderID; following fields in dsInputRemanOutputRequest: Sequence, Location/Lot/Tag/Content, OrderQty, OrderQtyUOM and ApplyNegativeUsage for each storage record needing to be updated

Optional Inputs

Remaining fields in dsInputRemanOutputRequest

Notes

dtInputRemanOutputDimensionReq is restricted for future use

Method deletes all existing storage records associated with the Sequences entered and creates new storage records based on the incoming values

Values are not needed in dtInputRemanOutputRequest or dtInputRemanOutputDimensionReq when deleting storage records

If the storage is for a dimension, Thickness, Width, Length, as needed by item type, are required inputs in dtInputRemanOutputStorageRequest

Method requires the storage locations specified for each output to have the Location, Lot, Tag, Content fields depending on how the inventory is carried

All replacement storage records for a single reman output item must have the same OrderQtyUOM

Relationships

ContextId and Branch come from Login

RemanOrderGet can be run to find the correct output Sequence values to use when replacing storage locations

Version Deployed
v546

**Request body:**
```json
{
    "request": {
        "OrderID": 0,
        "dsInputRemanOutputRequest": {
            "dtInputRemanOutputRequest": [
                {
                    "Sequence": 0,
                    "Key": "",
                    "LinkID": "",
                    "Cull": "",
                    "ItemCode": "",
                    "ItemSize": "",
                    "ItemDescription": "",
                    "OrderQty": 0,
                    "OrderQtyUOM": "",
                    "ApplyNegativeUsage": true
                }
            ],
            "dtInputRemanOutputDimensionReq": [
                {
                    "Sequence": 0,
                    "Thickness": 0,
                    "Width": 0,
                    "Length": 0,
                    "PieceCount": 0,
                    "OrderQty": 0,
                    "OrderQtyUOM": ""
                }
            ],
            "dtInputRemanOutputStorageRequest": [
                {
                    "Sequence": 0,
                    "Location": "",
                    "Lot": "",
                    "Tag": "",
                    "Content": "",
                    "Thickness": 0,
                    "Width": 0,
                    "Length": 0,
                    "PieceCount": 0,
                    "OrderQty": 0,
                    "OrderQtyUOM": ""
                }
            ]
        }
    }
}
```

---

# Session Service  (4 methods)

## AgilityVersion
`POST /Session/AgilityVersion`

Purpose
Returns the customer’s Agility version the web service is accessing
Required Inputs

N/A

Optional Inputs

N/A

Notes

This method can be used to ensure the Agility version the customer’s environment is running against is compatible with the methods being used

Relationships

N/A

Version Deployed
v534

## BranchList
`POST /Session/BranchList`

Purpose
Returns a list of branches the user has access to
Required Inputs

N/A

Optional Inputs

N/A

Notes
N/A
Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v534

## Login
`POST /Session/Login`

Purpose
Logs the user into Agility and returns a context id
Required Inputs

LoginID

Password

Optional Inputs

N/A

Notes

N/A

Relationships

ContextId returned is used as an input and sent in the header in most of the other methods

InitialBranch is the branch within which the context id is initially positioned and can be used as the Branch input in the header in most of the other methods

Version Deployed
v534

**Request body:**
```json
{
    "request": {
        "LoginID": "",
        "Password": ""
    }
}
```

## Logout
`POST /Session/Logout`

Purpose
Logs a user out of Agility and removes the context id
Required Inputs

N/A

Optional Inputs

N/A

Notes
N/A
Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v534

---

# Shipments Service  (13 methods)

## PickFileCreate
`POST /Shipments/PickFileCreate`

Purpose
Creates a new pick file based on a saved picking viewer
Required Inputs

ViewerName

AccessType

AccessedBy

Optional Inputs

SaleType

Route

CustomerID

OrderID

Dispatched

Location

HandlingCode

ShipVia

CutOffDate

Notes

Values provided as inputs override values saved in the viewer criteria and are used as the criteria.

{none} is a valid value for HandlingCode and < all > is a valid value for SaleType, Route, Customer, TransactionID, Dispatched, Location, HandlingCodeandShipVia. Please see the Entering special character values such as < or > topic for more information

If a value is not sent for CutOffDate, the current date is used

The following can contain a single value or a string separated by commas: SaleType, Route, Dispatched, Location, HandlingCode, ShipVia

The Action Allocation ‘Create Picks – 2 step’ is not applied and Data Allocations do not apply.

Pick Ticket and Pick Report Forms Assignments to print other forms, such as Reman Work Orders, are ignored.

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Valid values for SaleType come from GetSaleTypes

Valid values for CustomerID come from CustomersList or CustomerShiptoList

Valid values for TransactionID come from SalesOrderList

Version Deployed
v540

**Request body:**
```json
{
    "request": {
        "ViewerName": "",
        "AccessType": "",
        "AccessedBy": "",
        "SaleType": "",
        "Route": "",
        "CustomerID": "",
        "OrderID": "",
        "Dispatched": "",
        "Location": "",
        "HandlingCode": "",
        "ShipVia": "",
        "CutOffDate": ""
    }
}
```

## PickFileList
`POST /Shipments/PickFileList`

Purpose
Returns header and detail information for sales order pick files, associated with a customer, specific sales order, specific pick file id, route id or date range
Required Inputs

Must also include one of the following:

OrderID

PickID

CustomerID

RouteID

ExpectDateRangeStart

ExpectDateRangeEnd

OrderID

ShipmentNumber

PickID

ShipToSequence

ChunkStartPointer

RecordFetchLimit

Optional Inputs

RouteID

Notes

Method can be requested for a specific customer, specific customer and ship-to, a specific sales order, a specific shipment for a specific sales order, a specific route or a specific date range.

This method allows a user to request a specific number of records. Please see the Data-Chunking topic for more information

ContainerLength, ContainerWidth and ContainerHeight are retrieved from the primary item supplier record

HazMatFlag is based on the BOL code assigned to the item in Item Maintenance

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Valid values for CustomerID come from CustomersList or CustomerShiptoList.

Valid values for ShipToSequence come from CustomerShiptoList.

Valid values for OrderID come from SalesOrderList

Valid values for OrderID and related ShipmentNum come from ShipmentsList.

Valid values for PickID come from this method used in a circular way.

There is a Parent/Child relationship between dtPickResponse and dtPickDetailResponse through OrderID, PickID and ShipmentNum

Version Deployed
v614

**Request body:**
```json
{
    "request": {
        "OrderID": 0,
        "ShipmentNumber": 0,
        "PickID": 0,
        "CustomerID": "",
        "ShipToSequence": 0,
        "ExpectDateRangeStart": "",
        "ExpectDateRangeEnd": "",
        "RouteID": "",
        "ChunkStartPointer": 0,
        "RecordFetchLimit": 0
    }
}
```

## PODSignatureCreate
`POST /Shipments/PODSignatureCreate`

Purpose
Creates signatures for sales order shipments and credit memo transactions in the branch the user is logged into from a Proof of Delivery (POD) app
Required Inputs

Following fields in SignatureCreateJSON: TranID, TranType, ImageData signature image converted to Base64), PODSignature, ShipmentNum (for sales orders)

Optional Inputs

ImageInfo (typically, text representation of signature)

Notes

Valid values for TranType are CM, Credit Memo, SO, and Sales Order

ImageData is the image of the signature converted to Base64

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v554

**Request body:**
```json
{
    "request": {
        "PODSignatureCreateJSON": {
            "dsPODSignatureCreate": {
                "dtPODSignatureCreate": [
                    {
                        "TranType": "",
                        "TranID": 0,
                        "ShipmentNum": "",
                        "ImageData": "",
                        "ImageInfo": ""
                    }
                ]
            }
        }
    }
}
```

## ShipmentInfoUpdate
`POST /Shipments/ShipmentInfoUpdate`

Purpose
Updates specific fields related to shipment information
Required Inputs

OrderID

ShipmentNumber

UpdateAllPickFiles

Optional Inputs

UpdateSalesOrder

RouteID

StopNumber

ShipDate

RequestedDeliveryDate

ShipmentStatusFlag

Notes

The options of UpdateAllPickFiles and UpdateSalesOrder are used when the information being updated should apply to these records as well

ShipmentNumber can be specified as 0 to indicate the sales order header instead of a specific shipment

With Agility v553, to update sales order header fields instead of a specific shipment, ShipmentNumber must be set to 0 and the sales order cannot have a staged status

ShipmentStatusFlag can be entered in either of the following formats:

Loaded or L

Staged or S

En Route or E

Delivered or D

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Valid values for OrderID and/or ShipmentNumber come from ShipmentsList

Version Deployed
v534

**Request body:**
```json
{
    "request": {
        "OrderID": 0,
        "ShipmentInfoRequestJSON": {
            "dsShipInfoRequest": {
                "dtShipInfoRequest": [
                    {
                        "ShipmentNumber": 0,
                        "UpdateAllPickFiles": true,
                        "UpdateSalesOrder": true,
                        "RouteID": "",
                        "StopNumber": 0,
                        "ShipDate": "2019-05-08",
                        "RequestedDeliveryDate": "2019-04-12",
                        "ShipmentStatusFlag": ""
                    }
                ]
            }
        }
    }
}
```

## ShipmentsList
`POST /Shipments/ShipmentsList`

Purpose
Returns a list of shipments, including details, associated with a customer or specific sales order
Required Inputs
One or more of the following are required for a valid request: CustomerID, OrderID, RouteID, or ExpectDateRangeStart and ExpectDateRangeEnd
Optional Inputs

StatusFlagList

ShipmentNumber

ShipToSequence

RecordFetchLimit

ChunkStartPointer

Notes

Method can be requested for a specific customer, specific customer and ship-to or for a specific sales order.

If searching by CustomerID, entering 0 for the ShipToSequence returns information at the sold-to level

StatusFlagList can be entered in either of the following formats:

Loaded or L

Staged or S

En Route or E

Delivered or D

Invoiced or I

This method allows a user to request a specific number of records. Please see the Data-Chunking topic for more information

The ShipmentTotalDue returned in the dtShipmentDisplayResponse is populated only for C.O.D. orders where the ‘Priced pick & delivery’ field is set.

The following rule applies when displaying shipping tracking information:

When the Sequence = 0, the tracking information is stored on the shipment header

When the Sequence is not 0, the tracking information is stored on the shipment detail sequence specified

The system displays tracking information at the lowest level. For example, if a tracking number exists at the shipment header and another exists at the shipment detail, the system only displays the detail tracking number. If tracking numbers only exist at the shipment header, then the system displays these tracking numbers.

The PartNumber displays the part number stored on the so_detail. If this is blank, then the system searches for the related cross reference. If a single dimension was placed on the order, the dimension cross reference will be returned.

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

There is a Parent/Child relationship between dtShipment and dtShipmentDetail through OrderID and ShipmentNumber

The ItemXrefUsedToOrder displays the item cross reference field from the Sales order detail.

A one-to-many Parent/Child relationship exists between dtShipmentDisplayResponse and dtTrackingHeaderResponse through OrderID.

A one to many Parent/Child relationship exists between dtShipmentDisplayResponse and dtShipmentHeaderMessageResponse through OrderID.

A one-to-many Parent/Child relationship exists between dtShipmentDisplayResponseDetail and dtSerialNumberDetailResponse through Sequence.

A one to many Parent/Child relationship exists between dtShipmentDisplayResponseDetail and dtShipmentDetailMessageResponse through Sequence.

Version Deployed
v614

**Request body:**
```json
{
    "request": {
        "dsShipmentDisplayRequest": {
            "dtShipmentDisplayRequest": [
                {
                    "OrderID": 0,
                    "ShipmentNumber": 0,
                    "CustomerID": "",
                    "ShipToSequence": 0,
                    "ExpectDateRangeStart": "",
                    "ExpectDateRangeEnd": "",
                    "RouteID": "",
                    "StatusFlagList": "",
                    "ChunkStartPointer": 0,
                    "RecordFetchLimit": 0
                }
            ]
        }
    }
}
```

## ShippingHistoryCreate
`POST /Shipments/ShippingHistoryCreate`

Purpose
Creates shipping history record for various transaction types
Required Inputs

TranType

TranID

ShipmentStage

Optional Inputs

TranDispatchID

ShipmentNumber

AutoAssignDateTimeBy

StageBy

StageDate

StageTime

StageTimeZone

CurrentStage

Notes

Valid TranType values

DP

SO

PO

SR

RI

RO

CM

ShipmentStage value must be a valid Shipment Stage in Agility

Shipping history record may be created for a standalone dispatch, standalone transaction, or a transaction associated with a dispatch. Once a transaction is associated with a dispatch, you cannot create a shipping history record for the standalone transaction.

ShipmentNumber tag is required when creating a record for a transaction associated with a shipment on a dispatch or when the transaction is a reman input (RI) or reman output (RO). If creating for a standalone transaction (not on a dispatch, reman input, or reman output) the ShipmentNumber will be ignored.

If a transaction is associated with a dispatch, the optional TranDispatchID tag must be included.

Do not include the TranDispatchID tag when creating a record for a standalone dispatch or standalone transaction.

Include the TranDispatchID tag when creating a for a transaction associated with a dispatch.

API fails if the StageTime tag is sent and the StageDate tag is not sent.

If the StageDate, StageTime, and StageBy tags are sent, the values will be used to create the record even if the AutoAssignDateTimeBy tag is ‘true’.

StageTime value must be military time between 00:00 and 24:00.

The StageDate, StageTime and StageTimeZone values will be converted and stored based on the server’s time zone and displayed in the branch’s time zone in the Shipping History window in Agility.

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v612

**Request body:**
```json
{
    "request": {
        "TranType": "",
        "TranID": 0,
        "ShipmentStage": "",
        "ShippingHistoryCreateJSON": {
            "dsShippingHistoryCreate": {
                "dtShippingHistoryCreate": [
                    {
                        "TranDispatchID": 0,
                        "ShipmentNumber": 0,
                        "AutoAssignDateTimeBy": false,
                        "StageBy": "",
                        "StageDate": "2024-10-25",
                        "StageTime": "09:21",
                        "StageTimeZone": "",
                        "CurrentStage": true
                    }
                ]
            }
        }
    }
}
```

## ShippingHistoryDelete
`POST /Shipments/ShippingHistoryDelete`

Purpose
Deletes an existing shipping history record for various transaction types
Required Inputs

TranType

TranID

ShipmentStage

Optional Inputs

TranDispatchID

ShipmentNumber

Notes

Valid TranType values

DP

SO

PO

SR

RI

RO

CM

ShipmentStage value must be a valid Shipment Stage in Agility.

For a single shipping history record for the dispatch/transaction sent, delete that record.

The shipping history record cannot be deleted if there are multiple shipping history records for the dispatch/transaction and the Current stage is set to ‘Yes’ for the record being deleted.

ShipmentNumber tag is required when deleting a record for a transaction associated with a shipment on a dispatch or when the transaction is a reman input (RI) or reman output (RO). If deleting for a standalone transaction (not on a dispatch, reman input, or reman output) the ShipmentNumber will be ignored.

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v612

**Request body:**
```json
{
    "request": {
        "TranType": "",
        "TranID": 0,
        "ShipmentStage": "",
        "ShippingHistoryDeleteJSON": {
            "dsShippingHistoryDelete": {
                "dtShippingHistoryDelete": [
                    {
                        "TranDispatchID": 0,
                        "ShipmentNumber": 0
                    }
                ]
            }
        }
    }
}
```

## ShippingHistoryGet
`POST /Shipments/ShippingHistoryGet`

Purpose
View shipping history records for various transaction types
Required Inputs

TranType

TranID

Optional Inputs

TranDispatchID

ShipmentNumber

Notes

Valid TranType values

DP

SO

PO

SR

RI

RO

CM

TranDispatchID tag is required to return a record where a transaction is associated with a dispatch.

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v612

**Request body:**
```json
{
    "request": {
        "TranType": "",
        "TranID": 0,
        "ShippingHistoryGetJSON": {
            "dsShippingHistoryRequest": {
                "dtShippingHistoryRequest": [
                    {
                        "TranDispatchID": 0,
                        "ShipmentNumber": 0
                    }
                ]
            }
        }
    }
}
```

## ShippingHistoryUpdate
`POST /Shipments/ShippingHistoryUpdate`

Purpose
Updates an existing shipping history record for various transaction types
Required Inputs

TranType

TranID

ShipmentStage

Optional Inputs

TranDispatchID

ShipmentNumber

AutoAssignDateTimeBy

StageBy

StageDate

StageTime

StageTimeZone

CurrentStage

Notes

Valid TranType values

DP

SO

PO

SR

RI

RO

CM

ShipmentStage value must be a valid Shipment Stage in Agility.

Shipping history record may be updated for a standalone dispatch, standalone transaction, or transaction associated with a dispatch that is already created.

One shipping history record can be updated per request.

ShipmentNumber tag is required when updating a record for a transaction associated with a shipment on a dispatch or when the transaction is a reman input (RI) or reman output (RO). If updating for a standalone transaction (not on a dispatch, reman input, or reman output) the ShipmentNumber will be ignored.

If a transaction is associated with a dispatch, the optional TranDispatchID tag must be included.

Do not include the TranDispatchID tag when updating a record for a standalone dispatch or standalone transaction.

Include the TranDispatchID tag when updating a for a transaction associated with a dispatch.

API fails if the StageTime tag is sent and the StageDate tag is not sent.

If the StageDate, StageTime, and StageBy tags are sent, the values will be used to update the record even if the AutoAssignDateTimeBy tag is ‘true’.

The StageDate, StageTime and TimeZone values will be converted and stored based on the server’s time zone and displayed in the branch’s time zone in the Shipping History window in Agility.

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v612

**Request body:**
```json
{
    "request": {
        "TranType": "",
        "TranID": 0,
        "ShipmentStage": "",
        "ShippingHistoryUpdateJSON": {
            "dsShippingHistoryUpdate": {
                "dtShippingHistoryUpdate": [
                    {
                        "TranDispatchID": 0,
                        "ShipmentNumber": 0,
                        "AutoAssignDateTimeBy": true,
                        "StageBy": "",
                        "StageDate": "",
                        "StageTime": "",
                        "StageTimeZone": "",
                        "CurrentStage": true
                    }
                ]
            }
        }
    }
}
```

## ShippingStatusGet
`POST /Shipments/ShippingStatusGet`

Purpose
Returns status of sales order shipment
Required Inputs

SalesOrderID

ShipmentNum

Optional Inputs

N/A

Notes
Returns the status of the sales order shipment

Pickfile

Shipment

Relationships

ContextId and Branch come from Login

Version Deployed
v600

**Request body:**
```json
{
    "request": {
        "SalesOrderID": 0,
        "ShipmentNum": 0
    }
}
```

## ShippingTrackingDelete
`POST /Shipments/ShippingTrackingDelete`

Purpose
Delete shipping tracking information assigned to a sales order shipment or supplier return
Required Inputs

TranID

TranType

ShipmentNumber

TrackingNumber

Optional Inputs

Remaining fields in the dtTrackingDeleteRequest

Remaining fields in the dtTrackingDeleteSettings

Notes

Valid input values for the TranType field include 'SO' and 'SR'

When deleting tracking information for a supplier return ('SR'), the ShipmentNumber in the request must be set to zero.

The following rules apply to deleting shipment tracking information

If the requesting transaction is invoiced or canceled, a failure occurs

If the requesting sales order shipment is invoiced, a failure occurs

If an open dispatch is not found for the sales order shipment or supplier return, a failure occurs

If the requesting transaction is found on multiple dispatch transactions, a failure occurs

If the tracking number isn’t assigned to any details and more than one transaction is on the same dispatch, a failure occurs

If the tracking number is assigned to transaction details for multiple transactions on the same dispatch, a failure occurs

When the carrier assigned to the dispatch transaction is the default carrier assigned in Branch Parameters, and all containers are removed from the dispatch, and there are no other transactions on the dispatch the dispatch is deleted. If the carrier is not the default carrier assigned in Branch Parameters the dispatch is canceled.

The customer charge or order cost applied using the ShippingTrackingUpdateByPick or ShippingTrackingUpdateByShipment methods are deleted or updated from the shipment when the DeleteCharges or DeleteOrderCosts values are true.

If the DeleteCharges or DeleteOrderCosts tags are omitted, the default is set to true. The value must be set as false to retain the associated header charge or order cost record on the shipment.

The associated customer charge or order cost on the shipment is reduced by the same amount that was originally applied.

If the customer charge or order cost amount is reduced to or below 0, then the record is deleted from the shipment.

Relationships

ContextId and Branch come from Login

Valid values for SalesOrderID and ShipmentNumber come from ShipmentsList

Version Deployed
v600

**Request body:**
```json
{
    "request": {
        "TranID": 0,
        "TranType": "",
        "ShipmentNumber": 0,
        "TrackingDeleteRequestJSON": {
            "dsTrackingDeleteSettings": {
                "dtTrackingDeleteSettings": [
                    {
                        "DeleteCharges": true,
                        "DeleteOrderCosts": true
                    }
                ]
            },
            "dsTrackingDeleteRequest": {
                "dtTrackingDeleteRequest": [
                    {
                        "TrackingNumber": ""
                    }
                ]
            }
        }
    }
}
```

## ShippingTrackingUpdateByPick
`POST /Shipments/ShippingTrackingUpdateByPick`

Purpose
Creates a shipment based off a resolved pick ID and stores tracking information for the shipment on an auto-created dispatch transaction
Required Inputs

SalesOrderID

PickID

TrackingNumber

Optional Inputs

Remaining fields in the dtShipmentUpdateSettings, dtTrackingDetailRequest, and dtTrackingDetailItemRequest

Notes

A sales order shipment is created and a dispatch transaction for the shipment is auto generated when the following criteria are met:

Items for the tracking number are fully resolved in the pick file

Dispatch is not assigned to the pick ID or sales order

A default carrier is assigned in Branch parameters

TrackingNumber does not exceed 30 characters

Sales order is not on credit hold or has credit approval pending

Order is ship complete and has multiple pick files

In the event Transaction Criteria Order Restriction Exception records exist for items in the pick file, the date range specified on the exception record must include the current date

This method contains a parent/child relationship between the dsTrackingDetailRequest and the SalesOrder and PickID. Please see Parent/Child relationship topic for more information

There is a many to one relationship between the dsTrackingDetailRequest and SalesOrderID and PickID as the method allows the input of multiple tracking numbers.

Valid values for ContainerWeightUOM: LB, KG. If this field is not sent, the system defaults to a UOM of LB.

The PickID value cannot contain any leading zeroes.

The following rules apply to the ShipVia tag:

If a valid ship via is sent in the request, the sales order header ship via is updated with this value on creating the shipment. Because the ship via change may trigger other changes on the order, such as a change in tax calculations, review any order information as needed.

If an invalid or inactive ship via is sent in the request, a failure occurs.

If a blank value is sent for the ship via, no change occurs to the sales order header ship via.

If the ShipVia tag is not sent in the request, no change occurs to the sales order header ship via.

If the ShipVia tag sent includes a value that matches a routing parameter record, the system creates the dispatch for the routing parameter instead of using the default carrier assigned in Branch Parameters.

The following rules apply to the valid values for ShipmentStatusFlag tag: - The shipment status is updated based on the following valid values for ShipmentStatusFlag:

Loaded or L

Staged or S

En Route or E

Delivered or D - If an invalid or blank value is sent for the ShipmentStatusFlag or if the ShipmentStatusFlag is not sent, the system reads the customer branch ship-to Shipment Status setting. If a customer branch ship-to does not exist, then the system reads the customer ship-to Shipment Status setting.

A customer charge or order cost are applied to the shipment when the following criteria are met:

ShipmentCharge and ShipmentCost must be a positive amount.

Shipping/Tracking service on the ShipVia sent or on the order’s Ship Via when the ShipVia is not sent matches the Shipping/Tracking service on a customer charge or order cost.

Applies per on the customer charge or order cost is set to Order.

If more than one customer charge or order cost applies, the system uses the customer charge or order cost with the specified sale type.

If more than one customer charge or order cost applies with the same sale type setting, the system uses the first record alphanumerically.

If the same customer charge or order cost already exists on a prior shipment, the total amount for the order is increased and the prior shipment is unaffected.

If more than one container ID/tracking number is created for a single shipment, the customer charge or order cost is applied based on the container weight.

For example, if tracking number A has a container weight of 50 lbs and tracking number B has a container weight of 25 lbs, then a customer charge amount of 60 will allocate 40 to tracking number A and 20 to tracking number B.

If any containers have 0 weight or no weight defined, then the customer charge or order cost is applied evenly across each tracking number.

This method contains a parent/child relationship between the dtTrackingDetailItemRequest and the TrackingNumber. Please see Parent/Child relationship topic for more information

There is a many to one relationship between the dtTrackingDetailItemRequest and the TrackingNumber as the method allows you the option to specify items for each tracking number. - When multiple TrackingNumbers are sent in without the dtTrackingDetailItemRequest, the tracking information is stored at the shipment level on the auto generated dispatch transaction. - When a single TrackingNumber is sent in without the dtTrackingDetailItemRequest, the tracking information is stored at the item level for all items within the pick file. - When a TrackingNumber is sent in with dtTrackingDetailItemRequest fields, the tracking information is stored at the shipment/item level on the auto generated dispatch transaction.

Each item within the pick file must be specified in the dtTrackingDetailItemRequest in order to save tracking information at the item level.

The following rules apply when sending multiple tracking numbers in a single request

The dtTrackingDetailItemRequest must be excluded from the request to save all tracking numbers at the shipment level.

The dtTrackingDetailItemRequest must be included for each tracking number to save all tracking numbers at the shipment/item level.

The system does not allow some tracking numbers to include dtTrackingItemDetailRequest and others to exclude dtTrackingItemDetailRequest tags in a single request

If multiple resolved pick files exist on the sales order specified in the request, the system updates the ShipmentNumber on the sales order’s remaining resolved pick files. Use the PickFileList in this scenario to capture the most current ShipmentNumber associated with an PickID.

An S856 ASN is auto created when the customer ship-to is set to send S856 ASNs.

If the customer ship-to is not set to use the S856 ASN, a printed ASN report is auto created if the customer ship-to record is set to ‘Auto send ASN with WMS shipment and shipping tracking API’s’.

Relationships

ContextId and Branch come from Login

Valid values for OrderId, PickID and fields within the dtTrackingDetailItemRequest come from PickFileList

Version Deployed
v555

**Request body:**
```json
{
    "request": {
        "SalesOrderID": 0,
        "PickID": 0,
        "ShippingTrackingUpdateJSON": {
            "dsShipmentUpdateSettings": {
                "dtShipmentUpdateSettings": [
                    {
                        "ShipVia": "",
                        "ShipDate": "2022-02-27",
                        "ShipmentStatusFlag": "",
                        "ShipmentCharge": 0,
                        "ShipmentCost": 0
                    }
                ]
            },
            "dsTrackingDetailRequest": {
                "dtTrackingDetailRequest": [
                    {
                        "TrackingNumber": "",
                        "ContainerWeight": 0,
                        "ContainerWeightUOM": "",
                        "ContainerLength": 0,
                        "ContainerWidth": 0,
                        "ContainerHeight": 0,
                        "dtTrackingDetailItemRequest": [
                            {
                                "ItemCode": "",
                                "DetailSequence": 0,
                                "Quantity": 0,
                                "QtyUOM": ""
                            }
                        ]
                    },
                    {
                        "TrackingNumber": "",
                        "ContainerWeight": 0,
                        "ContainerWeightUOM": "",
                        "ContainerLength": 0,
                        "ContainerWidth": 0,
                        "ContainerHeight": 0,
                        "dtTrackingDetailItemRequest": [
                            {
                                "ItemCode": "",
                                "DetailSequence": 0,
                                "Quantity": 0,
                                "QtyUOM": ""
                            },
                            {
                                "ItemCode": "",
                                "DetailSequence": 0,
                                "Quantity": 0,
                                "QtyUOM": ""
                            }
                        ]
                    }
                ]
            }
        }
    }
}
```

## ShippingTrackingUpdateByShipment
`POST /Shipments/ShippingTrackingUpdateByShipment`

Purpose
Allow updates to container/tracking information for a shipment
Required Inputs

SalesOrderID

ShipmentNumber

TrackingNumber

Optional Inputs

Remaining fields in the dtShipmentUpdateByShipSettings, dtTrackingDetailByShipRequest, and dtTrackingDtlByShipItemRequest

Notes

This method contains a parent/child relationship between the dsTrackingDetailByShipRequest and the SalesOrderID and ShipmentNumber. Please see Parent/Child relationship topic for more information

There is a many to one relationship between the dsTrackingDetailByShipRequest and SalesOrderID and ShipmentNumber as the method allows the input of multiple tracking numbers.

Valid values for ContainerWeightUOM: LB, KG. If this field is not sent, the system defaults to a UOM of LB.

The following rules apply to the ShipVia tag:

When the Sales Order Parameter field Shipment ship via is set to "At invoicing", the sales order header ship via is updated when a valid ship via is sent in the request.

When the Sales Order Parameter field Shipment ship via is set to "At shipment creation", the shipment ship via is updated when a valid ship via is sent in the request.

Because the ship via change may trigger other changes on the order, such as a change in tax calculations, review any order information as needed.

If an invalid or inactive ship via is sent in the request, a failure occurs.

If a blank value is sent for the ship via or the ShipVia tag is not sent, no change occurs to the sales order header ship via. If the Sales Order Parameter field Shipment ship via is set to "At shipment creation" in this situation, the system retains the existing shipment ship via value.

The following rules apply to the valid values for ShipmentStatusFlag tag:

The shipment status is updated based on receiving one of the following values in the ShipmentStatusFlag request field:

Loaded or L

Staged or S

En Route or E

Delivered or D

If an invalid value is sent in the ShipmentStatusFlag request, a failure occurs.

A customer charge or order cost is applied to the shipment when the following criteria are met:

If the ShipmentCharge and/or ShipmentCost is a positive amount

If a Shipping/Tracking service assigned to the Ship via assigned to the sales order header matches the Shipping/Tracking service assigned to a customer charge or order cost within Agility.

Applies per on the customer charge or order cost is set to Order.

If more than one customer charge or order cost applies, the system uses the customer charge or order cost with the specified sale type.

If more than one customer charge or order cost applies with the same sale type setting, the system uses the first record found.

If the same customer charge or order cost already exists on the shipment, the charge and/or cost amount is overridden with the new value received.

If more than one container ID/tracking number is created for a single shipment, the customer charge or order cost is applied based on the container weight.

For example, if tracking number A has a container weight of 50 lbs and tracking number B has a container weight of 25 lbs, then a customer charge amount of 60 will allocate 40 to tracking number A and 20 to tracking number B.

If any containers have 0 weight or no weight defined, then the customer charge or order cost is applied evenly across each tracking number.

A dispatch transaction, is created for the shipment if one does not already exist.

When a TrackingNumber is sent in with items specified in the dtTrackingDtlByShipItemRequest, dispatch details are created only for the shipment items and quantities received.

When a TrackingNumber is sent without items specified, dispatch details are created for all shipment items and quantities, with no containers assigned at the item level.

When creating a new dispatch transaction an EDI S856 ASN is auto generated for the dispatch transaction if set to generate on the EDI Customer Reference Maintenance screen.

The system does not auto process for the EDI ASN when updating an existing dispatch transaction.

When tracking information is received for a shipment that has already been dispatched, the existing dispatch transaction is updated.

If a shipment is assigned to more than one dispatch, the method fails

If the TrackingNumber sent is already assigned to the dispatch, the method fails.

If container information is assigned by detail on the existing dispatch, the request must be sent in with the dtTrackingDtlByShipItemRequest fields.

When a TrackingNumber is sent in with dtTrackingDtlByShipItemRequest fields, the quantity received for an item cannot be more than the accumulated total of what remains to be dispatched plus any dispatched quantities not previously assigned to a container for that shipment.

This method contains a parent/child relationship between the dtTrackingDetailByShipRequest and the TrackingNumber. Please see Parent/Child relationship topic for more information.

There is a many to one relationship between the dtTrackingDtlByShipItemRequest and the TrackingNumber as the method allows you the option to specify item(s) for each tracking number.

When multiple TrackingNumbers are sent in without the dtTrackingDtlByShipItemRequest, the tracking information is stored at the shipment level on the dispatch transaction.

When a single TrackingNumber is sent in without the dtTrackingDtlByShiptemRequest, the tracking information is stored at the item level for all items on the shipment.

When a TrackingNumber is sent in with dtTrackingDtlByShipItemRequest fields, the tracking information is stored at the shipment/item level on the dispatch.

When multiple TrackingNumbers are sent in the dtTrackingDtlByShipItemRequest, only items on the shipment that are specified in the dtTrackingDtlByShipItemRequest are saved with tracking information at the item level.

The following rules apply when sending multiple tracking numbers in a single request

The dtTrackingDtlByShipItemRequest must be excluded from the request to save all tracking numbers at the shipment level.

The dtTrackingDtlByShipitemRequest must be included for each tracking number to save all tracking numbers at the shipment/item level.

The system does not allow some tracking numbers to include dtTrackingDtlByShipItemRequest and others to exclude dtTrackingDtlByShipItemRequest tags in a single request.

An S856 ASN is auto created when the customer ship-to is set to send S856 ASNs.

If the customer ship-to is not set to use the S856 ASN, a printed ASN report is auto created if the customer ship-to record is set to ‘Auto send ASN with WMS shipment and shipping tracking API’s’.

Relationships

ContextId and Branch come from Login

Version Deployed
v600

**Request body:**
```json
{
    "request": {
        "SalesOrderID": 0,
        "ShipmentNumber": 0,
        "ShippingTrackingUpdateByShipJSON": {
            "dsShipmentUpdateByShipSettings": {
                "dtShipmentUpdateByShipSettings": [
                    {
                        "ShipVia": "",
                        "ShipDate": "2022-07-14",
                        "ShipmentStatusFlag": "",
                        "ShipmentCost": 0,
                        "ShipmentCharge": 0
                    }
                ]
            },
            "dsTrackingDetailByShipRequest": {
                "dtTrackingDetailByShipRequest": [
                    {
                        "TrackingNumber": "",
                        "ContainerWeight": 0,
                        "ContainerWeightUOM": "",
                        "ContainerLength": 0,
                        "ContainerWidth": 0,
                        "ContainerHeight": 0,
                        "dtTrackingDtlByShipItemRequest": [
                            {
                                "ItemCode": "",
                                "DetailSequence": 0,
                                "Quantity": 0,
                                "QtyUOM": ""
                            }
                        ]
                    },
                    {
                        "TrackingNumber": "",
                        "ContainerWeight": 0,
                        "ContainerWeightUOM": "",
                        "ContainerLength": 0,
                        "ContainerWidth": 0,
                        "ContainerHeight": 0,
                        "dtTrackingDtlByShipItemRequest": [
                            {
                                "ItemCode": "",
                                "DetailSequence": 0,
                                "Quantity": 0,
                                "QtyUOM": ""
                            }
                        ]
                    }
                ]
            }
        }
    }
}
```

---

# Supplier Service  (20 methods)

## SupplierBranchCreate
`POST /Supplier/SupplierBranchCreate`

Purpose
Create new supplier branch records
Required Inputs

SupplierID

Optional Inputs

N/A

Notes

DMSi strongly recommends reviewing dsAuditResults regardless of the ReturnCode value

For the ExpenseGLComponent request field, you must use an X or # as the placeholder character for spaces if the account or component begins with or contains spaces.

Supplier branch records are created in the branch specified in the API header

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v610

**Request body:**
```json
{
    "request": {
        "SupplierID": "",
        "SupplierBranchJSON": {
            "dsSupplierBranch": {
                "dtSupplierBranch": [
                    {
                        "ShipVia": "",
                        "FreightTerms": "",
                        "Buyer": "",
                        "Buyer2": "",
                        "PurchaseType": "",
                        "ECommercePurchaseType": "",
                        "CutOffPOChangesDay": "",
                        "CutOffPOChangesTime": "12:34",
                        "PrimaryShipFrom": 0,
                        "Region": "",
                        "DistributorNumber": "",
                        "ExpenseGLAccount": "",
                        "ExpenseGLComponent": "",
                        "ExpenseGLComponentLevel": 0,
                        "GiveFreightNotSpecifiedQuestion": "",
                        "OrderMinimumCost": 0,
                        "OrderMinimumWeight": 0,
                        "OrderMinimumLoad": 0,
                        "FreightMinimumCost": 0,
                        "FreightMinimumWeight": 0,
                        "FreightMinimumLoad": 0,
                        "WMSIncludeLinkedOrders": "",
                        "WMSIncludeVerbalPO": "",
                        "CombineLikeItemsOnPrintedPO": ""
                    }
                ]
            }
        }
    }
}
```

## SupplierBranchUpdate
`POST /Supplier/SupplierBranchUpdate`

Purpose
Updates existing supplier branch records
Required Inputs

SupplierID

Optional Inputs

N/A

Notes

DMSi strongly recommends reviewing dsAuditResults regardless of the ReturnCode value

For the ExpenseGLComponent request fields, you must use an X or # as the placeholder character for spaces if the account or component begins with or contains spaces.

Supplier branch records are updated in the branch specified in the request header

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v610

**Request body:**
```json
{
    "request": {
        "SupplierID": "",
        "SupplierBranchJSON": {
            "dsSupplierBranch": {
                "dtSupplierBranch": [
                    {
                        "ShipVia": "",
                        "FreightTerms": "",
                        "Buyer": "",
                        "Buyer2": "",
                        "PurchaseType": "",
                        "ECommercePurchaseType": "",
                        "CutOffPOChangesDay": "",
                        "CutOffPOChangesTime": "10:45",
                        "PrimaryShipFrom": 0,
                        "Region": "",
                        "DistributorNumber": "",
                        "ExpenseGLAccount": "",
                        "ExpenseGLComponent": "",
                        "ExpenseGLComponentLevel": 0,
                        "GiveFreightNotSpecifiedQuestion": "",
                        "OrderMinimumCost": 0,
                        "OrderMinimumWeight": 0,
                        "OrderMinimumLoad": 0,
                        "FreightMinimumCost": 0,
                        "FreightMinimumWeight": 0,
                        "FreightMinimumLoad": 0,
                        "WMSIncludeLinkedOrders": true,
                        "WMSIncludeVerbalPO": false,
                        "CombineLikeItemsOnPrintedPO": false
                    }
                ]
            }
        }
    }
}
```

## SupplierContact
`POST /Supplier/SupplierContact`

Purpose
Creates or updates a supplier contact
Required Inputs

SupplierID

ContactName

ContactType

ContactJSON

Optional Inputs

N/A

Notes

The supplier must exist

The country code must exist

There must be one primary supplier contact record

The contact name and contact type cannot be updated, only created

Any fields not included in the ContactJSON assume the default values of the new or existing supplier contact record

DMSi strongly recommends reviewing dsAuditResults regardless of the ReturnCode value

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v610

**Request body:**
```json
{
    "request": {
        "SupplierID": "",
        "ContactName": "",
        "ContactType": "",
        "ContactJSON": {
            "dsSupplierContact": {
                "dtSupplierContact": [
                    {
                        "Primary": true,
                        "Address1": "",
                        "Address2": "",
                        "Address3": "",
                        "City": "",
                        "State": "",
                        "ZIP": "",
                        "Country": "",
                        "Phone1": "",
                        "Phone2": "",
                        "OtherPhone": "",
                        "MobilePhone": "",
                        "Fax": "",
                        "EmailAddress": "",
                        "ContactTitle": "",
                        "Salutation": "",
                        "OtherData": "",
                        "Remarks": ""
                    }
                ]
            }
        }
    }
}
```

## SupplierCreate
`POST /Supplier/SupplierCreate`

Purpose
Creates a supplier
Required Inputs

SupplierID

SupplierName

InvoiceCostType

Optional Inputs

N/A

Notes

Creating a supplier also creates default remit-to and ship-from records with a sequence of 1.

When the ‘Auto assign supplier ID’ option in Branch Controls is set, the SupplierID field is not a required input. If the SupplierID input is not populated, the next available sequence number is used.

Any fields not included in the SupplierJSON assume the default values of a new supplier.

DMSi strongly recommends reviewing dsAuditResults regardless of the ReturnCode value

For the InvoiceCashGLComponent request field, you must use an X or # as the placeholder character for spaces if the account or component begins with or contains spaces.

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v610

**Request body:**
```json
{
    "request": {
        "SupplierID": "",
        "SupplierJSON": {
            "dsSupplier": {
                "dtSupplier": [
                    {
                        "Name": "",
                        "Address1": "",
                        "Address2": "",
                        "Address3": "",
                        "City": "",
                        "State": "",
                        "ZIP": "",
                        "Country": "",
                        "Phone": "",
                        "PhoneFormat": "",
                        "Fax": "",
                        "Website": "",
                        "DivisionID": "",
                        "GroupID": "",
                        "Currency": "",
                        "PrintCurrency": "",
                        "Active": true,
                        "Temporary": false,
                        "CarrierSupplier": true,
                        "CarrierType": "",
                        "WMSIncludeLinkedOrders": false,
                        "WMSIncludeVerbalOrders": false,
                        "HistoryDisposition": "",
                        "HistoryStartDate": "2023-01-01",
                        "HistoryDateFirstOrder": "2023-02-12",
                        "HistoryCompanyCode": "",
                        "InvoiceDefaultVoucherStatus": "",
                        "InvoiceStandardDiscount": 0,
                        "InvoicePaymentMethod": "",
                        "InvoiceDaysToClear": 0,
                        "InvoicePaymentTermsCode": "",
                        "InvoiceCreditPaymentTermsCode": "",
                        "InvoiceCostType": "",
                        "InvoiceXrefRequiredBySupplier": "",
                        "InvoiceCashGLAccount": null,
                        "InvoiceCashGLComponent": "",
                        "InvoiceCashGLComponentLevel": 0,
                        "InvoiceAllowDuplicates": true,
                        "InvoiceRejectIfDupInvoiceAndDate": true,
                        "InvoiceSuppCheckDupMonths": 0,
                        "InvoiceSuppRejectDupMonths": 0,
                        "Misc1": "",
                        "Misc2": "",
                        "Misc3": "",
                        "ClientSupplierId": ""
                    }
                ]
            }
        }
    }
}
```

## SupplierCustomFormAssignment
`POST /Supplier/SupplierCustomFormAssignment`

Purpose
Creates or updates supplier custom form settings
Required Inputs

SupplierID

StandardFormName

FormName

Optional Inputs

FormCode

Notes

Valid values for StandardFormName include the following:

Purchase Order

Supplier Return

Supplier Work Order

Freight Dispatch (Detail)

Freight Dispatch (Summary)

Valid values for FormName and FormCode come from Custom Form Name Maintenance

Relationships

ContextId and Branch come from Login

Version Deployed
v619

**Request body:**
```json
{
    "request": {
        "SupplierID": "",
        "StandardFormName": "",
        "CustomFormAssignmentJSON": {
            "dsCustomFormAssignment": {
                "dtCustomFormAssignment": [
                    {
                        "FormName": "",
                        "FormCode": ""
                    }
                ]
            }
        }
    }
}
```

## SupplierGLCreate
`POST /Supplier/SupplierGLCreate`

Purpose
Create a supplier G/L record in the current branch
Required Inputs

SupplierID

SupplierGLJSON

Optional Inputs

N/A

Notes

The supplier must exist

The G/L Account branch for the new record comes from the branch defined in the header

For the GLComponent request field, you must use an X or # as the placeholder character for spaces if the component begins with or contains spaces.

Any fields not included in the SupplierGLJSON assume the default values of the new or existing supplier G/L record

DMSi strongly recommends reviewing dsAuditResults regardless of the ReturnCode value

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v610

**Request body:**
```json
{
    "request": {
        "SupplierID": "",
        "SupplierGLJSON": {
            "dsSupplierGL": {
                "dtSupplierGL": [
                    {
                        "GLAccount": "",
                        "GLComponent": " ",
                        "GLComponentLevel": 0
                    }
                ]
            }
        }
    }
}
```

## SupplierGLDelete
`POST /Supplier/SupplierGLDelete`

Purpose
Delete a supplier G/L record in the current branch
Required Inputs

SupplierID

SupplierGLJSON

Optional Inputs

N/A

Notes

The supplier must exist

The G/L Account must be valid in the branch defined in the header

If the supplier GL account was created with a full G/L account it can only be deleted with the full G/L account sent in the request. If the supplier G/L account was created with a component and component level, it can only be deleted by entering the component and component level in the request tags

For the GLComponent request field, you must use an X or # as the placeholder character for spaces if the component begins with or contains spaces

DMSi strongly recommends reviewing dsAuditResults regardless of the ReturnCode value

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v611

**Request body:**
```json
{
    "request": {
        "SuppierID": "",
        "SupplierGLJSON": {
            "dsSupplierGL": {
                "dtSupplierGL": [
                    {
                        "GLAccount": "",
                        "GLComponent": "",
                        "GLComponentLevel": 0
                    }
                ]
            }
        }
    }
}
```

## SupplierRemittoContact
`POST /Supplier/SupplierRemittoContact`

Purpose
Creates or updates a supplier remit-to contact
Required Inputs

SupplierID

RemittoSequence

ContactName

ContactType

ContactJSON

Optional Inputs

N/A

Notes

The supplier and remit-to must exist

The country code must exist

There must be one primary supplier remit-to contact record

The contact name and contact type cannot be updated, only created

There must be an email included in the call or on the existing contact for the ‘Receive AP Remittance’ flag to be set on the record.

Any fields not included in the ContactJSON assume the default values of the new or existing supplier remit-to contact record

DMSi strongly recommends reviewing dsAuditResults regardless of the ReturnCode value

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v610

**Request body:**
```json
{
    "request": {
        "SupplierID": "",
        "RemittoSequence": 0,
        "ContactName": "",
        "ContactType": "",
        "ContactJSON": {
            "dsSupplierRemittoContact": {
                "dtSupplierRemittoContact": [
                    {
                        "Primary": false,
                        "Address1": "",
                        "Address2": "",
                        "Address3": "",
                        "City": "",
                        "State": "",
                        "ZIP": "",
                        "Country": "",
                        "Phone1": "",
                        "Phone2": "",
                        "OtherPhone": "",
                        "MobilePhone": "",
                        "Fax": "",
                        "EmailAddress": "",
                        "ReceiveAPRemittance": true,
                        "ContactTitle": "",
                        "Salutation": "",
                        "OtherData": "",
                        "Remarks": ""
                    }
                ]
            }
        }
    }
}
```

## SupplierRemittoCreate
`POST /Supplier/SupplierRemittoCreate`

Purpose
Create Supplier Remit-to record
Required Inputs

SupplierID

SupplierRemittoJSON

Optional Inputs

N/A

Notes

The Supplier record must exist before creating a Supplier Remit-to

Any fields not included in the SupplierRemittoJSON assume the default values of a new supplier remit-to

DMSi strongly recommends reviewing dsAuditResults regardless of the ReturnCode value

If an existing sequence is sent in, then the call will fail as this API is only creating remit-to records

If no sequence value is sent in, the system auto-assigns the next sequence number for the supplier

If an existing remit-to record has the Primary option set in Agility and a new remit-to is created with the Primary tag set to true, the system automatically unsets the Primary option on the existing remit-to record

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v610

**Request body:**
```json
{
    "request": {
        "SupplierID": "",
        "SupplierRemittoJSON": {
            "dsSupplierRemitto": {
                "dtSupplierRemitto": [
                    {
                        "RemittoSequence": 0,
                        "RemittoName": "",
                        "Address1": "",
                        "Address2": "",
                        "Address3": "",
                        "City": "",
                        "State": "",
                        "ZIP": "",
                        "Country": "",
                        "PhoneFormat": "",
                        "Phone": "",
                        "AccountNumber": "",
                        "Active": true,
                        "Primary": true,
                        "PrintOneCheckPerInvoice": false,
                        "ACHDetailType": "",
                        "ACHCTXQualifier": "",
                        "ACHCTXMailboxID": "",
                        "ACHCTXVersion": "",
                        "ACHCTXUsageIndicator": "",
                        "APInterfaceInvoicePaymentTerms": "",
                        "APInterfaceCreditPaymentTerms": "",
                        "APInterfaceDefaultToHoldInvoice": false,
                        "APInterfaceBranchToApplyInvoice": "",
                        "CalculateTaxInInvoiceEntry": true,
                        "TaxCode": "",
                        "APHandlingCode": "",
                        "APHandlingCodeAdditionalInfo": "",
                        "Misc1Value": "",
                        "Misc2Value": "",
                        "Misc3Value": "",
                        "Requires1099": true,
                        "Payment1099TypeCode": "",
                        "TaxID1099": "",
                        "LegalID1099": "",
                        "LegalName1099": "",
                        "AmountThisYear1099": 0,
                        "AmountLastYear1099": 0,
                        "BankAccountType": "",
                        "BankRoutingNumber": "",
                        "BankAccountNumber": ""
                    }
                ]
            }
        }
    }
}
```

## SupplierRemittosList
`POST /Supplier/SupplierRemittosList`

Purpose
Returns a list of supplier remit-tos available in the branch the user is logged into
Required Inputs

N/A

Optional Inputs

SearchBy

SearchValue

SupplierID

RemittoSequence

FetchOnlyChangedSince

ChunkStartPointer

RecordFetchLimit

IncludeInactive

Notes

This method allows a user to request supplier remit-tos that have changed since a particular date and time.

This method allows the user to search for specific supplier remit-tos with limited criteria. Please see the Searchby topic for more information

This method allows a user to request a specific number of records. Please see the Chunking topic for more information

Because the number of records to be returned based on the search criteria could be large, DMSi recommends using the chunking feature, especially when requesting a list without specific supplier criteria specified.

Valid SearchBy values:

Remit-to name

Remit-to Address 1

Remit-to Address 2

Remit-to City

Remit-to State

Remit-to Zip

Remit-to Phone

Tax ID

When SearchBy = Tax ID, the SearchValue needs to be an exact match for the value in Agility.

The TaxID1099 and BankAccountNumber are stored as encrypted values; these values are are decrypted before being sent in the response

If the input value sent for IncludeInactive is blank or null, the system saves the value as false

If the ‘View 1099 Information’ security action is denied for the API user, values for these fields will not be returned in the response

Requires1099

LegalID1099

LegalName1099

PaymentType1099Code

TaxID1099

If the ‘Update Remit-to Bank Information’ security action is denied for the API user, values for these fields will not be returned in the response

BankAccountType

BankRoutingNumber

BankAccountNumber

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v609

**Request body:**
```json
{
    "request": {
        "SearchBy": "",
        "SearchValue": "",
        "AdditionalSearchCriteriaJSON": {
            "dsSupplierRemittoSearchRequest": {
                "dtSupplierRemittoSearchRequest": [
                    {
                        "SupplierID": "",
                        "RemittoSequence": "",
                        "FetchOnlyChangedSince": null,
                        "ChunkStartPointer": 0,
                        "RecordFetchLimit": 0,
                        "IncludeInactive": false
                    }
                ]
            }
        }
    }
}
```

## SupplierRemittoUpdate
`POST /Supplier/SupplierRemittoUpdate`

Purpose
Update existing Supplier Remit-to records
Required Inputs

SupplierID

SupplierRemittoSequence

SupplierRemittoJSON

Optional Inputs

N/A

Notes

The remit-to supplier must exist

Any fields not included in the SupplierRemittoJSON assume the default values of the existing supplier remit-to record

The Primary option is unset on an existing remit-to record in Agility if updating another remit-to record as the Primary

DMSi strongly recommends reviewing dsAuditResults regardless of the ReturnCode value

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v610

**Request body:**
```json
{
    "request": {
        "SupplierID": "",
        "SupplierRemittoJSON": {
            "dsSupplierRemitto": {
                "dtSupplierRemitto": [
                    {
                        "RemittoSequence": 0,
                        "RemittoName": "",
                        "Address1": "",
                        "Address2": "",
                        "Address3": "",
                        "City": "",
                        "State": "",
                        "ZIP": "",
                        "Country": "",
                        "PhoneFormat": "",
                        "Phone": "",
                        "AccountNumber": "",
                        "Active": true,
                        "Primary": true,
                        "PrintOneCheckPerInvoice": false,
                        "ACHDetailType": "",
                        "ACHCTXQualifier": "",
                        "ACHCTXMailboxID": "",
                        "ACHCTXVersion": "",
                        "ACHCTXUsageIndicator": "",
                        "APInterfaceInvoicePaymentTerms": "",
                        "APInterfaceCreditPaymentTerms": "",
                        "APInterfaceDefaultToHoldInvoice": false,
                        "APInterfaceBranchToApplyInvoice": "",
                        "CalculateTaxInInvoiceEntry": true,
                        "TaxCode": "",
                        "APHandlingCode": "",
                        "APHandlingCodeAdditionalInfo": "",
                        "Misc1Value": "",
                        "Misc2Value": "",
                        "Misc3Value": "",
                        "Requires1099": true,
                        "Payment1099TypeCode": "",
                        "TaxID1099": "",
                        "LegalID1099": "",
                        "LegalName1099": "",
                        "AmountThisYear1099": 0,
                        "AmountLastYear1099": 0,
                        "BankAccountType": "",
                        "BankRoutingNumber": "",
                        "BankAccountNumber": ""
                    }
                ]
            }
        }
    }
}
```

## SupplierShipfromBranchCreate
`POST /Supplier/SupplierShipfromBranchCreate`

Purpose
Creates a supplier ship-from branch record
Required Inputs

SupplierID

ShipfromSequence

Optional Inputs

N/A

Notes

The supplier and ship-from must exist before creating a ship-from branch record

Any fields not included in the SupplierShipfromBranchJSON assume the default values of a new supplier ship-from branch record

DMSi strongly recommends reviewing dsAuditResults regardless of the ReturnCode value

The UpdateLead tag is processed only when the EnableMiscSettingFlags tag is set to true

The LoadUnloadCallForAppointment, LoadUnloadFromHours, and LoadUnloadToHours tags are processed only when the EnableLoadUnloadFlags is set to true

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v611

**Request body:**
```json
{
    "request": {
        "SupplierID": "",
        "ShipfromSequence": 0,
        "SupplierShipfromBranchJSON": {
            "dsSupplierShipfromBranch": {
                "dtSupplierShipfromBranch": [
                    {
                        "EnableMiscSettingFlags": true,
                        "UpdateLead": true,
                        "EnableLoadUnloadFlags": true,
                        "LoadUnloadCallForAppointment": false,
                        "LoadUnloadFromHours": "09:30",
                        "LoadUnloadToHours": "10:24"
                    }
                ]
            }
        }
    }
}
```

## SupplierShipfromBranchUpdate
`POST /Supplier/SupplierShipfromBranchUpdate`

Purpose
Updates an existing supplier ship-from branch record
Required Inputs

SupplierID

ShipfromSequence

Optional Inputs

N/A

Notes

DMSi strongly recommends reviewing dsAuditResults regardless of the ReturnCode value

Supplier ship-from branch records are updated in the branch specified in the request header

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v611

**Request body:**
```json
{
    "request": {
        "SupplierID": "",
        "ShipfromSequence": 0,
        "SupplierShipfromBranchJSON": {
            "dsSupplierShipfromBranch": {
                "dtSupplierShipfromBranch": [
                    {
                        "EnableMiscSettingFlags": true,
                        "UpdateLead": true,
                        "EnableLoadUnloadFlags": true,
                        "LoadUnloadCallForAppointment": false,
                        "LoadUnloadFromHours": "09:30",
                        "LoadUnloadToHours": "10:24"
                    }
                ]
            }
        }
    }
}
```

## SupplierShipfromContact
`POST /Supplier/SupplierShipfromContact`

Purpose
Creates or updates a supplier ship-from contact
Required Inputs

SupplierID

ShipfromSequence

ContactName

ContactType

ContactJSON

Optional Inputs

N/A

Notes

The supplier and ship-from must exist

The country code must exist

There must be one primary supplier ship-from contact record

The contact name and contact type cannot be updated, only created

Any fields not included in the ContactJSON assume the default values of the new or existing supplier ship-from contact record

DMSi strongly recommends reviewing dsAuditResults regardless of the ReturnCode value

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v610

**Request body:**
```json
{
    "request": {
        "SupplierID": "",
        "ShipfromSequence": 0,
        "ContactName": "",
        "ContactType": "",
        "ContactJSON": {
            "dsSupplierShipfromContact": {
                "dtSupplierShipfromContact": [
                    {
                        "Primary": false,
                        "Address1": "",
                        "Address2": "",
                        "Address3": "",
                        "City": "",
                        "State": "",
                        "ZIP": "",
                        "Country": "",
                        "Phone1": "",
                        "Phone2": "",
                        "OtherPhone": "",
                        "MobilePhone": "",
                        "Fax": "",
                        "EmailAddress": "",
                        "ContactTitle": "",
                        "Salutation": "",
                        "OtherData": "",
                        "IncludeInfoInFormsSrcData": false,
                        "Remarks": ""
                    }
                ]
            }
        }
    }
}
```

## SupplierShipfromCreate
`POST /Supplier/SupplierShipfromCreate`

Purpose
Creates a ship-from supplier record
Required Inputs

SupplierID

Optional Inputs

ShipfromSequence

Notes

The supplier must exist before creating a ship-from supplier

Any fields not included in the SupplierShipfromJSON assume the default values of a new supplier ship-from

DMSi strongly recommends reviewing dsAuditResults regardless of the ReturnCode value

The system auto assigns the next sequential number as the ship-from sequence if the ShipfromSequence tag is not included in the request

For the GrantAccessToAllBranchesOnCreate field, if any branch shares supplier ship-froms with the branch sent in the API header and shares item suppliers with other branches, access will be granted to all branches whether a true or false value is sent

If an existing ship-from record has the Primary option set in Agility and a new ship-from is created with the Primary tag set to true, the system will automatically unset the Primary option on the existing ship-from record

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v611

**Request body:**
```json
{
    "request": {
        "SupplierID": "",
        "SupplierShipfromJSON": {
            "dsSupplierShipfrom": {
                "dtSupplierShipfrom": [
                    {
                        "ShipfromSequence": 0,
                        "GrantAccessToAllBranchesOnCreate": false,
                        "ShipfromName": "",
                        "Address1": "",
                        "Address2": "",
                        "Address3": "",
                        "City": "",
                        "State": "",
                        "ZIP": "",
                        "Country": "",
                        "PhoneFormat": "",
                        "Phone": "",
                        "Fax": "",
                        "Memo": "",
                        "AssignAsDescToTallyRecords": true,
                        "Primary": true,
                        "NewItemSuppForNewPrimaryShipfrom": false,
                        "Active": true,
                        "UpdateLead": true,
                        "AutoRecvAutoDisplayInvoiceEntry": true,
                        "APReconBalanceBy": "",
                        "LoadUnloadCallForAppointment": true,
                        "LoadUnloadFromHours": "",
                        "LoadUnloadToHours": "",
                        "Misc1Value": "",
                        "Misc2Value": "",
                        "Misc3Value": ""
                    }
                ]
            }
        }
    }
}
```

## SupplierShipfromLaserControls
`POST /Supplier/SupplierShipfromLaserControls`

Purpose
Creates or updates supplier ship-from laser controls
Required Inputs

SupplierID

ShipfromSequence

FormType

PrinterSequence

LaserControlJSON

Optional Inputs

N/A

Notes

The supplier ship-from must exist

Any fields not included in the LaserControlJSON assume the default values of the new or existing supplier ship-from laser control record

DMSi strongly recommends reviewing dsAuditResults regardless of the ReturnCode value

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v611

**Request body:**
```json
{
    "request": {
        "SupplierID": "",
        "ShipfromSequence": 0,
        "FormType": "",
        "PrinterSequence": 0,
        "LaserControlJSON": {
            "dsSupplierShipfromLaserControls": {
                "dtSupplierShipfromLaserControls": [
                    {
                        "PrinterName": "",
                        "FaxEmailToSource": "",
                        "Fax": "",
                        "Email": "",
                        "Copies": 0,
                        "FormFooter": ""
                    }
                ]
            }
        }
    }
}
```

## SupplierShipfromsList
`POST /Supplier/SupplierShipfromsList`

Purpose
Returns a list of supplier ship-from records
Required Inputs

N/A

Optional Inputs

SearchBy

SearchValue

SupplierID

ShipfromSequence

FetchOnlyChangedSince

ChunkStartPointer

RecordFetchLimit

IncludeInactive

Notes

This method allows the user to search for specific supplier ship-froms with limited criteria. Please see the Searchby topic for more information.

This method allows a user to request supplier ship-froms that have changed since a particular date and time.

This method allows a user to request a specific number of records. Please see the Chunking topic for more information.

Because the number of records to be returned based on the search criteria could be large, DMSi recommends using the chunking feature, especially when requesting a list without specific supplier criteria specified.

If the input value sent for IncludeInactive is blank or null, the system saves the value as false.

Valid SearchBy values:

Ship-from Name

Ship-from Address 1

Ship-from Address 2

Ship-from City

Ship-from State

Ship-from Zip

Ship-from Phone

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v611

**Request body:**
```json
{
    "request": {
        "SearchBy": "",
        "SearchValue": "",
        "AdditionalSearchCriteriaJSON": {
            "dsSupplierShipfromSearchRequest": {
                "dtSupplierShipfromSearchRequest": [
                    {
                        "SupplierID": "",
                        "ShipfromSequence": 0,
                        "FetchOnlyChangedSince": "2024-02-08T10:00:00.000",
                        "ChunkStartPointer": 0,
                        "RecordFetchLimit": 0,
                        "IncludeInactive": false
                    }
                ]
            }
        }
    }
}
```

## SupplierShipfromUpdate
`POST /Supplier/SupplierShipfromUpdate`

Purpose
Updates an existing supplier ship-from record
Required Inputs

SupplierID

ShipfromSequence

SupplierShipfromJSON

Optional Inputs

N/A

Notes

The ship-from supplier record must exist

Any fields not included in the SupplierShipfromJSON assume the default values of the existing supplier ship-from record

The Primary option will be unset on an existing ship-from record in Agility if updating another ship-from record as the Primary

DMSi strongly recommends reviewing dsAuditResults regardless of the ReturnCode value

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v611

**Request body:**
```json
{
    "request": {
        "SupplierID": "",
        "SupplierShipfromJSON": {
            "dsSupplierShipfrom": {
                "dtSupplierShipfrom": [
                    {
                        "ShipfromSequence": 0,
                        "ShipfromName": "",
                        "Address1": "",
                        "Address2": "",
                        "Address3": "",
                        "City": "",
                        "State": "",
                        "ZIP": "",
                        "Country": "",
                        "PhoneFormat": "",
                        "Phone": "",
                        "Fax": "",
                        "Memo": "",
                        "AssignAsDescToTallyRecords": true,
                        "Primary": false,
                        "NewItemSuppForNewPrimaryShipfrom": false,
                        "Active": true,
                        "UpdateLead": true,
                        "AutoRecvAutoDisplayInvoiceEntry": false,
                        "APReconBalanceBy": "",
                        "LoadUnloadCallForAppointment": false,
                        "LoadUnloadFromHours": "1000",
                        "LoadUnloadToHours": "1200",
                        "Misc1Value": "",
                        "Misc2Value": "",
                        "Misc3Value": ""
                    }
                ]
            }
        }
    }
}
```

## SuppliersList
`POST /Supplier/SuppliersList`

Purpose
Returns a list of suppliers available to the user
Required Inputs

SearchBy

SearchValue

Optional Inputs

FetchOnlyChangedSince

ChunkStartPointer

RecordFetchLimit

IncludeInactive

Notes

The FetchOnlyChangedSince parameter allows the user to determine if they would like records returned that have been modified since a particular date/time. This parameter is evaluated against the update date/time on the record.

This method allows a user to request a specific number of records. Please see the Chunking topic for more information.

If the input value sent for IncludeInactive is blank or null, the system saves the value as false.

Valid SearchBy options:

Supplier Name

Supplier ID

Supplier Address 1

Supplier Address 2

Supplier City

Supplier State

Supplier ZIP

Supplier Phone

Supplier Group ID

Supplier Division ID

A value of < all > can be specified in SearchValue (Note: Do not include spaces between the characters and the word "all" when including this in the request.)

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v610

**Request body:**
```json
{
    "request": {
        "SearchBy": "",
        "SearchValue": "",
        "AdditionalSearchCriteriaJSON": {
            "dsSupplierSearchRequest": {
                "dtSupplierSearchRequest": [
                    {
                        "IncludeInactive": true,
                        "FetchOnlyChangedSince": "2024-04-24T08:39:32",
                        "ChunkStartPointer": 0,
                        "RecordFetchLimit": 0
                    }
                ]
            }
        }
    }
}
```

## SupplierUpdate
`POST /Supplier/SupplierUpdate`

Purpose
Update existing supplier record
Required Inputs

SupplierID

Optional Inputs

N/A

Notes

DMSi strongly recommends reviewing dsAuditResults regardless of the ReturnCode value

For the InvoiceCashGLComponent request field, you must use an X or # as the placeholder character for spaces if the account or component begins with or contains spaces.

The UpdShipFromActiveWhenSetActive request field allows you to set all ship-from records as active when setting the supplier record as active.

The UpdOpenVoucherWithStatusChange request field allows you to update all open vouchers for the updated supplier with the updated invoice voucher status.

Relationships

ContextId and Branch come from Login

Alternate branches come from BranchList

Version Deployed
v610

**Request body:**
```json
{
    "request": {
        "SupplierID": "",
        "SupplierJSON": {
            "dsSupplier": {
                "dtSupplier": [
                    {
                        "Name": "",
                        "Address1": "",
                        "Address2": "",
                        "Address3": "",
                        "City": "",
                        "State": "",
                        "ZIP": "",
                        "Country": "",
                        "Phone": "",
                        "PhoneFormat": "",
                        "Fax": "",
                        "Website": "",
                        "DivisionID": "",
                        "GroupID": "",
                        "Currency": "",
                        "PrintCurrency": "",
                        "Active": true,
                        "UpdShipFromActiveWhenSetActive": false,
                        "Temporary": false,
                        "CarrierSupplier": true,
                        "CarrierType": "",
                        "WMSIncludeLinkedOrders": false,
                        "WMSIncludeVerbalOrders": false,
                        "HistoryDisposition": "",
                        "HistoryStartDate": "2024-12-12",
                        "HistoryDateFirstOrder": "2022-12-12",
                        "HistoryCompanyCode": "",
                        "InvoiceDefaultVoucherStatus": "",
                        "UpdOpenVoucherWithStatusChange": false,
                        "InvoicePaymentMethod": "",
                        "InvoiceDaysToClear": 0,
                        "InvoicePaymentTermsCode": "",
                        "InvoiceCreditPaymentTermsCode": "",
                        "InvoiceCostType": "",
                        "InvoiceXrefRequiredBySupplier": "",
                        "InvoiceCashGLAccount": "",
                        "InvoiceCashGLComponent": "",
                        "InvoiceCashGLComponentLevel": 0,
                        "InvoiceAllowDuplicates": "",
                        "InvoiceRejectIfDupInvoiceAndDate": false,
                        "InvoiceSuppCheckDupMonths": 0,
                        "InvoiceSuppRejectDupMonths": 0,
                        "Misc1Value": "",
                        "Misc2Value": "",
                        "Misc3Value": "",
                        "ClientSupplierId": ""
                    }
                ]
            }
        }
    }
}
```