# coding=utf-8

import base64, copy, json, os, random, sys, warnings
from StringIO import StringIO

from mod_python import apache, Session

OLDPATH = copy.copy(sys.path)
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../../pybcdd')))
from dealconvert import DealConverter
sys.path = OLDPATH

CACHEPATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        '../../cache'))

def _get_rand_string(length=30):
    return ('%0' + str(length) + 'x') % (random.randrange(16**length))

def _get_file_id():
    while True:
        output_id = _get_rand_string()
        output_path = os.path.join(CACHEPATH, output_id)
        if not os.path.exists(output_path):
            return output_id, output_path

def _print_response(response, obj):
    response.write(json.dumps(obj))

def handle_upload(response, request):
    if request.method != 'POST':
        response.status = apache.HTTP_METHOD_NOT_ALLOWED
        return
    try:
        params = json.load(request)
    except ValueError as e:
        response.write(str(e))
        response.status = apache.HTTP_BAD_REQUEST
        return

    session = Session.Session(response)
    if 'tokens' not in session:
        session['tokens'] = {}

    response.content_type = 'application/json'
    return_obj = {
        'name': None,
        'warnings': [],
        'error': None,
        'files': []
    }
    warnings.simplefilter('always')
    warnings.showwarning = lambda msg, *args: return_obj['warnings'].append(
        unicode(msg))

    try:
        return_obj['name'] = params['name']
        converter = DealConverter(columns=4, orientation='Portrait')
        parser = converter.detect_format(params['name'])
        input_file = StringIO(base64.b64decode(params['content']))
        dealset = parser.parse_content(input_file)
        input_file.close()
        if not len(dealset):
            raise RuntimeError('Dealset is empty')
        if params['display_deals']:
            preview_obj = []
            for board in dealset:
                deal_preview = {
                    'number': board.number,
                    'conditions': 'nesw'[board.dealer],
                    'hands': []
                }
                for pair in ['ns', 'ew']:
                    if board.vulnerable[pair.upper()]:
                        deal_preview['conditions'] += '-' + pair
                deal_preview['hands'] = board.hands
                preview_obj.append(deal_preview)
            return_obj['preview'] = preview_obj
        else:
            return_obj['preview'] = None
    except RuntimeError as e:
        return_obj['error'] = unicode(e)
        return _print_response(response, return_obj)

    for output_type in params['output']:
        output_return = {
            'name': None,
            'link': None,
            'warnings': [],
            'error': None
        }
        warnings.showwarning = lambda msg, *args: output_return['warnings'].append(
            unicode(msg))
        try:
            output_name = '.'.join(params['name'].split('.')[:-1] + [output_type])
            output_return['name'] = output_name
            output = converter.detect_format(output_name, False)
            output_id, output_path = _get_file_id()
            token = _get_rand_string(16)
            output_buffer = StringIO()
            output.analyze = params.get('analyze_deals', False)
            output.output_content(output_buffer, dealset)
            with file(output_path, 'w') as output_file:
                json.dump({
                    'token': token,
                    'name': output_name,
                    'content': base64.b64encode(output_buffer.getvalue())
                }, output_file)
                output_buffer.close()
            session['tokens'][output_id] = token
            output_return['link'] = 'download/%s' % (output_id)
        except RuntimeError as e:
            output_return['error'] = unicode(e)
        return_obj['files'].append(output_return)
    session.save()
    _print_response(response, return_obj)


def handle_download(response, request, uri_parts=[]):
    if not len(uri_parts):
        response.status = apache.HTTP_BAD_REQUEST
        return
    if request.method != 'GET':
        response.status = apache.HTTP_METHOD_NOT_ALLOWED
        return

    session = Session.Session(response)

    if 'tokens' not in session:
        response.status = apache.HTTP_NOT_FOUND
        return

    output_id = uri_parts[0]
    output_path = os.path.join(CACHEPATH, output_id)
    if not os.path.exists(output_path):
        response.status = apache.HTTP_NOT_FOUND
        return
    if output_id not in session['tokens']:
        response.status = apache.HTTP_NOT_FOUND
        return
    with file(output_path) as output_file:
        output = json.load(output_file)
        if output['token'] != session['tokens'][output_id]:
            response.status = apache.HTTP_NOT_FOUND
            return
    content = base64.b64decode(output['content'])
    response.content_type = 'application/octet-stream'
    response.headers_out.add(
        'Content-Disposition', 'attachment; filename=%s' % (output['name']))
    response.write(content)

def handler(req):
    # MIME type fix for error messages
    req.content_type = 'text/plain'

    # we need to recover original request path, from before rewrite
    orig_req = req
    while True:
        if orig_req.prev:
            orig_req = orig_req.prev
        else:
            break

    uri_parts = [part for part in orig_req.uri.split('/') if part.strip()]
    uri_parts = uri_parts[uri_parts.index('api')+1:]

    if not len(uri_parts):
        req.status = apache.HTTP_BAD_REQUEST
    else:
        try:
            if uri_parts[0] == 'upload':
                handle_upload(req, orig_req)
            elif uri_parts[0] == 'download':
                handle_download(req, orig_req, uri_parts[1:])
            else:
                req.status = apache.HTTP_BAD_REQUEST
        except Exception as e:
            req.status = apache.HTTP_INTERNAL_SERVER_ERROR
            req.write(str(e))

    return apache.OK
