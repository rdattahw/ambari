#!/usr/bin/env python

'''
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
from resource_management import *
from stacks.utils.RMFTestCase import *
from mock.mock import patch

class TestKnoxGateway(RMFTestCase):
  COMMON_SERVICES_PACKAGE_DIR = "KNOX/0.5.0.2.2/package"
  STACK_VERSION = "2.2"

  def test_configure_default(self):
    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/knox_gateway.py",
                       classname = "KnoxGateway",
                       command = "configure",
                       config_file="default.json",
                       hdp_stack_version = self.STACK_VERSION,
                       target = RMFTestCase.TARGET_COMMON_SERVICES
    )

    self.assertResourceCalled('Directory', '/var/lib/knox/data',
                              owner = 'knox',
                              group = 'knox',
                              recursive = True
    )
    self.assertResourceCalled('Directory', '/var/log/knox',
                              owner = 'knox',
                              group = 'knox',
                              recursive = True
    )
    self.assertResourceCalled('Directory', '/var/run/knox',
                              owner = 'knox',
                              group = 'knox',
                              recursive = True
    )
    self.assertResourceCalled('Directory', '/etc/knox/conf',
                              owner = 'knox',
                              group = 'knox',
                              recursive = True
    )

    self.assertResourceCalled('XmlConfig', 'gateway-site.xml',
                              owner = 'knox',
                              group = 'knox',
                              conf_dir = '/etc/knox/conf',
                              configurations = self.getConfig()['configurations']['gateway-site'],
                              configuration_attributes = self.getConfig()['configuration_attributes']['gateway-site']
    )

    self.assertResourceCalled('File', '/etc/knox/conf/gateway-log4j.properties',
                              mode=0644,
                              group='knox',
                              owner = 'knox',
                              content = self.getConfig()['configurations']['gateway-log4j']['content']
    )
    self.assertResourceCalled('File', '/etc/knox/conf/topologies/default.xml',
                              group='knox',
                              owner = 'knox',
                              content = InlineTemplate(self.getConfig()['configurations']['topology']['content'])
    )
    self.assertResourceCalled('Execute', ('chown',
     '-R',
     'knox:knox',
     '/var/lib/knox/data',
     '/var/log/knox',
     '/var/run/knox',
     '/etc/knox/conf'),
        sudo = True,
    )
    self.assertResourceCalled('Execute', '/usr/hdp/current/knox-server/bin/knoxcli.sh create-master --master sa',
        environment = {'JAVA_HOME': u'/usr/jdk64/jdk1.7.0_45'},
        not_if = "ambari-sudo.sh su knox -l -s /bin/bash -c '[RMF_EXPORT_PLACEHOLDER]test -f /var/lib/knox/data/security/master'",
        user = 'knox',
    )
    self.assertResourceCalled('Execute', '/usr/hdp/current/knox-server/bin/knoxcli.sh create-cert --hostname c6401.ambari.apache.org',
        environment = {'JAVA_HOME': u'/usr/jdk64/jdk1.7.0_45'},
        not_if = "ambari-sudo.sh su knox -l -s /bin/bash -c '[RMF_EXPORT_PLACEHOLDER]test -f /var/lib/knox/data/security/keystores/gateway.jks'",
        user = 'knox',
    )
    self.assertResourceCalled('File', '/etc/knox/conf/ldap-log4j.properties',
        content = '\n        # Licensed to the Apache Software Foundation (ASF) under one\n        # or more contributor license agreements.  See the NOTICE file\n        # distributed with this work for additional information\n        # regarding copyright ownership.  The ASF licenses this file\n        # to you under the Apache License, Version 2.0 (the\n        # "License"); you may not use this file except in compliance\n        # with the License.  You may obtain a copy of the License at\n        #\n        #     http://www.apache.org/licenses/LICENSE-2.0\n        #\n        # Unless required by applicable law or agreed to in writing, software\n        # distributed under the License is distributed on an "AS IS" BASIS,\n        # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\n        # See the License for the specific language governing permissions and\n        # limitations under the License.\n        #testing\n\n        app.log.dir=${launcher.dir}/../logs\n        app.log.file=${launcher.name}.log\n\n        log4j.rootLogger=ERROR, drfa\n        log4j.logger.org.apache.directory.server.ldap.LdapServer=INFO\n        log4j.logger.org.apache.directory=WARN\n\n        log4j.appender.stdout=org.apache.log4j.ConsoleAppender\n        log4j.appender.stdout.layout=org.apache.log4j.PatternLayout\n        log4j.appender.stdout.layout.ConversionPattern=%d{yy/MM/dd HH:mm:ss} %p %c{2}: %m%n\n\n        log4j.appender.drfa=org.apache.log4j.DailyRollingFileAppender\n        log4j.appender.drfa.File=${app.log.dir}/${app.log.file}\n        log4j.appender.drfa.DatePattern=.yyyy-MM-dd\n        log4j.appender.drfa.layout=org.apache.log4j.PatternLayout\n        log4j.appender.drfa.layout.ConversionPattern=%d{ISO8601} %-5p %c{2} (%F:%M(%L)) - %m%n',
        owner = 'knox',
        group = 'knox',
        mode = 0644,
    )
    self.assertResourceCalled('File', '/etc/knox/conf/users.ldif',
        content = '\n            # Licensed to the Apache Software Foundation (ASF) under one\n            # or more contributor license agreements.  See the NOTICE file\n            # distributed with this work for additional information\n            # regarding copyright ownership.  The ASF licenses this file\n            # to you under the Apache License, Version 2.0 (the\n            # "License"); you may not use this file except in compliance\n            # with the License.  You may obtain a copy of the License at\n            #\n            #     http://www.apache.org/licenses/LICENSE-2.0\n            #\n            # Unless required by applicable law or agreed to in writing, software\n            # distributed under the License is distributed on an "AS IS" BASIS,\n            # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\n            # See the License for the specific language governing permissions and\n            # limitations under the License.\n\n            version: 1\n\n            # Please replace with site specific values\n            dn: dc=hadoop,dc=apache,dc=org\n            objectclass: organization\n            objectclass: dcObject\n            o: Hadoop\n            dc: hadoop\n\n            # Entry for a sample people container\n            # Please replace with site specific values\n            dn: ou=people,dc=hadoop,dc=apache,dc=org\n            objectclass:top\n            objectclass:organizationalUnit\n            ou: people\n\n            # Entry for a sample end user\n            # Please replace with site specific values\n            dn: uid=guest,ou=people,dc=hadoop,dc=apache,dc=org\n            objectclass:top\n            objectclass:person\n            objectclass:organizationalPerson\n            objectclass:inetOrgPerson\n            cn: Guest\n            sn: User\n            uid: guest\n            userPassword:guest-password\n\n            # entry for sample user admin\n            dn: uid=admin,ou=people,dc=hadoop,dc=apache,dc=org\n            objectclass:top\n            objectclass:person\n            objectclass:organizationalPerson\n            objectclass:inetOrgPerson\n            cn: Admin\n            sn: Admin\n            uid: admin\n            userPassword:admin-password\n\n            # entry for sample user sam\n            dn: uid=sam,ou=people,dc=hadoop,dc=apache,dc=org\n            objectclass:top\n            objectclass:person\n            objectclass:organizationalPerson\n            objectclass:inetOrgPerson\n            cn: sam\n            sn: sam\n            uid: sam\n            userPassword:sam-password\n\n            # entry for sample user tom\n            dn: uid=tom,ou=people,dc=hadoop,dc=apache,dc=org\n            objectclass:top\n            objectclass:person\n            objectclass:organizationalPerson\n            objectclass:inetOrgPerson\n            cn: tom\n            sn: tom\n            uid: tom\n            userPassword:tom-password\n\n            # create FIRST Level groups branch\n            dn: ou=groups,dc=hadoop,dc=apache,dc=org\n            objectclass:top\n            objectclass:organizationalUnit\n            ou: groups\n            description: generic groups branch\n\n            # create the analyst group under groups\n            dn: cn=analyst,ou=groups,dc=hadoop,dc=apache,dc=org\n            objectclass:top\n            objectclass: groupofnames\n            cn: analyst\n            description:analyst  group\n            member: uid=sam,ou=people,dc=hadoop,dc=apache,dc=org\n            member: uid=tom,ou=people,dc=hadoop,dc=apache,dc=org\n\n\n            # create the scientist group under groups\n            dn: cn=scientist,ou=groups,dc=hadoop,dc=apache,dc=org\n            objectclass:top\n            objectclass: groupofnames\n            cn: scientist\n            description: scientist group\n            member: uid=sam,ou=people,dc=hadoop,dc=apache,dc=org',
        owner = 'knox',
        group = 'knox',
        mode = 0644,
    )
    self.assertNoMoreResources()


  @patch("resource_management.libraries.functions.security_commons.build_expectations")
  @patch("resource_management.libraries.functions.security_commons.get_params_from_filesystem")
  @patch("resource_management.libraries.functions.security_commons.validate_security_config_properties")
  @patch("resource_management.libraries.functions.security_commons.cached_kinit_executor")
  @patch("resource_management.libraries.script.Script.put_structured_out")
  def test_security_status(self, put_structured_out_mock, cached_kinit_executor_mock,
                           validate_security_config_mock, get_params_mock, build_exp_mock):
    # Test that function works when is called with correct parameters

    security_params = {
      "krb5JAASLogin":
        {
          'keytab': "/path/to/keytab",
          'principal': "principal"
        },
      "gateway-site" : {
        "gateway.hadoop.kerberos.secured" : "true"
      }
    }

    result_issues = []

    get_params_mock.return_value = security_params
    validate_security_config_mock.return_value = result_issues

    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/knox_gateway.py",
                       classname = "KnoxGateway",
                       command="security_status",
                       config_file="secured.json",
                       hdp_stack_version = self.STACK_VERSION,
                       target = RMFTestCase.TARGET_COMMON_SERVICES
    )

    self.assertTrue(build_exp_mock.call_count, 2)
    build_exp_mock.assert_called_with('gateway-site', {"gateway.hadoop.kerberos.secured": "true"}, None, None)
    put_structured_out_mock.assert_called_with({"securityState": "SECURED_KERBEROS"})
    self.assertTrue(cached_kinit_executor_mock.call_count, 1)
    cached_kinit_executor_mock.assert_called_with('/usr/bin/kinit',
                                                  self.config_dict['configurations']['knox-env']['knox_user'],
                                                  security_params['krb5JAASLogin']['keytab'],
                                                  security_params['krb5JAASLogin']['principal'],
                                                  self.config_dict['hostname'],
                                                  '/tmp')

    # Testing that the exception throw by cached_executor is caught
    cached_kinit_executor_mock.reset_mock()
    cached_kinit_executor_mock.side_effect = Exception("Invalid command")

    try:
      self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/knox_gateway.py",
                         classname = "KnoxGateway",
                         command="security_status",
                         config_file="secured.json",
                         hdp_stack_version = self.STACK_VERSION,
                         target = RMFTestCase.TARGET_COMMON_SERVICES
      )
    except:
      self.assertTrue(True)

    # Testing with a security_params which doesn't contains krb5JAASLogin
    empty_security_params = {"krb5JAASLogin" : {}}
    cached_kinit_executor_mock.reset_mock()
    get_params_mock.reset_mock()
    put_structured_out_mock.reset_mock()
    get_params_mock.return_value = empty_security_params

    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/knox_gateway.py",
                       classname = "KnoxGateway",
                       command="security_status",
                       config_file="secured.json",
                       hdp_stack_version = self.STACK_VERSION,
                       target = RMFTestCase.TARGET_COMMON_SERVICES
    )
    put_structured_out_mock.assert_called_with({"securityIssuesFound": "Keytab file and principal are not set."})

    # Testing with not empty result_issues
    result_issues_with_params = {'krb5JAASLogin': "Something bad happened"}
    validate_security_config_mock.reset_mock()
    get_params_mock.reset_mock()
    validate_security_config_mock.return_value = result_issues_with_params
    get_params_mock.return_value = security_params

    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/knox_gateway.py",
                       classname = "KnoxGateway",
                       command="security_status",
                       config_file="secured.json",
                       hdp_stack_version = self.STACK_VERSION,
                       target = RMFTestCase.TARGET_COMMON_SERVICES
    )
    put_structured_out_mock.assert_called_with({"securityState": "UNSECURED"})

    # Testing with security_enable = false
    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/knox_gateway.py",
                       classname = "KnoxGateway",
                       command="security_status",
                       config_file="default.json",
                       hdp_stack_version = self.STACK_VERSION,
                       target = RMFTestCase.TARGET_COMMON_SERVICES
    )
    put_structured_out_mock.assert_called_with({"securityState": "UNSECURED"})

  @patch("tarfile.open")
  @patch("os.path.isdir")
  def test_pre_rolling_restart(self, isdir_mock, tarfile_open_mock):
    isdir_mock.return_value = True

    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/knox_gateway.py",
                       classname = "KnoxGateway",
                       command = "pre_rolling_restart",
                       config_file="default.json",
                       hdp_stack_version = self.STACK_VERSION,
                       target = RMFTestCase.TARGET_COMMON_SERVICES)

    self.assertTrue(tarfile_open_mock.called)

    self.assertResourceCalled("Execute", "hdp-select set knox-server 2.2.1.0-2067")
