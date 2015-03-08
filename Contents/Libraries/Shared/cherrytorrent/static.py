try:
    from io import UnsupportedOperation
except ImportError:
    UnsupportedOperation = object()

import os

import cherrypy
from cherrypy._cpcompat import ntob
from cherrypy.lib import cptools, httputil, file_generator_limited

def serve_fileobj(fileobj, content_type=None, content_length=None, 
                  last_modified=None, disposition=None, name=None, debug=False):
    """Set status, headers, and body in order to serve the given file object.

    The Content-Type header will be set to the content_type arg, if provided.

    If content_length is not None, the Content-Length header will be set to
    this value. If content_length is None, its value will be computed using
    a call to os.fstat if possible.

    If last_modified is not None, the Last-Modified header will be set to
    this value. If last_modified is None, its value will be computed using
    a call to os.fstat if possible.

    If disposition is not None, the Content-Disposition header will be set
    to "<disposition>; filename=<name>". If name is None, 'filename' will
    not be set. If disposition is None, no Content-Disposition header will
    be written.

    CAUTION: If the request contains a 'Range' header, one or more seek()s will
    be performed on the file object.  This may cause undesired behavior if
    the file object is not seekable.  It could also produce undesired results
    if the caller set the read position of the file object prior to calling
    serve_fileobj(), expecting that the data would be served starting from that
    position.
    """

    response = cherrypy.serving.response

    if content_length == None or last_modified == None:
        try:
            st = os.fstat(fileobj.fileno())
        except AttributeError:
            if debug:
                cherrypy.log('os has no fstat attribute', 'TOOLS.STATIC')
        except UnsupportedOperation:
            pass
        else:
            if not content_length:
                content_length = st.st_size
            if not last_modified:
                last_modified = st.st_mtime

    if last_modified:
        # Set the Last-Modified response header, so that
        # modified-since validation code can work.
        response.headers['Last-Modified'] = httputil.HTTPDate(last_modified)
        cptools.validate_since()

    if content_type is not None:
        response.headers['Content-Type'] = content_type
    if debug:
        cherrypy.log('Content-Type: %r' % content_type, 'TOOLS.STATIC')

    cd = None
    if disposition is not None:
        if name is None:
            cd = disposition
        else:
            cd = '%s; filename="%s"' % (disposition, name)
        response.headers["Content-Disposition"] = cd
    if debug:
        cherrypy.log('Content-Disposition: %r' % cd, 'TOOLS.STATIC')

    return _serve_fileobj(fileobj, content_type, content_length, debug=debug)


def _serve_fileobj(fileobj, content_type, content_length, debug=False):
    """Internal. Set response.body to the given file object, perhaps ranged."""
    response = cherrypy.serving.response

    # HTTP/1.0 didn't have Range/Accept-Ranges headers, or the 206 code
    request = cherrypy.serving.request
    if request.protocol >= (1, 1):
        response.headers["Accept-Ranges"] = "bytes"
        r = httputil.get_ranges(request.headers.get('Range'), content_length)
        if r == []:
            response.headers['Content-Range'] = "bytes */%s" % content_length
            message = ("Invalid Range (first-byte-pos greater than "
                       "Content-Length)")
            if debug:
                cherrypy.log(message, 'TOOLS.STATIC')
            raise cherrypy.HTTPError(416, message)

        if r:
            if len(r) == 1:
                # Return a single-part response.
                start, stop = r[0]
                if stop > content_length:
                    stop = content_length
                r_len = stop - start
                if debug:
                    cherrypy.log(
                        'Single part; start: %r, stop: %r' % (start, stop),
                        'TOOLS.STATIC')
                response.status = "206 Partial Content"
                response.headers['Content-Range'] = (
                    "bytes %s-%s/%s" % (start, stop - 1, content_length))
                response.headers['Content-Length'] = r_len
                fileobj.seek(start)
                response.body = file_generator_limited(fileobj, r_len)
            else:
                # Return a multipart/byteranges response.
                response.status = "206 Partial Content"
                try:
                    # Python 3
                    from email.generator import _make_boundary as make_boundary
                except ImportError:
                    # Python 2
                    from mimetools import choose_boundary as make_boundary
                boundary = make_boundary()
                ct = "multipart/byteranges; boundary=%s" % boundary
                response.headers['Content-Type'] = ct
                if "Content-Length" in response.headers:
                    # Delete Content-Length header so finalize() recalcs it.
                    del response.headers["Content-Length"]

                def file_ranges():
                    # Apache compatibility:
                    yield ntob("\r\n")

                    for start, stop in r:
                        if debug:
                            cherrypy.log(
                                'Multipart; start: %r, stop: %r' % (
                                    start, stop),
                                'TOOLS.STATIC')
                        yield ntob("--" + boundary, 'ascii')
                        yield ntob("\r\nContent-type: %s" % content_type,
                                   'ascii')
                        yield ntob(
                            "\r\nContent-range: bytes %s-%s/%s\r\n\r\n" % (
                                start, stop - 1, content_length),
                            'ascii')
                        fileobj.seek(start)
                        gen = file_generator_limited(fileobj, stop - start)
                        for chunk in gen:
                            yield chunk
                        yield ntob("\r\n")
                    # Final boundary
                    yield ntob("--" + boundary + "--", 'ascii')

                    # Apache compatibility:
                    yield ntob("\r\n")
                response.body = file_ranges()
            return response.body
        else:
            if debug:
                cherrypy.log('No byteranges requested', 'TOOLS.STATIC')

    # Set Content-Length and use an iterable (file object)
    #   this way CP won't load the whole file in memory
    response.headers['Content-Length'] = content_length
    response.body = fileobj
    return response.body
