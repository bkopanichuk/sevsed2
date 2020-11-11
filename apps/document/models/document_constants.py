INCOMING = "INCOMING"
OUTGOING = 'OUTGOING'
INNER = 'INNER'
DOCUMENT_CAST = [(INCOMING, "Вхідний"), (OUTGOING, "Вихідний"), (INNER, "Внутрішній")]

############PERMISSIONS###############################################################
class CustomDocumentPermissions:
    REGISTER_DOCUMENT = 'register_document'
    CREATE_RESOLUTION = 'create_resolution'
    EXECUTE_RESOLUTION = 'execute_resolution'
    SEND_TO_ARCHIVE = 'send_to_archive'