from six import StringIO
from django.utils.xmlutils import SimplerXMLGenerator
from django.conf import settings
from fastsitemaps.sitemaps import RequestSitemap

def sitemap_generator(request, maps, page, current_site):
    output = StringIO()
    xml = SimplerXMLGenerator(output, settings.DEFAULT_CHARSET)
    xml.startDocument()
    ns = {
        'xmlns':'http://www.sitemaps.org/schemas/sitemap/0.9',
        'xmlns:image':"http://www.google.com/schemas/sitemap-image/1.1",
    }
    xml.startElement('urlset', ns)
    yield output.getvalue()
    pos = output.tell()
    for site in maps:
        if callable(site):
            if issubclass(site, RequestSitemap):
                site = site(request=request)
            else:
                site = site()
        elif hasattr(site, 'request'):
            site.request = request
        for url in site.get_urls(page=page, site=current_site):
            xml.startElement('url', {})
            xml.addQuickElement('loc', url['location'])
            try:
                if url['lastmod']:
                    xml.addQuickElement('lastmod', url['lastmod'].strftime('%Y-%m-%d'))
            except (KeyError, AttributeError):
                pass
            try:
                if url['changefreq']:
                    xml.addQuickElement('changefreq', url['changefreq'])
            except KeyError:
                pass
            try:
                if url['priority']:
                    xml.addQuickElement('priority', url['priority'])
            except KeyError:
                pass

            try:
                # This will generate image links, if the item has an 'image' attribute
                img = url['item'].image
                xml.startElement('image:image', {})
                xml.addQuickElement('image:loc', request.build_absolute_uri(img.url))
                try:
                    # if it also has name and description attributes, it will add those
                    # to the image sitemaps
                    xml.addQuickElement('image:title', url['item'].name)
                    xml.addQuickElement('image:caption', url['item'].description)
                except: pass
                xml.endElement('image:image')
            except:
                pass

            xml.endElement('url')
            output.seek(pos)
            yield output.read()
            pos = output.tell()
    xml.endElement('urlset')
    xml.endDocument()
    output.seek(pos)
    last = output.read()
    output.close()
    yield last
