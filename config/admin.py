from django.contrib.admin import AdminSite


class SEDAdminSite(AdminSite):
    # Text to put at the end of each page's <title>.
    site_title = 'СЕВ СЕВ 2.0'

    # Text to put in each page's <h1> (and above login form).
    site_header = 'СЕВ СЕВ 2.0'

    # Text to put at the top of the admin index page.
    index_title = 'СЕВ СЕВ 2.0'

admin_site = SEDAdminSite()