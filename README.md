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