# Running the Project

To get the project up and running, follow these steps:

1. **Create `.env` Files**: 
   - Create a `.env` file in the root directory and another inside the `app` directory based on the provided `example.env` templates.

2. **Build the Project**:
   - Run the command `docker compose build` to build the project. This step compiles the Docker images necessary for the project.

3. **Run the Project**:
   - Execute `docker compose up -d` to start the project in detached mode. This will run your containers in the background.

4. **Check Logs**:
   - Use `docker logs -f web` to follow the logs of the web container in real-time. This is useful for monitoring the application's output or debugging issues.

5. **Check Containers Status**:
   - To view the status of all containers, use `docker ps -a`. This command lists all containers, their IDs, status, and other details.

6. **Stop the Project**:
   - When you need to stop all running containers, execute `docker compose down`. This command stops and removes all containers, networks, and volumes created by \`docker compose up\`.

# Keycloak Configuration

1. **Check Keycloak Logs**:
   - Use `docker logs -f keycloak` to follow the logs of the Keycloak container in real-time. This helps you monitor the initialization process and find the URL where Keycloak is accessible.

2. **Access Keycloak**:
   - Open the URL displayed in the console where it says "Listening on". This will take you to the Keycloak admin console.

3. **Login**:
   - Login using the superuser credentials specified in your `.env` file (`SUPERUSER_EMAIL` and `SUPERUSER_PASSWORD`).

4. **Configure Users**:
   - In the **Master Realm**, navigate to **Users**. Choose the user, set up their email and set `Email verified = True`.

5. **Create a New Realm**:
   - Create a new realm by importing data from the `SOF-realm.json` file.

6. **User Setup in SOF Realm**:
   - In the **SOF Realm**, navigate to **Users** and select the user:
     - Set up the email to be the same as the superuser.
     - In `Credentials`, set up a password and ensure `Temporary` is set to `False`.
     - In `Details`, under `Required Actions`, remove the `Update Password` action.
7. **Set Up Email Connection**:
   - In the **SOF Realm**, navigate to `Realm Settings` -> `Email` and set up the email connection.