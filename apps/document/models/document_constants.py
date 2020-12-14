INCOMING = "INCOMING"
OUTGOING = 'OUTGOING'
INNER = 'INNER'
DOCUMENT_CAST = [(INCOMING, "Вхідний"), (OUTGOING, "Вихідний"), (INNER, "Внутрішній")]

############PERMISSIONS###############################################################
class CustomDocumentPermissions:
    REGISTER_DOCUMENT = 'register_document'
    CREATE_INNER_DOCUMENT = 'create_inner_document'
    CREATE_INCOMING_DOCUMENT = 'create_incoming_document'
    CREATE_OUTGOING_DOCUMENT = 'create_outgoing_document'
    CREATE_RESOLUTION = 'create_resolution'
    EXECUTE_RESOLUTION = 'execute_resolution'
    SEND_TO_ARCHIVE = 'send_to_archive'
    SEND_TO_OVERVIEW = 'send_to_verview'

    VIEW_ON_REGISTRATION = 'view_on_registrations'
    VIEW_REGISTERED = 'view_registered'
    VIEW_ON_RESOLUTION = 'view_on_resolution'
    VIEW_ON_EXECUTION = 'view_on_execution'
    VIEW_COMPLETED = 'view_completed'
    VIEW_ON_CONTROL = 'view_on_control'
    VIEW_PASSED_CONTROL = 'view_passed_control'
    VIEW_ARCHIVED = 'view_archived'
    VIEW_ON_AGREEMENT = 'view_on_agreement'
    VIEW_PROJECT = 'view_project'
    VIEW_REJECT = 'view_reject'
    VIEW_CONCERTED = 'view_concerted'
    VIEW_ON_SIGNING = 'view_on_singing'
    VIEW_SIGNED = 'view_signed'
    VIEW_TRANSFERRED = 'view_transfered'
    CHANGE_DOCUMENT_DICTIONARY = 'change_document_dictionary'


class CustomTaskPermissions:
    SET_CONTROLLER = 'set_controller'