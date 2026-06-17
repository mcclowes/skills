# Structure a chatty dashboard screen's data access

Our React dashboard has a customer detail screen that shows the customer, their last 5 invoices, their outstanding balance, and a formatted 'next action' label. Right now the frontend calls GET /customers/{id}, then GET /customers/{id}/invoices, then computes the balance and the label itself. It feels chatty and the logic is duplicated in our mobile app. Should we just add all those fields to GET /customers/{id}? How should we structure this?
