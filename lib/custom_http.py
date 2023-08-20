def generate_html():
    doctype = "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\"><html><head><title>This is a TL;DR page.</title></head><body>"
    content = "What you are looking for is in the next line<br>" * 100
    return doctype + content
