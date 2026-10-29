# Notes App with Docker

A simple Notes application built with **Flask** and **SQLite**, packaged with **Docker** and tested automatically with **GitHub Actions**. Built as a college-level DevOps project.

## Features

- Add a note (title + content)
- View all notes with creation date/time
- Edit a note
- Delete a note
- Notes are stored permanently in SQLite
- Clean, responsive UI (works on mobile too)
- Automated tests and CI pipeline

## Technology Stack

| Layer            | Technology        |
|------------------|-------------------|
| Frontend         | HTML + CSS        |
| Backend          | Python Flask      |
| Database         | SQLite            |
| Containerization | Docker            |
| Version Control  | Git + GitHub      |
| CI/CD            | GitHub Actions    |
| UI Testing       | Selenium          |
| Orchestration    | Kubernetes        |
| CI Server        | Jenkins           |

## Architecture

```
+---------+      HTTP       +------------------------+
| Browser | <-------------> |  Docker container      |
+---------+   port 5000     |  Flask app (app.py)    |
                            |        |               |
                            |   SQLite (notes.db)    |
                            +--------|---------------+
                                     |
                              Docker volume (/data)

Developer --git push--> GitHub --> GitHub Actions:
   checkout -> setup Python -> install -> pytest -> docker build
```

## Project Structure

```
Notes-App/
├── app.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .gitignore
├── README.md
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── edit.html
│   └── 404.html
├── static/
│   └── style.css
├── Jenkinsfile
├── k8s/
│   ├── deployment.yaml
│   └── service.yaml
├── tests/
│   ├── test_app.py
│   └── test_ui_selenium.py
└── .github/workflows/
    └── ci.yml
```

## Run Locally (Windows)

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000

## Run with Docker

```
docker build -t notes-app .
docker run -d --name notes-container -p 5000:5000 -v notes-data:/data notes-app
```

Open http://localhost:5000

The `-v notes-data:/data` option keeps your notes even if the container is removed.

## Docker Commands

| Task                    | Command                                   |
|-------------------------|-------------------------------------------|
| Build image             | `docker build -t notes-app .`             |
| Run container           | `docker run -d --name notes-container -p 5000:5000 -v notes-data:/data notes-app` |
| Stop container          | `docker stop notes-container`             |
| Remove container        | `docker rm notes-container`               |
| View running containers | `docker ps`                               |
| View all containers     | `docker ps -a`                            |
| View images             | `docker images`                           |
| View logs               | `docker logs notes-container`             |

## Testing

```
pytest -v
```

The tests check: app startup, home page, create, display, edit, delete, validation and 404 handling. Each test uses a temporary database, so your real notes are never touched.

## Selenium UI Test

`tests/test_ui_selenium.py` starts the app and opens it in a real (headless) Chrome browser using Selenium. It adds, edits and deletes a note by clicking the buttons. It runs together with `pytest -v`. If Chrome is not installed on your computer, this test is skipped automatically. On GitHub Actions, Chrome is pre-installed, so it runs in the pipeline.

## Kubernetes Deployment

The `k8s/` folder has a Deployment and a Service. Build the Docker image first, then enable Kubernetes in Docker Desktop (Settings > Kubernetes > Enable) and run:

```
kubectl apply -f k8s/
kubectl get pods
kubectl get services
```

Open http://localhost:30007. To remove it: `kubectl delete -f k8s/`.

(With Minikube: run `minikube image load notes-app:latest`, then `minikube service notes-service --url`.)

## Jenkins Pipeline

The `Jenkinsfile` defines the same pipeline for a Jenkins server: Checkout, Install Dependencies, Run Tests, Build Docker Image. To use it: install Jenkins, create a **Pipeline** job, choose "Pipeline script from SCM", enter your GitHub repository URL, branch `main`, script path `Jenkinsfile`, then click **Build Now**. Jenkins needs Python, Git and Docker installed on the machine where it runs.

## CI/CD Pipeline

The file `.github/workflows/ci.yml` runs on every push and pull request to `main`:

1. **Checkout** - downloads the code onto the GitHub runner
2. **Set up Python** - installs Python 3.12 (with pip cache)
3. **Install dependencies** - `pip install -r requirements.txt`
4. **Run tests** - `pytest -v` (the pipeline fails if any test fails)
5. **Build Docker image** - `docker build` confirms the Dockerfile works

This is **Continuous Integration**: every change is automatically tested and built. Deployment is intentionally left out to keep the project simple.

## Future Enhancements

- Search notes
- User login
- Push the Docker image to Docker Hub from the pipeline
- Deploy to a cloud service
- Categories / tags for notes

## Conclusion

This project shows a complete beginner-friendly DevOps flow: write code, test it, containerize it, store it in Git, and let GitHub Actions automatically verify every change.
