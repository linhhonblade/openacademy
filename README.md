# First Odoo module
Reference this [tutorial](https://www.odoo.com/documentation/13.0/howtos/backend.html#)

## Internationalization

```shell
|- idea/ # The module directory
   |- i18n/ # Translation files
      | - idea.pot # Translation Template (exported from Odoo)
      | - fr.po # French translation
      | - pt_BR.po # Brazilian Portuguese translation
      | (...)
```

# Qweb

Qweb is an XML templating engine (a software designed to combine templates with a data model to produce result documents) used by Odoo

# Working with database

changes in:

   - XML -> update module
   - Python -> restart server
   - JS,CSS -> reload webpage

