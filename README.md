# About Project
[Complete Guide | Run this project on your computer](https://github.com/danialafjeh/Run-My-Projects-Locally)<br>
Projects are numbered in development order. Higher numbers represent newer projects that introduce new backend tools, concepts, and increasing levels of complexity throughout my learning journey.

# Image Processor

A Django-MVT Image Processing application designed primarily as a practical learning project for implementing and understanding **Celery** and asynchronous background task processing.

The application allows users to upload images and perform four different image processing operations. Each processing operation is handled asynchronously by a Celery worker, with Redis acting as the message broker and PostgreSQL used for persistent data storage.

The project was developed from the ground up to understand how Django, Celery, Redis, PostgreSQL, Pillow, and Docker can work together as a complete backend system.

---

## Project Purpose

The primary goal of this project is to learn and implement **Celery in a real Django application** rather than simply learning its syntax in isolation.

The project focuses on understanding:

* Asynchronous task processing
* Celery workers and tasks
* Redis as a message broker
* Communication between Django and Celery
* Task queues
* Background image processing
* Tracking task status
* Handling successful and failed tasks
* Polling task status from the frontend
* Storing uploaded and processed files
* Dockerizing a Django application with Celery
* Running Django and Celery as separate services
* Connecting multiple Docker containers through a shared network
* Using PostgreSQL inside Docker
* Persistent Docker volumes
* Environment-based Django configuration

The application itself is intentionally straightforward. The main purpose is to provide a practical environment for learning and experimenting with Celery and background processing.

---

## Features

### Image Processing

The application currently provides four image processing operations:

* Resize
* Convert
* Grayscale
* Compress

Each operation is processed asynchronously through Celery.

### Resize

Allows the user to resize an uploaded image by providing the desired width and height.

The request is validated by Django before a processing job is created and sent to Celery.

### Convert

Converts an uploaded image into one of the supported output formats:

* JPEG
* PNG
* WebP

The uploaded file is also validated to ensure that it is a valid image before the task is queued.

### Grayscale

Converts the uploaded image into grayscale using Pillow.

### Compress

Compresses the uploaded image according to the selected compression settings.

---

## Asynchronous Processing

Image processing is not performed directly inside the Django request.

Instead, Django creates a processing job and sends the corresponding Celery task to Redis.

The general flow is:

```text
User
  |
  v
Django
  |
  | Create ProcessingJob
  |
  v
Redis
  |
  | Task Queue
  |
  v
Celery Worker
  |
  v
Pillow
  |
  v
Processed Image
```

This allows Django to respond to the user without having to perform the image processing inside the original HTTP request.

---

## Celery Architecture

Celery is the central learning component of this project.

Each image processing operation has its own Celery task.

For example:

```text
resize_image_task
convert_image_task
grayscale_image_task
compress_image_task
```

When Django receives a valid request, it creates a `ProcessingJob` record and queues the corresponding task using Celery.

For example:

```python
resize_image_task.delay(job.id)
```

The task ID is not used as the primary application identifier. Instead, the application tracks its own `ProcessingJob` record and uses its database ID to identify the processing operation.

---

## Redis

Redis is used as the **Celery message broker**.

Its responsibility in this project is to temporarily hold queued task messages until a Celery worker receives and processes them.

The communication flow is:

```text
Django
   |
   | Send task
   v
Redis
   |
   | Queue task
   v
Celery Worker
```

Redis is not being used as the application's primary database.

PostgreSQL is responsible for persistent application data.

---

## Celery Worker

The Celery worker is responsible for receiving queued tasks from Redis and executing them.

The worker runs separately from the Django web server.

Inside Docker, the architecture is:

```text
Django Container
    |
    | sends tasks
    v
Redis Container
    |
    | provides task queue
    v
Celery Worker Container
    |
    | executes tasks
    v
Pillow
```

The Celery container contains the Django project code and its dependencies, allowing Celery to initialize the Django project and access its settings, models, and task definitions.

However, the Django development server is not started inside the Celery container.

The Celery container only starts the Celery worker.

---

## Processing Job Status

Each processing operation is represented by a `ProcessingJob`.

The job tracks the lifecycle of an image processing operation.

The general lifecycle is:

```text
Pending
   |
   v
Processing
   |
   +---------> Completed
   |
   +---------> Failed
```

The job stores information such as:

* Operation type
* Related image
* Processing parameters
* Current status
* Processing start time
* Error information
* Result file

This allows the frontend to determine what is happening without keeping the original HTTP request open.

---

## Result Page and Status Polling

After a processing request is submitted, the user is redirected to a processing/result page.

The frontend periodically requests the processing status from Django.

The status endpoint returns information such as:

```json
{
    "status": "processing"
}
```

When processing finishes:

```json
{
    "status": "completed",
    "result_url": "..."
}
```

If processing fails:

```json
{
    "status": "failed",
    "error": "..."
}
```

The frontend uses this information to update the interface automatically.

This creates a simple asynchronous user experience:

```text
Submit
  |
  v
Pending
  |
  v
Processing
  |
  v
Completed
  |
  v
Download Result
```

---

## Error Handling

The project handles errors at multiple stages.

### Django Validation

Invalid form input is rejected before a Celery task is queued.

Examples include:

* Missing image
* Invalid image file
* Invalid resize parameters
* Unsupported output format
* Invalid compression parameters

Django messages are used to display validation errors to the user.

### Celery Task Errors

Errors that occur during actual image processing are handled by the Celery task.

If an error occurs during background processing, the corresponding `ProcessingJob` is marked as failed and the error message is stored.

The result page can then display the failure state instead of remaining indefinitely in the processing state.

---

## Image Validation

Uploaded images are validated before creating the processing job.

Pillow is used to verify that the uploaded file is actually a valid image.

This prevents obviously invalid files from being sent unnecessarily to the Celery queue.

---

## Pillow

[Pillow](https://python-pillow.org/) is used as the image processing library.

It provides the actual image manipulation functionality for:

* Resizing
* Format conversion
* Grayscale conversion
* Compression

No artificial intelligence or external image processing API is used.

The image processing is performed locally by the Celery worker.

---

## Database

PostgreSQL is used as the primary relational database.

It stores persistent application data such as:

* Uploaded image records
* Processing jobs
* Processing parameters
* Processing statuses
* Processing timestamps
* Error information
* Result file references

PostgreSQL is also containerized when the project is run with Docker.

---

## Docker Architecture

The project is fully Dockerized.

The Docker Compose setup contains four main services:

```text
                 Docker Network
                       |
       +---------------+---------------+
       |               |               |
       v               v               v
    Django           Redis         PostgreSQL
       |
       |
       v
 Celery Worker
```

More precisely:

```text
+-----------------------+
| Django Container      |
|                       |
| Django Web Server     |
+-----------+-----------+
            |
            v
+-----------------------+
| Redis Container       |
|                       |
| Celery Broker         |
+-----------+-----------+
            |
            v
+-----------------------+
| Celery Worker         |
| Container             |
|                       |
| Celery Worker         |
| Django Project Code   |
+-----------+-----------+
            |
            v
+-----------------------+
| PostgreSQL Container  |
+-----------------------+
```

### Django Service

Responsible for:

* Running Django
* Receiving HTTP requests
* Validating user input
* Creating database records
* Sending Celery tasks
* Serving the frontend
* Providing the processing status endpoint

### Celery Worker Service

Responsible for:

* Running the Celery worker
* Receiving tasks from Redis
* Executing image processing
* Updating processing job status
* Saving processed images

The Celery worker does not run the Django web server.

### Redis Service

Responsible for:

* Acting as the Celery message broker
* Holding queued task messages until a worker consumes them

### PostgreSQL Service

Responsible for:

* Persistent database storage

---

## Docker Image and Containers

The Django and Celery services are built from the same Docker image.

This does not mean that two Django servers are running.

Instead, the same project environment is used to run two different processes:

```text
Same Docker Image
       |
       +----------------------+
       |                      |
       v                      v
Django Container       Celery Container
       |                      |
   runserver              celery worker
```

This approach keeps the project code and dependencies consistent while allowing the Django web server and Celery worker to be managed independently.

---

## Docker Volumes

Two different storage approaches are used.

### PostgreSQL Named Volume

PostgreSQL uses a Docker-managed named volume:

```yaml
volumes:
  postgres_data:
```

This allows database data to persist when the PostgreSQL container is recreated.

### Media Bind Mount

Uploaded and processed images are stored using:

```yaml
- ./media:/app/media
```

This is a bind mount between the project's local `media` directory and the `/app/media` directory inside the containers.

Both Django and Celery have access to this directory because both services need to read uploaded files and write processed results.

---

## Environment Variables

Docker Compose provides the required configuration to Django and Celery through environment variables.

Examples include:

```text
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_HOST
POSTGRES_PORT
CELERY_BROKER_URL
```

Inside Docker, Django connects to PostgreSQL through the Docker service name:

```text
db
```

and Celery connects to Redis through:

```text
redis://redis:6379/0
```

This avoids using `localhost` for communication between containers.

---

## Docker Health Checks

PostgreSQL and Redis include Docker health checks.

PostgreSQL uses `pg_isready` to verify that the database is ready to accept connections.

Redis uses:

```text
redis-cli ping
```

to verify that Redis is available.

Django and Celery depend on the database and Redis services being healthy before they start.

This helps prevent application services from starting before their required dependencies are ready.

---

## Entrypoints

The project uses separate entrypoint scripts for the Django and Celery services.

### Django

The Django entrypoint performs the database migrations and then starts the Django development server.

```text
Django entrypoint
    |
    +-- migrate
    |
    +-- runserver
```

### Celery

The Celery entrypoint starts the Celery worker:

```text
Celery entrypoint
    |
    +-- celery worker
```

This keeps the responsibilities of the two containers clear.

---

## Frontend

The application uses a modern single-page interface.

There is no traditional navigation bar or separate page for each operation.

Instead, the main page contains the available image processing operations and opens the corresponding operation interface directly on the page.

The available operations are:

* Resize
* Convert
* Grayscale
* Compress

The interface also provides:

* File selection
* Operation-specific form fields
* HTML form validation
* Processing states
* Loading indicators
* Error messages
* Successful result states
* Download functionality
* Return to the main page

The result interface automatically monitors the processing job and updates the page when processing finishes.
The frontend is based on a ready-made website template from [Tooplate.com](https://www.tooplate.com/).
The template was modified and adapted to fit the requirements, functionality, structure, and visual needs of this project.

---

## Frontend Error Handling

Django messages are displayed in the relevant operation interface when validation fails before the task is queued.

This provides immediate feedback for problems such as:

* Missing image
* Invalid image
* Invalid parameters
* Unsupported format

Errors that occur during background processing are instead stored in the `ProcessingJob` and displayed through the processing/result interface.

---

## Main Technologies

| Technology     | Purpose                                             |
| -------------- | --------------------------------------------------- |
| Python         | Main programming language                           |
| Django         | Web framework and application backend               |
| Celery         | Asynchronous background task processing             |
| Redis          | Celery message broker                               |
| PostgreSQL     | Relational database                                 |
| Pillow         | Image processing                                    |
| Docker         | Application containerization                        |
| HTML, CSS      | Frontend structure & styling                        |
| Bootstrap      | Frontend UI components                              |
| JavaScript     | Processing status polling and frontend interactions |

---

## Task Processing Example

A typical Resize operation follows this process:

```text
1. User selects an image.
2. User submits the Resize form.
3. Django validates the request.
4. An Image record is created.
5. A ProcessingJob record is created with pending status.
6. Django sends resize_image_task to Celery.
7. Celery places the task in Redis.
8. The Celery worker receives the task.
9. The job status changes to processing.
10. Pillow processes the image.
11. The processed image is saved.
12. The job status changes to completed.
13. The frontend detects the completed status.
14. The download option becomes available.
```

If an error occurs during processing:

```text
Celery Worker
      |
      v
Task Exception
      |
      v
ProcessingJob
      |
      v
status = failed
      |
      v
error_message stored
      |
      v
Frontend displays the error
```

---

## Development Considerations

This project is primarily a learning and portfolio project focused on Celery and asynchronous processing.

The architecture intentionally keeps the business logic simple so that the main focus remains on:

* Understanding Celery
* Understanding workers
* Understanding message brokers
* Understanding asynchronous execution
* Understanding task status tracking
* Understanding Docker service separation
* Understanding communication between containers

The image processing operations provide enough real work for the background tasks without introducing unnecessary domain complexity.
The main objective was not simply to build an image manipulation website, but to understand how **Celery can be integrated into a Django application and used to perform real background work**.
