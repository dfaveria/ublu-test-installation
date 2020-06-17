Information on deployment:
	https://www.unblu.com/en/docs/latest/#deployment-models

Information on architecture:
	https://www.unblu.com/en/docs/latest/#overview-2

1 Preparations:
==============

 kustomize:
 ----------
	In order to customise and build your deployment YAML file you need the tool kustomize, this tool can be downloaded from:
	https://github.com/kubernetes-sigs/kustomize/releases
	
 
 Database:
 ________
 - Schema:
	A database needs to be created for unblu, the name of the database will be required for configuration. config -> (unblu-customer.properties)

   Users:
		DB ADMIN: must have rights to execute the following statements: CREATE, ALTER, INSERT, UPDATE, DELETE, SELECT, DROP. config -> (database-secret.yaml)
		Runtime User: muts have rights to execute the following statements: INSERT, UPDATE, DELETE, SELECT (on unblu-specific schemas). config -> (database-secret.yaml)

  URL: the URL of database config -> (unblu-customer.properties) 
	example URL => jdbc:oracle:thin:@10.10.1.121:1521:xe 
	example URL => jdbc:mysql://192.168.1.182:3306/unblu

- make sure that from inside the cluster a connection to the database can be established, FW white listing

- Configuration:
	Unblu requires a conventional RDBMS, i.e., a SQL-based DB. The supported systems are:

		* Oracle 11.2g or later
		* Microsoft SQL Server 2012 or later
		* MySQL 5.5 or later
		* PostgreSQL 9.1.22 or later
		* MariaDB 10.1 or later

   add database configuration into 	unblu-customer.properties and database-secret.yaml
   
	database-secret.yaml: users and passwords need to be added to this file
	
	unblu-customer.properties: other configuration of database need to be added to this file
	 example: oracle
		# Database Generell Parameters
		com.unblu.storage.database.platform=org.eclipse.persistence.platform.database.OraclePlatform 
		com.unblu.storage.database.driver=oracle.jdbc.driver.OracleDriver 
		#DB URL
		# example com.unblu.storage.database.url=jdbc:oracle:thin:@10.10.1.121:1521:xe 
		com.unblu.storage.database.url=
		#schema name  
		com.unblu.storage.database.schema=unblu 
		#liquibaseSchema name, the same as schema name
		com.unblu.storage.database.liquibaseSchema=unblu
	example: mariadb
		com.unblu.storage.database.platform=org.eclipse.persistence.platform.database.MySQLPlatform<<<<<<
		com.unblu.storage.database.driver=com.mysql.jdbc.Driver
		com.unblu.storage.database.url=jdbc:mysql://192.168.1.182:3306/unblu
		com.unblu.storage.database.jdbcProperties=connectTimeout=60000,socketTimeout=60000,useUnicode=yes,characterEncoding=UTF-8,useLegacyDatetimeCode=true,serverTimezone=UTC,useSSL=false
		com.unblu.storage.database.schema=unblu
		com.unblu.storage.database.adminJdbcProperties=connectTimeout=7200000,socketTimeout=7200000,useUnicode=yes,characterEncoding=UTF-8,useLegacyDatetimeCode=true,serverTimezone=UTC,useSSL=false

	For more details on database see Unblu documentation: 
		* https://www.unblu.com/en/docs/latest/#database-2
		* https://www.unblu.com/en/docs/latest/#database-configuration
		 
 Namespace:
 ----------
 Adjust your namespace in file kustomization.yaml (namespace: example-openshift)

 Route:
 -------	
 Adjust your route inside the file route.yaml (host: unblu.example.com)

 OriginLocator:
 --------------
 Adjust the origins for staticContent and services inside the file "unblu-customer.properties" according to the route in put in route.yaml ->  (origins=staticContent=https://unblu.example.com,services=https://unblu.example.com)
 the origin needs to be same as what you defined in route.yaml (host: unblu.example.com) like https://unblu.example.com

 Environment Qualifier:
 ----------------------
 Adjust your environment qualifier inside the file "unblu-customer.properties" (com.unblu.identifier.environmentQualifier=www)


 SuperAdmin Password:
 -------------------
  Adjust the superadmin password in file "unblu-customer.properties" (superAdminPassword=superadminUqd!12$)


 Grafana Secret:
 ---------------
 Adjust granafa user credentials in file grafana-secret.yaml

 
2 Kustomize and build deployment YAML:
=====================================
Assume you are inside the directory you-20200515 

 build: ./kustomize build your-kustom > deployment.yaml

3 Deployment:
=============
	- create the namespace/project
		oc new-project example_openshift (your namespace/project defined in the file kustomization.yaml)
	
	- change to that project
		oc project example_openshift 
		
	- create the secret/credentials to access images
		oc apply -f your-kustom/gcr-secret.yaml
		
	- deploy the deployment file:
		cat deployment.yaml | oc apply -f -

4 Check deployments:
====================
You can check deployment either by using the UI (openshift console) or oc command, for example oc get pods

with command "oc get pods" you should see the unblu pods

5 How can Unblu be accessed:
===========================
Supposed the DNS is already in placed, you should be able to access Unblu via the route (defined in file route.yaml), examples
	- https://unblu.example.com/unblu/rest/product/all
		should deliver info on the product deployed, such as product.com.unblu.core_6.11.2 and etc
		
	- https://unblu.example.com/co-unblu/
		should deliver the login page for Unblu Agent Desk, you should be able to log into system by the user/password of superadmin
			username: superadmin
			password: is defined in "unblu-customer.properties"

   - if you are in this point, you should be able to upload a license too, you should have received a license in a separate file.

