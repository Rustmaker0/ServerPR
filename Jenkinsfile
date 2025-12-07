pipeline {
  agent any

  environment {
    REPO_URL     = 'https://github.com/Rustmaker0/ServerPR.git'
    BRANCH       = 'main'
    GITHUB_CREDS = 'github-token'
  }

  stages {

    stage('Prep Workspace') {
      steps { cleanWs() }
    }

    stage('Checkout') {
      steps {
        checkout([$class: 'GitSCM',
          branches: [[name: "*/${BRANCH}"]],
          userRemoteConfigs: [[url: REPO_URL, credentialsId: GITHUB_CREDS]],
          extensions: [[$class: 'CloneOption', shallow: true, noTags: true, depth: 1]]
        ])
      }
    }

    stage('Build Docker image') {
      steps {
        sh '''
          echo "Building backend image..."
          DOCKER_BUILDKIT=0 docker build -t serverpr-web:latest .
        '''
      }
    }

    stage('Stop old container') {
      steps {
        sh '''
          echo "Stopping old containers..."
          docker compose -f docker-compose.yml down || true
        '''
      }
    }

    stage('Start new container') {
      steps {
        sh '''
          echo "Starting new containers..."
          docker compose -f docker-compose.yml up -d --force-recreate --build
        '''
      }
    }

    stage('Healthcheck backend') {
      steps {
        sh '''
          echo "Checking backend availability..."
          for i in $(seq 1 30); do
            code=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/api/transports/ || true)

            if [ "$code" = "200" ] || [ "$code" = "401" ] || [ "$code" = "403" ]; then
              echo "Backend UP (HTTP $code)"
              exit 0
            fi

            sleep 2
          done

          echo "Backend failed to start!"
          docker compose logs
          exit 1
        '''
      }
    }

    stage('Migrate & Collectstatic') {
      steps {
        sh '''
          echo "Running migrations..."
          docker compose exec -T app_web python manage.py migrate --noinput

          echo "Collecting static..."
          docker compose exec -T app_web python manage.py collectstatic --noinput
        '''
      }
    }
  }

  post {
    success { echo '🚀 Deploy OK — everything is running' }
    failure { echo '❌ Deploy failed' }
  }
}
