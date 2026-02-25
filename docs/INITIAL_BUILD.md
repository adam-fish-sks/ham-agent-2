Create a. Workwize management platform. Data is to be pulled from the workwize APIs:

https://docs.goworkwize.com/

And inserted into a new postgress database in podman on the local machine. Tables include:

Orders
Products
Employees
Assets
Offices
Warehouses
Addresses
Offboards

Each of these have their respective APIs detailed in the workwize Documentation. 

Create a folder called data-samples on the root of the project that contains a sample of JSON pulled from each GET API for the respective tables. Get the JSON samples by using real API calls. Do not guess at the responses. Base URL is https://prod-back.goworkwize.com/api/public

The project needs to include a front end that enables navigation to table listing all the records from the assets table.

The project needs to include an AI assistant that has full access to the data.

Make sure you follow the PII scrubbing guidelines for the database.

Get the JSON samples by using real API calls. Do not guess at the responses.

Use tailwind, monorepo, prisma and turbo.

Create a python script that restarts the dev servers.