#!/usr/bin/env python
import pygtk
import gtk
import webkit
import urllib
import urlparse

FB_TOKEN_FILE = 'access_token.txt'

class Browser:
    """ Creates a web browser using GTK+ and WebKit to authorize a
        desktop application in Facebook. It uses OAuth 2.0.
        Requires the Facebook's Application ID. The token is then
        saved to FB_TOKEN_FILE.
    """

    def __init__(self, app_key, scope='offline_access'):
        """ Constructor. Creates the GTK+ app and adds the WebKit widget
            @param app_key Application key ID (Public).

            @param scope A string list of permissions to ask for. More at
            http://developers.facebook.com/docs/reference/api/permissions/
        """
        self.token = ''
        self.token_expire = ''
        self.scope = scope
        # Creates the GTK+ app
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.scrolled_window = gtk.ScrolledWindow()
        # Creates a WebKit view
        self.web_view = webkit.WebView()
        self.scrolled_window.add(self.web_view)
        self.window.add(self.scrolled_window)
        # Connects events
        self.window.connect('destroy', self._destroy_event_cb) # Close window
        self.web_view.connect('load-committed', self._load_committed_cb) # Load page
        self.window.set_default_size(1024, 800)
        # Loads the Facebook OAuth page
        self.web_view.load_uri(
            'https://www.facebook.com/dialog/oauth?client_id=%s&redirect_uri=%s&response_type=token&scope=%s' % (urllib.quote(app_key), urllib.quote('https://www.facebook.com/connect/login_success.html'), urllib.quote(self.scope))
            )

    def _load_committed_cb(self, web_view, frame):
        """ Callback. The page is about to be loaded. This event is captured
            to intercept the OAuth 2.0 redirection, which includes the
            access token.

            @param web_view A reference to the current WebKitWebView.

            @param frame A reference to the main WebKitWebFrame.
        """
        # Gets the current URL to check whether is the one of the redirection
        uri = frame.get_uri()
        parse = urlparse.urlparse(uri)
        if (hasattr(parse, 'netloc') and hasattr(parse, 'path') and
            hasattr(parse, 'fragment') and parse.netloc == 'www.facebook.com' and
            parse.path == '/connect/login_success.html' and parse.fragment):
            # Get token from URL
            params = urlparse.parse_qs(parse.fragment)
            self.token = params['access_token'][0]
            self.token_expire = params['expires_in'][0] # Should be equal to 0, don't expire
            # Save token to file
            token_file = open(FB_TOKEN_FILE, 'w')
            token_file.write(self.token)
            token_file.close()
            print "Authentication done. Access token available at %s" % (FB_TOKEN_FILE)
            gtk.main_quit() # Finish

    def _destroy_event_cb(self, widget):
        """ Callback for close window. Closes the application. """
        return gtk.main_quit()

    def authorize(self):
        """ Runs the app. """
        self.window.show_all()
        gtk.main()

if (__name__ == '__main__'):
    # Creates the browser
    browser = Browser(app_key='XXXXXXXXXXX', scope='offline_access,read_stream')
    # Launch browser window
    browser.authorize()
    # Token available?
    print "Token: %s" % (browser.token)
