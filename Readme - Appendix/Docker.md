# Docker 🐋
Since the client had the requirement of running the process on premises – with the exception of JotForms, which they already use – the project team created a Docker image. This enables the client's IT team to set up the Python workers with minimal effort. This section will describe what needs to be done to set up the Docker container.

Because the project team did not have access to the client's internal network, which hindered testing, the web app has not been put in a Docker image yet. This will be done if the client decides to implement the process.


## Step 1: Set up the folders

The first step is to create a folder that contains the files, that the container requires to run. In this document this folder will from now on be referred to as the Docker folder.
The required files are:
1. config.json
2. password.txt
3. api_key.txt

For easier handling the exported Docker image "feedback-management-app.tar" can also be safed in this folder.

Additionally, a folder that will later contain the Excel database is required. This folder will be referred to as database folder.


## Step 2: Configure the config file

Since the database is created from the container itself, it cannot be mounted like the other three files. The "fileshare" refers to a shared directory between the host machine and the Docker container, allowing the container to access files from the host system. In the configuration file, the path to any file that resides in this shared directory needs to start with "/host/" to ensure the container correctly references the host's file system.

As the other files are in the Docker folder and are mounted later in the Docker build command, they do not need the "/host/" prefix in the config file.

```json
{
  "camundaEngineUrl": "https://digibp.engine.martinlab.science/engine-rest",
  "excelFilePath": "/host/form_data.xlsm",
  "passwordFilePath": "password.txt",
  "apiKeyPath": "api_key.txt",
  "tenantID": "25DIGIBP12",
  "documentationFormID": "251324255618051",
  "supplementationFormID": "251256180381049",
  "emailHost": "mail.infomaniak.com",
  "emailUser": "digipro-demo@ikmail.com",
  "emailPort": 465,
  "ceoName": "Helga Geschäftsführerin",
  "ceoEmail": "digipro-demo@ikmail.com",
  "departments": [
    {
    "departmentName": "testDepartment",
    "departmentEmail": "digipro-demo@ikmail.com"
    },
    {
    "departmentName": "testDepartment2",
    "departmentEmail": "digipro-demo@ikmail.com"
    }
  ]
}
```


## Step 3: Import the Docker image

First open Powershell and navigate to the Docker folder. Also do not forget to launch the Docker engine.
Then execute the following command:

```powershell
docker load -i feedback-management-app.tar
```

This will load the image into Docker’s local image registry on the new machine.

---

This command verifies if the image could be imported.

```powershell
docker images
```

The output should look something like this.

```
REPOSITORY               TAG       IMAGE ID       CREATED         SIZE
feedback-management-app  latest    abc123456789   ...             ...
```


## Step 4: Lauch the docker container

The final step is to launch the doker container. The powershell terminal should still point to the Docker folder. In the following command the penultimate line needs to be changed. There the path **from the first quotation mark to the colon** needs to be changed to the database folder's path.

```powershell
docker run --rm `
  -v "${PWD}\config.json:/app/config.json" `
  -v "${PWD}\api_key.txt:/app/api_key.txt" `
  -v "${PWD}\password.txt:/app/password.txt" `
  -v "C:\users\ChangeThis\Documents\DatabaseFolder:/host" `
  feedback-management-app
```

All workers should now launch. Press Ctrl+C to shut them down again.
