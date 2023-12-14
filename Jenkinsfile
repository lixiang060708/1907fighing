pipeline {
    parameters {
        booleanParam(name: "NEW_FUNCTION_NAME",defaultValue: true, description: "")
        choice(name: "env", choices: ['dev', 'uat', 'prod'], description: "")
        string(name: "jobtest", defaultValue: "test", description: "")
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
 
        stage("credential") {
            steps {
                withCredentials([file(credentialsId: "ACK_SA", variable: "ACK"), usernamePassword(credentialsId: "ACK-1", passwordVariable: "ACK-1", usernameVariable: "ACK-1")]) {
                    sh '''
                    set +x
                    source ${ACK_SA}
                    '''
                }
            }
        }
 
        stage("allof") {
            when {
                allOf {
                    expression { env.NEW_FUNCTION_NAME_Success != "False"}
                }
            }
            steps {
                sh """
                echo "success"
                sh -ex test.sh 123.sh
                """
            }
        }
 
    }
    post {}
}
