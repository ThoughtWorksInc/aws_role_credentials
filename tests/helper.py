def saml_assertion(roles):
    attribute_value = '''<saml2:AttributeValue xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">
      {0}
    </saml2:AttributeValue>'''

    roles_values = [(attribute_value.format(x)) for x in roles]

    return '''<?xml version="1.0" encoding="UTF-8"?>
    <saml2p:Response xmlns:saml2p="urn:oasis:names:tc:SAML:2.0:protocol" Version="2.0" xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <saml2:Assertion xmlns:saml2="urn:oasis:names:tc:SAML:2.0:assertion" ID="id17773561036281221470153530" IssueInstant="2015-11-06T10:48:25.399Z" Version="2.0" xmlns:xs="http://www.w3.org/2001/XMLSchema">
      <saml2:AttributeStatement xmlns:saml2="urn:oasis:names:tc:SAML:2.0:assertion">
        <saml2:Attribute Name="https://aws.amazon.com/SAML/Attributes/Role" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
          {0}
        </saml2:Attribute>
      </saml2:AttributeStatement>
    </saml2:Assertion>
    </saml2p:Response>'''.format("".join(roles_values))


def read_config_file(filename):
    with open(filename, "r") as testfile:
        config = [(l.replace('\n', ''))
                  for l in testfile.readlines()]

    return config


def write_config_file(filename, *lines):
    with open(filename, 'w') as testfile:
        for line in lines:
            testfile.write("%s\n" % line)


class Struct:
    def __init__(self, entries):
        self.__dict__.update(**entries)
