import declxml as xml

RegNumber = xml.dictionary('RegNumber', [
    xml.string('.'),
    xml.string('.', attribute='regdate'),
])
OutNumber = xml.dictionary('OutNumber', [
    RegNumber
])

Name = xml.dictionary('Name', [
    xml.string('.'),
    xml.string('.', attribute='secname', required=False, omit_empty=True),
    xml.string('.', attribute='firstname', required=False, omit_empty=True),
    xml.string('.', attribute='fathersname', required=False, omit_empty=True),
])
Official = xml.dictionary('Official', [
    xml.string('.'),
    xml.string('.', attribute='department', required=False, omit_empty=True),
    xml.string('.', attribute='post', required=False, omit_empty=True),
    xml.string('.', attribute='separator', required=False, omit_empty=True),
])
OfficialPerson = xml.dictionary('OfficialPerson', [
    Name,
    Official,
])

Address = xml.dictionary('Address', [
    xml.string('.', attribute='street', required=False, omit_empty=True),
    xml.string('.', attribute='house', required=False, omit_empty=True),
    xml.string('.', attribute='building', required=False, omit_empty=True),
    xml.string('.', attribute='flat', required=False, omit_empty=True),
    xml.string('.', attribute='settlement', required=False, omit_empty=True),
    xml.string('.', attribute='district', required=False, omit_empty=True),
    xml.string('.', attribute='region', required=False, omit_empty=True),
    xml.string('.', attribute='postcode', required=False, omit_empty=True),
    xml.string('.', attribute='postbox', required=False, omit_empty=True),
    xml.string('.', attribute='nontypical', required=False, omit_empty=True),
    xml.string('.', attribute='country', required=False, omit_empty=True),
])

Organization = xml.dictionary('Organization', [
    xml.string('.', attribute='fullname', required=False, omit_empty=True),
    xml.string('.', attribute='shortname', required=False, omit_empty=True),
    xml.string('.', attribute='ownership', required=False, omit_empty=True),
    xml.string('.', attribute='ogrn'),
    xml.string('.', attribute='inn', required=False, omit_empty=True),
    Address,
])

Author = xml.dictionary('Author', [
    Organization,
    OutNumber

])

Writer = xml.dictionary('Writer', [
    Organization

])

Confident = xml.dictionary('Confident', [
    xml.string('.', attribute='flag', required=False, omit_empty=True, default='0'),
])

Addressee = xml.dictionary('Addressee', [
    xml.string('.', attribute='type', required=False, omit_empty=True, default='0'),
    Organization
])

DocTransfer = xml.dictionary('DocTransfer', [
    xml.string('.', attribute='type', ),
    xml.string('.', attribute='char_set', required=False, omit_empty=True, default='UTF-8'),
    xml.string('.', attribute='idnumber'),
    xml.string('.', attribute='description'),
    xml.string('.'),

])

Document = xml.dictionary('Document', [
    xml.string('.', attribute='idnumber'),
    xml.string('.', attribute='type'),
    xml.string('.', attribute='kind', required=False, omit_empty=True, default='Лист'),
    xml.string('.', attribute='annotation'),
    xml.string('.', attribute='collection', required=False, omit_empty=True, default='0'),
    xml.string('.', attribute='purpose_type', required=False, omit_empty=True, default='0'),
    xml.string('.', attribute='urgent', required=False, omit_empty=True, default='0'),
    RegNumber,
    Confident,
    DocTransfer,
    Author,
    Addressee,
    Writer

])

###############################

CertificateData = xml.dictionary('CertificateData', [
    xml.string('.'),
])

SignData = xml.dictionary('SignData', [
    xml.string('.'),
])

SigningTime = xml.dictionary('SigningTime', [
    xml.string('.'),
])

SignInfo = xml.dictionary('SignInfo', [
    SigningTime,
    SignData,
    xml.string('.', attribute='docTransfer_idnumber'),

])
StaticExpansion = xml.dictionary('StaticExpansion', [
    SignInfo
])

Expansion = xml.dictionary('Expansion', [
    StaticExpansion,
    xml.string('.', attribute='organization'),
    xml.string('.', attribute='exp_ver'),
])
######################################################


DocumentXML1207Serializer = xml.dictionary('Header', [
    xml.string('.', attribute='standart', required=False, omit_empty=True, default='1207'),
    xml.string('.', attribute='version', required=False, omit_empty=True, default='1.5'),
    xml.string('.', attribute='charset', required=False, omit_empty=True, default='UTF-8'),
    xml.string('.', attribute='time'),
    xml.string('.', attribute='msg_type', required=False, omit_empty=True, default='1'),
    xml.string('.', attribute='msg_id'),
    xml.string('.', attribute='msg_acknow', required=False, omit_empty=True, default='2'),
    xml.string('.', attribute='from_org_id'),
    xml.string('.', attribute='from_sys_id'),
    xml.string('.', attribute='from_organization'),
    xml.string('.', attribute='from_system'),
    xml.string('.', attribute='to_org_id'),
    xml.string('.', attribute='to_organization'),
    xml.string('.', attribute='to_sys_id'),
    xml.string('.', attribute='to_system'),
    Document,
    Expansion
])