# Create virtual environment and install dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install django djangorestframework drf-spectacular

# Create Django project and app
django-admin startproject slot_machine_api
cd slot_machine_api

# Load initial symbols data (after creating fixture)
python manage.py loaddata symbols

# Run the development server
python manage.py runserver

# Docker Setup
## Prerequisites
- Docker installed (https://docs.docker.com/get-docker/)
- Docker Compose installed (https://docs.docker.com/compose/install/)

## Running with Docker
1. Build and start the containers:
```
docker-compose up -d
```

2. Access the application at http://localhost:8000

3. To stop the containers:
```
docker-compose down
```

## Docker Commands
- View logs:
```
docker-compose logs -f
```

- Run migrations:
```
docker-compose exec web python slot_machine_api/manage.py migrate
```

- Create a superuser:
```
docker-compose exec web python slot_machine_api/manage.py createsuperuser
```

- Load fixtures:
```
docker-compose exec web python slot_machine_api/manage.py loaddata symbols
```

# SonarQube Integration
## Prerequisites
- SonarQube server running (local or remote)
- SonarScanner installed (see installation instructions below)

### Installing SonarScanner

#### macOS
1. Using Homebrew:
```
brew install sonar-scanner
```

2. Manual installation:
   - Download the SonarScanner ZIP from https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/
   - Extract it to a directory (e.g., `/opt/sonar-scanner` or `~/sonar-scanner`)
   - Add the bin directory to your PATH in `~/.zshrc` or `~/.bash_profile`:
   ```
   export PATH=$PATH:/path/to/sonar-scanner/bin
   ```
   - Apply changes with: `source ~/.zshrc` or `source ~/.bash_profile`

#### Windows
1. Download the SonarScanner ZIP from https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/
2. Extract it to a directory (e.g., `C:\sonar-scanner`)
3. Add the bin directory to your PATH:
   - Right-click on 'This PC' > Properties > Advanced system settings > Environment Variables
   - Edit the Path variable and add the path to the bin directory (e.g., `C:\sonar-scanner\bin`)

#### Linux
1. Download the SonarScanner ZIP from https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/
2. Extract it to a directory (e.g., `/opt/sonar-scanner` or `~/sonar-scanner`)
3. Add the bin directory to your PATH in `~/.bashrc` or `~/.profile`:
   ```
   export PATH=$PATH:/path/to/sonar-scanner/bin
   ```
4. Apply changes with: `source ~/.bashrc` or `source ~/.profile`

### Troubleshooting
- If you get `command not found: sonar-scanner`, ensure that:
  - SonarScanner is installed correctly
  - The bin directory is added to your PATH
  - You've reloaded your shell configuration or opened a new terminal
- Verify installation with: `sonar-scanner -v` which should display the version information

## Setup
1. Install required packages for code coverage:
```
pip install coverage pytest pytest-django
```

2. Run tests with coverage:
```
coverage run --source=slot_machine_api manage.py test
coverage xml -o coverage.xml
```

3. Run SonarQube scan:
```
sonar-scanner
```

The SonarQube configuration is in the `sonar-project.properties` file at the root of the project.

## Using SonarQube with Docker
The project includes SonarQube and SonarScanner services in the Docker Compose configuration, making it easy to run code analysis without installing SonarQube or SonarScanner locally.

1. Start the Docker containers (including SonarQube):
```
docker-compose up -d
```

2. Wait for SonarQube to initialize (this may take a minute or two). You can check the logs with:
```
docker-compose logs -f sonarqube
```

3. Access the SonarQube dashboard at http://localhost:9000 (default credentials: admin/admin)

4. Run tests with coverage in the web container:
```
docker-compose exec web bash -c "cd slot_machine_api && coverage run --source=. manage.py test && coverage xml -o coverage.xml"
```

5. Run SonarQube analysis using the sonarscanner container:
```
docker-compose exec sonarscanner sonar-scanner -Dsonar.projectBaseDir=/usr/src
```

6. View the analysis results in the SonarQube dashboard at http://localhost:9000

### Troubleshooting SonarQube in Docker

If you encounter issues with the SonarQube container stopping unexpectedly, check the following:

1. **System Requirements**: SonarQube requires significant resources to run properly:
   - At least 2GB of RAM allocated to the Docker container
   - Sufficient disk space for the volumes
   - Proper file descriptor limits

2. **Host System Configuration**: On Linux hosts, you may need to increase the max_map_count:
   ```
   sudo sysctl -w vm.max_map_count=262144
   ```
   To make this change permanent, add the following to `/etc/sysctl.conf`:
   ```
   vm.max_map_count=262144
   ```

3. **Container Logs**: Check the logs for specific errors:
   ```
   docker-compose logs sonarqube
   ```

4. **Memory Issues**: If you see ElasticSearch errors, it's often related to memory. The docker-compose.yml file has been configured with appropriate memory settings, but you may need to adjust them based on your system capabilities.
