pipeline {
  agent any

  options {
    timestamps()
    disableConcurrentBuilds()
    timeout(time: 40, unit: 'MINUTES')
  }

  environment {
    REPO_URL       = 'https://github.com/Rustmaker0/ServerPR.git'
    BRANCH         = 'main'
    GITHUB_CREDS   = 'github-token'

    IMAGE_NAME_BASE = 'serverpr-web'
    IMAGE_TAG       = 'latest'
    IMAGE_NAME      = "${IMAGE_NAME_BASE}:${IMAGE_TAG}"
    CONTAINER_NAME  = 'serverpr-web'
    APP_PATH        = '/opt/app'
    GUNICORN_PORT   = '8000'
  }

  stages {

    stage('Prep workspace') {
      steps { cleanWs() }
    }

   stage('Checkout (clean)') {
  steps {
    deleteDir()  // Полное удаление workspace
    checkout([$class: 'GitSCM',
      branches: [[name: "*/${BRANCH}"]],
      userRemoteConfigs: [[url: REPO_URL, credentialsId: GITHUB_CREDS]],
      extensions: [
        [$class: 'WipeWorkspace'], // Полная очистка
        [$class: 'CloneOption', depth: 1, noTags: false, shallow: true]
      ]
    ])
  }
}

    stage('Build Docker image') {
      steps {
        sh '''
          echo "Building backend image..."

          # ВАЖНО: BuildKit выключен
          DOCKER_BUILDKIT=0 docker build --no-cache -t ${IMAGE_NAME} .
        '''
      }
    }

    stage('Stop & remove old container') {
      steps {
        sh '''
          docker stop ${CONTAINER_NAME} || true
          docker rm   ${CONTAINER_NAME} || true
        '''
      }
    }

    stage('Prepare environment & volumes') {
      steps {
        sh '''
          mkdir -p ${APP_PATH} ${APP_PATH}/media ${APP_PATH}/staticfiles

          [ -f ${APP_PATH}/db.sqlite3 ] || touch ${APP_PATH}/db.sqlite3

          if [ ! -f ${APP_PATH}/.env ]; then
            cp .env.example ${APP_PATH}/.env
          fi
        '''
      }
    }

    stage('Run new container') {
      steps {
        sh '''
          docker run -d --name ${CONTAINER_NAME} \
            --restart unless-stopped \
            --env-file ${APP_PATH}/.env \
            -p 127.0.0.1:${GUNICORN_PORT}:${GUNICORN_PORT} \
            -v ${APP_PATH}/db.sqlite3:/app/db.sqlite3 \
            -v ${APP_PATH}/media:/app/media \
            -v ${APP_PATH}/staticfiles:/app/staticfiles \
            serverpr-web:latest

          echo "Waiting for container health..."

for i in $(seq 1 30); do
  status=$(docker inspect --format='{{.State.Health.Status}}' ${CONTAINER_NAME} || echo "starting")

  echo "Status: $status"

  if [ "$status" = "healthy" ]; then
    echo "Backend is HEALTHY"
    exit 0
  fi

  sleep 2
done

echo "Backend failed to start!"
docker logs ${CONTAINER_NAME}
exit 1

        '''
      }
    }

    stage('Migrate & Collectstatic') {
      steps {
        sh '''
          docker exec ${CONTAINER_NAME} python manage.py migrate --noinput
          docker exec ${CONTAINER_NAME} python manage.py collectstatic --noinput
        '''
      }
    }
  }

  post {
    success { echo '🚀 Deploy OK' }
    failure { echo '❌ Deploy FAILED' }
  }
}
