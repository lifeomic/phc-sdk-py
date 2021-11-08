#!groovy
pipeline {
  agent { label 'ecs-builder-node12' }
  options {
    ansiColor('xterm')
    timestamps()
  }

  stages {
    stage('publish') {
      when { not { branch 'master' } }
      steps {
        publishPyPIPackage('phc')
      }
    }
  }
}
