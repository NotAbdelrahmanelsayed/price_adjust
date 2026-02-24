# Proposal for Payment Reconciliation

This is a proposal to create a button that reconciles every voucher in the system. invoices against payments and journal entries.

## The problem

This is not a straightforward task, as it has some risk. 
If something goes wrong, the accounts in the system will be corrupted. 

## Challenge

To make sure that we are safe hundered percent, most of the time will be spent on creating robust testing to cover all the possibilities of making the wrong transaction. 

## Planned Steps

1. Read the Payment reconciliation code carefully to understand core logic (1 - 2 hours)
2. adding ui button (10-20 minutes)
3. Backend Logic (fetch outstanding invoices and match unallocated payments/JE across all parties and reconcile them) (4- 6 hours)
4. Covering Different Edge cases (1-2 hours)
  - already allocated payments
  - multiple companies
  - performance issues
5. Testing, gathering random vouchers, and testing the button on them (1-2 hours)
6. Taking a backup before running the app live, and running it (1 hour)

## Estimation
8-13 hours
