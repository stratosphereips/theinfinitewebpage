import requests
import sys
import concurrent.futures

MAX_WORKERS = 200

USER_AGENTS = [
    # Common Browsers
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',  # Google Chrome
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',  # Safari
    'Mozilla/5.0 (Windows NT 10.0; rv:90.0) Gecko/20100101 Firefox/90.0',  # Firefox
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/92.0.902.55',  # Microsoft Edge

    # Mobile Browsers
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',  # iPhone Safari
    'Mozilla/5.0 (Linux; Android 11; SM-G998U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.115 Mobile Safari/537.36',  # Android Chrome

    # Bots/Crawlers
    'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',  # Googlebot
    'Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)',  # Bingbot
    'Mozilla/5.0 (compatible; Yahoo! Slurp; http://help.yahoo.com/help/us/ysearch/slurp)',  # Yahoo! Slurp

    # Other Clients
    'curl/7.68.0',  # cURL command-line tool
    'Wget/1.21.1 (linux-gnu)',  # Wget command-line tool
    'PostmanRuntime/7.28.1',    # Postman HTTP client
    'python-requests/2.25.1',   # Python requests library
    'Java/1.8.0_131',           # Java HttpUrlConnection

    # Security tools
    'Go-http-client/1.1',  # Common Go user-agent, often used in scanning tools
    'masscan/1.0 (https://github.com/robertdavidgraham/masscan)',  # Masscan scanner
    'ZmEu',  # User-agent associated with the ZmEu vulnerability scanner
    'sqlmap/1.0-dev (http://sqlmap.org)',  # sqlmap SQL injection tool
    'Nmap Scripting Engine',  # Nmap scanner
]

METHODS = [
    'GET',      # Retrieve a resource
    'POST',     # Submit data to be processed to a specified resource
    'CONNECT',  # Establish a network connection for use with a proxy
    'PUT',      # Update a current resource with new data
    'REPORT',    # Used by WebDAV; obtain information about a resource
    'PROPFIND',  # Used by WebDAV; retrieve properties of a resource
    'PROPPATCH', # Used by WebDAV; change and delete multiple properties in one atomic act
    'TRACE',    # Perform a message loop-back test along the path to the target resource
    'COPY',      # Used by WebDAV; copy a resource from one URI to another
    'ACL',       # Used by WebDAV; set access control lists
    'MKCOL',     # Used by WebDAV; create collections (like a directory)
    'VERSION-CONTROL', # Used by WebDAV; place a resource under version control
    'MOVE',      # Used by WebDAV; move a resource from one URI to another
    'UNLOCK',    # Used by WebDAV; unlock a resource
    'MERGE',     # Used by WebDAV; merge a resource
    'LINK',      # Used to establish one or more Link relationships between the existing resource identified by the effective request URI and other resources
    'PATCH',    # Apply partial modifications to a resource
    'UNLINK',    # Used to remove one or more Link relationships from the existing resource identified by the effective request URI
    ]

NOT_IMPLEMENTED_YET = [
    'HEAD',     # Same as GET but without the response body
    'OPTIONS',
    'DELETE',   # Delete a specified resource
    'SEARCH',    # Used by WebDAV; similar to GET but with additional query capabilities
    'LOCK',      # Used by WebDAV; lock a resource for exclusive use
    'CHECKOUT',  # Used by WebDAV; check out a resource for editing
    'MKACTIVITY',# Used by WebDAV; create a new activity
    'BASELINE-CONTROL',# Used by WebDAV; set options for a baseline
    'BIND',      # Used by WebDAV; bind a source resource to a destination
    'UNBIND',    # Used by WebDAV; unbind a source resource from a destination
    'M-SEARCH',  # Used by SSDP; discover, search, and present devices
    'NOTIFY',    # Used by SSDP; event notification
    'SUBSCRIBE', # Used by SSDP; subscribe to events
    'UNSUBSCRIBE', # Used by SSDP; unsubscribe from events
    'PRI',       # Priority access to the connection
]

PATHS = [
    '/favicon.ico',
    '/robots.txt',
    '/sitemap.xml',
    '/.htaccess',
    '/crossdomain.xml',
    '/security.txt',
    '/ads.txt',
    '/humans.txt',
    '/manifest.json',
    '/browserconfig.xml',
    '/apple-touch-icon.png',
    '/.well-known/',
]

def test_user_agent(user_agent):
    url = 'http://localhost:8800'
    headers = {'User-Agent': user_agent}
    response = requests.get(url, headers=headers, timeout=5)
    print(f"User-Agent: {user_agent}, Status code: {response.status_code}")

def test_method(method):
    url = 'http://localhost:8800'
    response = requests.request(method, url, timeout=5)
    print(f"Method: {method}, Status code: {response.status_code}")

def test_path(path):
    url = 'http://localhost:8800' + path
    response = requests.get(url, timeout=5)
    print(f"URL: {url}, Status code: {response.status_code}")

def run_tests():
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # Test user agents
            # executor.map(test_user_agent, USER_AGENTS)
            # Test methods
            executor.map(test_method, METHODS)
            # Test methods not implemented
            # executor.map(test_method, NOT_IMPLEMENTED_YET)
            # Test paths
            #executor.map(test_path, PATHS)
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as err:
        logger.info(f'Exception in run_tests: {err}')


if __name__ == '__main__':
    run_tests()
