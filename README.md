# TechConf Registration Website

## Project Overview
The TechConf website allows attendees to register for an upcoming conference. Administrators can also view the list of attendees and notify all attendees via a personalized email message.

The application is currently working but the following pain points have triggered the need for migration to Azure:
 - The web application is not scalable to handle user load at peak
 - When the admin sends out notifications, it's currently taking a long time because it's looping through all attendees, resulting in some HTTP timeout exceptions
 - The current architecture is not cost-effective 

In this project, you are tasked to do the following:
- Migrate and deploy the pre-existing web app to an Azure App Service
- Migrate a PostgreSQL database backup to an Azure Postgres database instance
- Refactor the notification logic to an Azure Function via a service bus queue message

## Dependencies

You will need to install the following locally:
- [Postgres](https://www.postgresql.org/download/)
- [Visual Studio Code](https://code.visualstudio.com/download)
- [Azure Function tools V3](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=windows%2Ccsharp%2Cbash#install-the-azure-functions-core-tools)
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)
- [Azure Tools for Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=ms-vscode.vscode-node-azure-pack)

## Project Instructions

### Part 1: Create Azure Resources and Deploy Web App
1. Create a Resource group
2. Create an Azure Postgres Database single server
   - Add a new database `techconfdb`
   - Allow all IPs to connect to database server
   - Restore the database with the backup located in the data folder
3. Create a Service Bus resource with a `notificationqueue` that will be used to communicate between the web and the function
   - Open the web folder and update the following in the `config.py` file
      - `POSTGRES_URL`
      - `POSTGRES_USER`
      - `POSTGRES_PW`
      - `POSTGRES_DB`
      - `SERVICE_BUS_CONNECTION_STRING`
4. Create App Service plan
5. Create a storage account
6. Deploy the web app

### Part 2: Create and Publish Azure Function
1. Create an Azure Function in the `function` folder that is triggered by the service bus queue created in Part 1.

      **Note**: Skeleton code has been provided in the **README** file located in the `function` folder. You will need to copy/paste this code into the `__init.py__` file in the `function` folder.
      - The Azure Function should do the following:
         - Process the message which is the `notification_id`
         - Query the database using `psycopg2` library for the given notification to retrieve the subject and message
         - Query the database to retrieve a list of attendees (**email** and **first name**)
         - Loop through each attendee and send a personalized subject message
         - After the notification, update the notification status with the total number of attendees notified
2. Publish the Azure Function

### Part 3: Refactor `routes.py`
1. Refactor the post logic in `web/app/routes.py -> notification()` using servicebus `queue_client`:
   - The notification method on POST should save the notification object and queue the notification id for the function to pick it up
2. Re-deploy the web app to publish changes

## Monthly Cost Analysis
Complete a month cost analysis of each Azure resource to give an estimate total cost using the table below:

| Azure Resource           | Service Tier                                                 | Monthly Cost |
| ------------             | ------------                                                 | ------------ |
| Azure Postgres Database  | Flexible Server - B1MS - 1 vCore(s) - 2 GB                   |     12.99    |
| Azure Service Bus        | Basic - Max Msg Size 256kb - 1M Ops                          |     0.05     |
| App Function             | Basic - 1vCpu - 1.75Gb Memory - 10Gb Storage - 3 Instances   |       0      |
| Azure Web App            | Free                                                         |       0      |
| Storage Accounts         | StorageV2 (general purpose v2)                               |     19.44    |

## Architecture Explanation

This section provides an overview of the chosen architecture for both the Azure Web App and Azure Function, along with the reasoning behind each selection:

1. **Web Client as App Service**: Since the primary function of the client is to create and query notifications and retrieve attendees from the database, the web traffic load is relatively low. Therefore, a Free Tier App Service is sufficient for handling these operations. The core actions involve CRUD operations on the attendees and notifications tables, so the focus of the budget should be more on database performance and background processing.

2. **PostgreSQL Database**: Given that the application's logic is centered on querying data, a flexible server should meet the requirements. I opted for the minimum specifications in the Burstable plan, as it's more cost-effective and suitable for the expected data growth. Since the future data scaling of the project is not anticipated to be significant, advanced options like Hyperscale or Multi-server configurations are unnecessary.

3. **Azure Function App**: The background processing for the app requires more resources than the web client. The Function App and Service Bus plan are selected based on the estimated volume of emails and attendees. With the current database size, a Basic plan for both services should provide sufficient resources. These services are also easily scalable, allowing for quick adjustments without needing to scale the App Service. For now, the Basic plan offers the best balance between cost and resource optimization.

4. **Azure Service Bus**: Since the app is divided between the web client, which handles notification and attendee creation and querying, and Azure Functions for background processing, a Service Bus is needed for communication between them. The Service Bus sends messages whenever a new notification is created in the web app, and listens for messages in the notification queue to trigger the appropriate function in the background.

5. **Azure Storage Account**: The Azure Storage Account is used primarily for storing webjob-host data and secrets. Since read and write actions to the storage account are infrequent, the minimum specification is sufficient for this purpose.