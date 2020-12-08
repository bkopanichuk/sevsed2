import declxml as xml

AckResult = xml.dictionary('AckResult', [
    xml.string('.', attribute='errorcode', ),
    xml.string('.', attribute='errortext', default="Повідомлення доставлено без помилок"),
])
Acknowledgement = xml.dictionary('AckResult', [
    xml.string('.', attribute='msg_id', default='0'),
    xml.string('.', attribute='ack_type', default='1'),
    AckResult
])

AcknowledgementXML1207Serializer = xml.dictionary('Header', [
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
    Acknowledgement,
])
