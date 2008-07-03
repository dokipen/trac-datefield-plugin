from trac.core import *
from trac.web.api import IRequestFilter, IRequestHandler
from trac.web.chrome import ITemplateProvider, add_script, add_stylesheet
from trac.ticket.api import ITicketManipulator
from trac.config import Option

import time
import traceback

datedict= {'y':'1996', 'm':'01', 'd': '01',}

class DateFieldModule(Component):
    """A module providing a JS date picker for custom fields."""
    
    date_format = Option('datefield', 'format', default='dd/mm/yy',
             doc='The format to use for dates. d - day of month (no ' +
             'leading zero), dd - day of month (two digits), m - month ' +
             '(no leading zero), mm - month (two digits), y - year (two ' +
             'digits), yy - year (four digits), D - name of day (short), DD ' +
             '- name of day (long), M - name of month (short), MM - name of ' +
             'month (long) "..." - literal text \'\' - single quote, ' +
             'anything else - literal text.')
    date_sep = Option('datefield', 'separator', default='/',
                      doc='The separator character to use for dates.')
    
    implements(IRequestFilter, IRequestHandler, ITemplateProvider, ITicketManipulator)
    
    # IRequestHandler methods
    def match_request(self, req):
        return req.path_info.startswith('/datefield')

    def process_request(self, req):
        self.log.debug("in datefield process_request")
        global datedict
        datefield = {}
        datefield['calendar'] = req.href.chrome('datefield', 'calendar.png')
        datefield['ids'] = list(self._date_fields())
        datefield['format'] = self.date_format
        return 'datefield.html', {'datefield': datefield},'text/javascript' 
    
    # IRequestFilter methods
    def pre_process_request(self, req, handler):
        return handler
            
    def post_process_request(self, req, template, data, content_type):
        if req.path_info.startswith('/newticket') or req.path_info.startswith('/ticket'):
            add_script(req, 'datefield/jquery-ui.js')
            #add_stylesheet(req, 'datefield/jquery-ui.css')

            req.chrome['scripts'].append({'href': req.href.datefield('datefield.js'), 'type': 'text/javascript'})
        return template, data, content_type
        
    # ITemplateProvider methods
    def get_htdocs_dirs(self):
        from pkg_resources import resource_filename
        return [('datefield', resource_filename(__name__, 'htdocs'))]

    def get_templates_dirs(self):
        from pkg_resources import resource_filename
        return [resource_filename(__name__, 'templates')]
        
    # ITicketManipulator methods
    def prepare_ticket(self, req, ticket, fields, actions):
        pass

    def validate_ticket(self, req, ticket): # dmy mdy ymd
        for field in self._date_fields():
            try:
                val = ticket[field].strip()
                
                if not val and self.config['ticket-custom'].getbool(field+'.date_empty', default=False):
                    continue
                if len(val.split(self.date_sep)) != 3:
                    raise Exception # Token exception to force failure
                    
                format = self.date_sep.join(['%'+c for c in self.date_format])     
                try:
                    time.strptime(val, format)
                except ValueError:
                    time.strptime(val, format.replace('y', 'Y'))
            except Exception:
                self.log.debug('DateFieldModule: Got an exception, assuming it is a validation failure.\n'+traceback.format_exc())
                yield field, 'Field %s does not seem to look like a date. The correct format is %s.' % \
                             (field, self.date_sep.join([c.upper()*(c=='y' and 4 or 2) for c in self.date_format]))
                
                
        
    # Internal methods
    def _date_fields(self):
        # XXX: Will this work when there is no ticket-custom section? <NPK>
        for key, value in self.config['ticket-custom'].options():
            if key.endswith('.date'):
                yield key.split('.', 1)[0]
    
