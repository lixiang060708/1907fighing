pipeline {
    agent {
        node {
            label "any"                             // 指定节点的标签与名称
            // customWorkspace "${workspace}"          // 指定运行工作目录（可选）
        }
    }
    parameters {
        booleanParam(name: "NEW_FUNCTION_NAME",defaultValue: true, description: "")
        choice(name: "env", choices: ['dev', 'uat', 'prod'], description: "")
        string(name: "branch", defaultValue: "master", description: "")
    }
 
    stages {
        stage("ENV") {
            steps {
                wrap([$class: "BuildUser"]) {
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
                        withCredentials([usernamePassword(credentialsId: 'OSS', passwordVariable: "OSS", usernameVariable: 'OSS')]) {
                        sh '''
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
                allOf {
                    expression { env.NEW_FUNCTION_NAME_Success != "False"}
                }
            }
            steps {
                sh """
                echo "success"
                """
            }
        }
 
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
