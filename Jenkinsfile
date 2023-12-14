pipeline {
    agent {
        any
        // node {
        //     label "any"                             // 指定节点的标签与名称
        //     // customWorkspace "${workspace}"       // 指定运行工作目录（可选）
        // }
    }
    environment {                                      // 声明环境变量
        HARBOR_CREDS = credentials('jenkins-harbor-creds')                       // 使用方式：${HARBOR_CREDS}
        K8S_CONFIG = credentials('jenkins-k8s-config')
        GIT_TAG = sh(returnStdout: true,script: 'git describe --tags --always').trim()
        // K8S_NAMESPACE：k8s中的namespace名称，执行kubectl命令会部署至此命名空间。
    }
    parameters {                                       // 流水线参数化构建参数（web UI构建选择的参数）
        booleanParam(name: "NEW_FUNCTION_NAME",defaultValue: true, description: "")    
        choice(name: "env", choices: ['dev', 'uat', 'prod'], description: "")            // // 使用方式：${params.env}
        string(name: "branch", defaultValue: "master", description: "")
    }
 
    stages {
        stage("ENV") {
            steps {
                wrap([$class: "BuildUser"]) {       // 记录当前流水线构建着用户信息
                    script {
                        env["BUILD_USER_EMAIL"] = "${env.BUILD_USER_EMAIL}"
                        env["BUILD_USER"] = "${BUILD_USER}"
                        env["BUILD_USER_ID"] = "${BUILD_USER_ID}"
 
                        echo "${BUILD_USER_ID} ${BUILD_USER} ${BUILD_USER_EMIAL}"
                    }
                }
 
                sh '''
                ### create new functions 
                NEW_FUNCTION_NAME = ${<URL>}
                echo -n ${NEW_FUNCTION_NAME} > NEW_FUNCTION_NAME.txt
                '''
                script {
                    env["NEW_FUNCTION_NAMEJobName"] = readFile('NEW_FUNCTION_NAME.txt').trim()
                }
                sh '''
                echo "NEW_FUNCTION_NAMEJobName: ${NEW_FUNCTION_NAME}" 
                '''
            }
        }
        
        stage("try") {
            steps {
                script {
                    try {
                        withCredentials([usernamePassword(credentialsId: 'id', passwordVariable: "password", usernameVariable: 'username')]) {
                        sh '''
                        echo "Username: $USERNAME"
                        echo "Password: $PASSWORD"
                        set +x
                        source ${OSS}
                        export OSS_INFO=${OSS_INFO}
                        '''
                        }
                    }catch(Exception err){
                        env.NEW_FUNCTION_NAME_Success = "False"
                        echo "error"
                    }
                }
            }
        }
 
        stage("NEW_FUNCTION_NAME") {
            when { expression {params.NEW_FUNCTION_NAME == true}}
            steps {
                script {
                    def NEW_FUNCTION_NAMEResult = build job: "${NEW_FUNCTION_NAMEJobName}", parameters: [
                        string(key: "foo", value: "${foo}")
                    ]
                    env["NEW_FUNCTION_NAME_Success"] = NEW_FUNCTION_NAMEResult.buildVariables["NEW_FUNCTION_NAME"]
                    if (NEW_FUNCTION_NAME_Success == "False") {
                        error "NEW_FUNCTION_NAME build false ${NEW_FUNCTION_NAME_Success}"
                    }
                }
            }
        }
 
        // stage("credential") {
        //     steps {
        //         withCredentials([file(credentialsId: "ACK_SA", variable: "ACK"), usernamePassword(credentialsId: "ACK-1", passwordVariable: "ACK-1", usernameVariable: "ACK-1")]) {
        //             sh '''
        //             set +x
        //             source ${ACK_SA}
        //             '''
        //         }
        //     }
        // }
 
        stage("allof") {
            when {
                allOf {  // 逻辑与,下边两个条件均满足在执行后续语句
                    expression { env.NEW_FUNCTION_NAME_Success != "False"}
                    expression { env.NEW_FUNCTION_NAME_Success != "False"}
                }
            }
            steps {
                sh """
                echo "success"
                """
            }
        }

        stage('Checkout') {
            steps {
                // 拉取指定分支的代码
                checkout([$class: 'GitSCM',
                          branches: [[name: ${params.env}]],
                          doGenerateSubmoduleConfigurations: false,
                          extensions: [],
                          submoduleCfg: [],
                          userRemoteConfigs: [[credentialsId: '<your-credentials-id>',
                                              url: 'https://github.com/your/repo.git']]])
            }
        }

        stage('Maven Build') {
            when { expression { env.GIT_TAG != null } }
            agent {
                docker {
                    image 'maven:3-jdk-8-alpine'
                    args '-v $HOME/.m2:/root/.m2'
                }
            }
            steps {
                sh 'mvn clean package -Dfile.encoding=UTF-8 -DskipTests=true'
                stash includes: 'target/*.jar', name: 'app' // 将文件暂存在服务器上
            }
        }
            
        stage('Docker Build') {
            when { 
                allOf {
                    expression { env.GIT_TAG != null }
                }
            }
            agent any
            steps {
                unstash 'app'     // 拉取服务器上暂存的maven构建的包
                sh "docker login -u ${HARBOR_CREDS_USR} -p ${HARBOR_CREDS_PSW} ${params.HARBOR_HOST}"
                sh "docker build --build-arg JAR_FILE=`ls target/*.jar |cut -d '/' -f2` -t ${params.HARBOR_HOST}/${params.DOCKER_IMAGE}:${GIT_TAG} ."    // Dockerfile添加在分支流水线下
                sh "docker push ${params.HARBOR_HOST}/${params.DOCKER_IMAGE}:${GIT_TAG}"
                sh "docker rmi ${params.HARBOR_HOST}/${params.DOCKER_IMAGE}:${GIT_TAG}"
            }
            
        }
        
        stage('Deploy') {
            when { 
                allOf {
                    expression { env.GIT_TAG != null }
                }
            }
            agent {           // Pipeline 将在该 'lwolf/helm-kubectl-docker' 镜像的环境中执行
                docker {
                    image 'lwolf/helm-kubectl-docker'
                }
            }
            steps {
                sh "mkdir -p ~/.kube"
                // 下载kube-config.yml之后，通过 base64 kube-config.yml > kube-config.txt 将文件编码，jenkins添加凭证“Secret text”，ID设置为“jenkins-k8s-config”（此处的ID必须与Jenkinsfile中的保持一致）
                sh "echo ${K8S_CONFIG} | base64 -d > ~/.kube/config" 
                // 使用k8s-deployment.tpl文件，通过sed替换变量生成k8s-deployment.yml
                sh "sed -e 's#{IMAGE_URL}#${params.HARBOR_HOST}/${params.DOCKER_IMAGE}#g;s#{IMAGE_TAG}#${GIT_TAG}#g;s#{APP_NAME}#${params.APP_NAME}#g;s#{SPRING_PROFILE}#k8s-test#g' k8s-deployment.tpl > k8s-deployment.yml"
                sh "kubectl apply -f k8s-deployment.yml --namespace=${K8S_NAMESPACE}"
            }
        }

        // stage('Deploy to Kubernetes') {
        //     steps {
        //         // 部署到 Kubernetes
        //         withKubeConfig([credentialsId: 'your-kubeconfig-cred', serverUrl: 'your-kubernetes-server-url']) {
        //             sh 'kubectl apply -f your-deployment-file.yaml'
        //         }
        //     }
        // }
        
    }
    post {
        always {                                    //总是执行脚本
            script{
                println("always")
                echo "clean up the job workspace"
                cleanWs()                           // 清楚工作空间
            }
        }
        success {                                   //成功后执行
            mail bcc: "", cc: "", body: "<b>Dear Team,<b><br>The below Jenkins job was failed<br>${BUILD_URL}",
                charset: "UTF-8", mimeType: 'text/html', to: "${email_to}", subject: "test ${BUILD_NUMBER} ${GIT_BRANCH}"
        }
    }
}
