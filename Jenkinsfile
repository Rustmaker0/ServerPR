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
          docker build -t serverpr-web:latest .
        '''
      }
    }

    stage('Stop old container') {
      steps {
        sh '''
          # Останавливаем старый контейнер app_web_1 если он существует
          docker compose -f docker-compose.yml down || true
        '''
      }
    }

    stage('Start new container') {
      steps {
        sh '''
          # Запускаем backend + все зависимости строго через compose
          docker compose -f docker-compose.yml up -d --force-recreate --build
        '''
      }
    }

    stage('Check backend health') {
      steps {
        sh '''
          echo "Waiting for backend..."

          for i in $(seq 1 30); do
            code=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/api/transports/ || true)

            if [ "$code" = "200" ] || [ "$code" = "401" ] || [ "$code" = "403" ]; then
              echo "Backend is UP (HTTP $code)"
              exit 0
            fi

            sleep 2
          done

          echo "Backend did not start correctly"
          docker compose logs
          exit 1
        '''
      }
    }

    stage('Migrate & Collectstatic') {
      steps {
        sh '''
          docker compose exec -T app_web python manage.py migrate --noinput
          docker compose exec -T app_web python manage.py collectstatic --noinput
        '''
      }
    }
  }

  post {
    success {
      echo '🚀 Deploy OK'
    }
    failure {
      echo '❌ Deploy failed'
    }
  }
}
