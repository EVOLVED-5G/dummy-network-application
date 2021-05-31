pipeline {
    agent { node {label 'evolved5g'}  }

    environment {
        AWS_DEFAULT_REGION = 'eu-central-1'
        OPENSHIFT_URL= 'https://openshift-epg.hi.inet:443'
    }

    stages {
        stage('Login openshift') {
            steps {
                withCredentials([string(credentialsId: '18e7aeb8-5552-4cbb-bf66-2402ca6772de', variable: 'TOKEN')]) {
                    dir ("${env.WORKSPACE}/iac/terraform/") {
                        sh '''
                            export KUBECONFIG="./kubeconfig"
                            oc login --insecure-skip-tls-verify --token=$TOKEN $OPENSHIFT_URL
                        '''
                        readFile('kubeconfig')
                    }
                }

            }
        }
        stage ('Deploy app in kubernetess') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: '328ab84a-aefc-41c1-aca2-1dfae5b150d2', accessKeyVariable: 'AWS_ACCESS_KEY_ID', secretKeyVariable: 'AWS_SECRET_ACCESS_KEY']]) {
                    dir ("${env.WORKSPACE}/iac/terraform/") {
                        sh '''
                            ls
                            cat kubeconfig
                            terraform init
                            terraform validate
                            terraform plan -out deployment.tfplan
                            terraform apply --auto-approve deployment.tfplan
                        '''
                    }
                }
            }
        }
        stage ('Expose service') {
            steps {
                withCredentials([string(credentialsId: '18e7aeb8-5552-4cbb-bf66-2402ca6772de', variable: 'TOKEN')]) {
                    dir ("${env.WORKSPACE}/iac/terraform/") {
                        sh '''
                            oc login --insecure-skip-tls-verify --token=$TOKEN $OPENSHIFT_URL
                            oc expose service dummy-netapp-service
                        '''
                    }
                }
            }
        }
    }
}