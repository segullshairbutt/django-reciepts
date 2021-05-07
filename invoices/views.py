import functools
import ssl
import tempfile

from django.conf import settings
from django.shortcuts import render
from django.utils import timezone
from django.views.generic import View
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
from django_weasyprint import WeasyTemplateResponseMixin
from django_weasyprint.utils import django_url_fetcher
from django_weasyprint.views import CONTENT_TYPE_PNG, WeasyTemplateResponse
from django.http import HttpResponse


class IndexView(View):
    def get(self, request):
        return render(request, "invoices/invoice.html")


class CustomWeasyTemplateResponse(WeasyTemplateResponse):
    # customized response class to change the default URL fetcher
    def get_url_fetcher(self):
        # disable host and certificate check
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return functools.partial(django_url_fetcher, ssl_context=context)


class IndexPrintView(WeasyTemplateResponseMixin, IndexView):
    # output of MyModelView rendered as PDF with hardcoded CSS
    pdf_stylesheets = [
        settings.STATIC_URL + 'css/app.css',
    ]
    # show pdf in-line (default: True, show download dialog)
    pdf_attachment = False
    # custom response class to configure url-fetcher
    response_class = CustomWeasyTemplateResponse


class IndexDownloadView(WeasyTemplateResponseMixin, IndexView):
    # suggested filename (is required for attachment/download!)
    pdf_filename = 'foo.pdf'


class IndexImageView(WeasyTemplateResponseMixin, IndexView):
    # generate a PNG image instead
    content_type = CONTENT_TYPE_PNG

    # dynamically generate filename
    def get_pdf_filename(self):
        return 'foo-{at}.pdf'.format(
            at=timezone.now().strftime('%Y%m%d-%H%M'),
        )


def generate_pdf(request):
    """Generate pdf."""
    # Model data

    # Rendered
    html_string = render_to_string('invoices/invoice.html')
    html = HTML(string=html_string)
    css = CSS(string="@page {size: Letter; margin: 2.5cm;}")
    result = html.write_pdf(stylesheets=[css])

    # Creating http response
    response = HttpResponse(content_type='application/pdf;')
    response['Content-Disposition'] = 'inline; filename=temp.pdf'
    response['Content-Transfer-Encoding'] = 'binary'

    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        output = open(output.name, 'rb')
        response.write(output.read())

    return response
