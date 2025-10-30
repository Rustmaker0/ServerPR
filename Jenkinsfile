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

    stage('Checkout (shallow, no-tags, 30m)') {
      steps {
        script {
          checkout([$class: 'GitSCM',
            branches: [[name: "*/${BRANCH}"]],
            userRemoteConfigs: [[url: REPO_URL, credentialsId: GITHUB_CREDS?.trim() ? GITHUB_CREDS : null]],
            extensions: [[$class: 'CloneOption', depth: 1, noTags: true, shallow: true, timeout: 30]]
          ])
          env.IMAGE_TAG  = sh(returnStdout: true, script: "git rev-parse --short=12 HEAD").trim()
          env.IMAGE_NAME = "${IMAGE_NAME_BASE}:${IMAGE_TAG}"
          echo "Building image: ${env.IMAGE_NAME}"
        }
      }
    }

    stage('Preflight checks') {
      steps {
        sh '''#!/bin/bash
          set -euo pipefail
          test -f Dockerfile || { echo "Dockerfile missing"; exit 1; }
          test -f requirements.txt || { echo "requirements.txt missing"; exit 1; }

 
          if git grep -nE "^(<<<<<<<|=======|>>>>>>>)" -- Dockerfile || \
             git grep -nE "^(<<<<<<<|=======|>>>>>>>)" -- Jenkinsfile 2>/dev/null || \
             git grep -nE "^(<<<<<<<|=======|>>>>>>>)" -- admin/package*.json 2>/dev/null; then
            echo "Merge conflict markers found"; exit 1
          fi

          echo "Preflight OK"
        '''
      }
    }

    stage('Build backend Docker image') {
      steps {
        sh '''
          set -e
          echo "Disk before:"; df -h || true
          docker builder prune -af || true
          DOCKER_BUILDKIT=1 docker build --pull --network=host -t "${IMAGE_NAME}" .
          docker image tag "${IMAGE_NAME}" "${IMAGE_NAME_BASE}:latest" || true
        '''
      }
    }

    stage('Stop & remove old container') {
      steps {
        sh '''
          docker ps   -q --filter name=${CONTAINER_NAME} | xargs -r docker stop
          docker ps -a -q --filter name=${CONTAINER_NAME} | xargs -r docker rm
        '''
      }
    }

    stage('Prepare env & volumes') {
      steps {
        sh '''
          set -e
          mkdir -p ${APP_PATH} ${APP_PATH}/media ${APP_PATH}/staticfiles
          [ -f ${APP_PATH}/db.sqlite3 ] || install -m 664 /dev/null ${APP_PATH}/db.sqlite3

          if [ -f .env ]; then
            install -m 600 .env ${APP_PATH}/.env
          elif [ -f .env.example ]; then
            cp .env.example ${APP_PATH}/.env
          fi
          grep -q '^DJANGO_SETTINGS_MODULE=' ${APP_PATH}/.env 2>/dev/null || \
            echo 'DJANGO_SETTINGS_MODULE=RoadData.settings_prod' >> ${APP_PATH}/.env
        '''
      }
    }

    stage('Run new container') {
      steps {
        sh '''
          set -e
          docker run -d --name ${CONTAINER_NAME} \
            --restart unless-stopped \
            --env-file ${APP_PATH}/.env \
            -p 127.0.0.1:${GUNICORN_PORT}:${GUNICORN_PORT} \
            -v ${APP_PATH}/db.sqlite3:/app/db.sqlite3 \
            -v ${APP_PATH}/media:/app/media \
            -v ${APP_PATH}/staticfiles:/app/staticfiles \
            "${IMAGE_NAME}"

          echo "Waiting backend to start..."
          for i in $(seq 1 30); do
            code=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:${GUNICORN_PORT}/api/transports/ || true)
            if [ "$code" = "200" ] || [ "$code" = "401" ] || [ "$code" = "403" ]; then
              echo "Backend up (HTTP $code)"; break
            fi
            sleep 2
            if [ $i -eq 30 ]; then echo "Backend did not start"; docker logs ${CONTAINER_NAME}; exit 1; fi
          done
        '''
      }
    }

    stage('Migrate & Collectstatic') {
      steps {
        sh '''
          set -e
          docker exec ${CONTAINER_NAME} python manage.py migrate --noinput
          docker exec ${CONTAINER_NAME} python manage.py collectstatic --noinput
        '''
      }
    }

    stage('Build frontend (admin) & publish') {
      when { expression { fileExists('admin/package.json') } }
      steps {
        sh '''
          set -e
          UID=$(id -u); GID=$(id -g)

          # Сборка фронта
          docker run --rm -u $UID:$GID \
            -e HOME=/tmp -e NPM_CONFIG_CACHE=/tmp/.npm \
            -v "$PWD/admin:/app" -w /app node:20 bash -lc '
              rm -rf node_modules \
              && ( [ -f package-lock.json ] && npm ci --prefer-offline --no-audit --fund=false || npm install ) \
              && npm run build
            '

          # Публикация строго в /opt/app/admin/dist
          docker run --rm \
            -v "$PWD/admin/dist:/src:ro" \
            -v "${APP_PATH}:/dst" \
            alpine sh -lc 'mkdir -p /dst/admin/dist && rm -rf /dst/admin/dist/* && cp -r /src/* /dst/admin/dist/'

          # Права для nginx (без sudo)
          chown -R www-data:www-data ${APP_PATH}/admin || true
          find ${APP_PATH}/admin -type d -exec chmod 755 {} \\; || true
          find ${APP_PATH}/admin -type f -exec chmod 644 {} \\; || true

          # Очистка workspace
          rm -rf admin/dist admin/node_modules || true
        '''
      }
    }

  

  post {
    success { echo '✅ Deploy OK' }
    failure { echo '❌ Deploy FAILED' }
    always  { sh 'echo "Disk after:" && df -h || true' }
  }
}
