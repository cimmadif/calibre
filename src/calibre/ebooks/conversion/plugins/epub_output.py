#!/usr/bin/env python


__license__   = 'GPL v3'
__copyright__ = '2009, Kovid Goyal <kovid@kovidgoyal.net>'
__docformat__ = 'restructuredtext en'

import os
import re
import shutil

from calibre import CurrentDir
from calibre.customize.conversion import OptionRecommendation, OutputFormatPlugin
from calibre.ptempfile import TemporaryDirectory
from polyglot.builtins import as_bytes

block_level_tags = (
    'address',
    'body',
    'blockquote',
    'center',
    'dir',
    'div',
    'dl',
    'fieldset',
    'form',
    'h1',
    'h2',
    'h3',
    'h4',
    'h5',
    'h6',
    'hr',
    'isindex',
    'menu',
    'noframes',
    'noscript',
    'ol',
    'p',
    'pre',
    'table',
    'ul',
)

dont_split_on_page_breaks = OptionRecommendation(name='dont_split_on_page_breaks',
    recommended_value=False, level=OptionRecommendation.LOW,
    help=_('Turn off splitting at page breaks. Normally, input '
            'files are automatically split at every page break into '
            'two files. This gives an output e-book that can be '
            'parsed faster and with less resources. However, '
            'splitting is slow and if your source file contains a '
            'very large number of page breaks, you should turn off '
            'splitting on page breaks.'
    )
)
extract_to = OptionRecommendation(name='extract_to',
    help=_('Extract the contents of the generated book to the '
        'specified folder. The contents of the folder are first '
        'deleted, so be careful.'))

max_image_size_help = _(
    'The maximum image size (width x height). A value of {0} means use the screen size from the output'
    ' profile. A value of {1} means no maximum size is specified. For example, a value of {2}'
    ' will cause all images to be resized so that their width is no more than {3} pixels and'
    ' their height is no more than {4} pixels. Note that this only affects the size of the actual'
    ' image files themselves. Any given image may be rendered at a different size depending on the styling'
    ' applied to it in the document.'
).format('none', 'profile', '100x200', 100, 200)


class EPUBOutput(OutputFormatPlugin):

    name = 'EPUB Output'
    author = 'Kovid Goyal'
    file_type = 'epub'
    commit_name = 'epub_output'
    ui_data = {'versions': ('2', '3')}

    options = {
        dont_split_on_page_breaks,

        extract_to,

        OptionRecommendation(name='flow_size', recommended_value=260,
            help=_('Split all HTML files larger than this size (in KB). '
                'This is necessary as most EPUB readers cannot handle large '
                'file sizes. The default of %defaultKB is the size required '
                'for Adobe Digital Editions. Set to 0 to disable size based splitting.')
        ),

        OptionRecommendation(name='no_default_epub_cover', recommended_value=False,
            help=_("Normally, if the input file has no cover and you don't"
            ' specify one, a default cover is generated with the title, '
            'authors, etc. This option disables the generation of this cover.')
        ),

        OptionRecommendation(name='no_svg_cover', recommended_value=False,
            help=_('Do not use SVG for the book cover. Use this option if '
                'your EPUB is going to be used on a device that does not '
                'support SVG, like the iPhone or the JetBook Lite. '
                'Without this option, such devices will display the cover '
                'as a blank page.')
        ),

        OptionRecommendation(name='preserve_cover_aspect_ratio',
            recommended_value=False, help=_(
            'When using an SVG cover, this option will cause the cover to scale '
            'to cover the available screen area, but still preserve its aspect ratio '
            '(ratio of width to height). That means there may be white borders '
            'at the sides or top and bottom of the image, but the image will '
            'never be distorted. Without this option the image may be slightly '
            'distorted, but there will be no borders.'
            )
        ),

        OptionRecommendation(name='epub_flatten', recommended_value=False,
            help=_('This option is needed only if you intend to use the EPUB'
                ' with FBReaderJ. It will flatten the file system inside the'
                ' EPUB, putting all files into the top level.')
        ),

        OptionRecommendation(name='epub_inline_toc', recommended_value=False,
            help=_('Insert an inline Table of Contents that will appear as part of the main book content.')
        ),

        OptionRecommendation(name='epub_toc_at_end', recommended_value=False,
            help=_('Put the inserted inline Table of Contents at the end of the book instead of the start.')
        ),

        OptionRecommendation(name='toc_title', recommended_value=None,
            help=_('Title for any generated inline table of contents.')
        ),

        OptionRecommendation(name='epub_version', recommended_value='2', choices=ui_data['versions'],
            help=_('The version of the EPUB file to generate. EPUB 2 is the'
                ' most widely compatible, only use EPUB 3 if you know you'
                ' actually need it.')
        ),

        OptionRecommendation(name='epub_max_image_size', recommended_value='none',
            help=max_image_size_help
        ),

    }

    recommendations = {('pretty_print', True, OptionRecommendation.HIGH)}

    def workaround_webkit_quirks(self):  # {{{
        from calibre.ebooks.oeb.base import XPath
        for x in self.oeb.spine:
            root = x.data
            body = XPath('//h:body')(root)
            if body:
                body = body[0]

            if not hasattr(body, 'xpath'):
                continue

            for pre in XPath('//h:pre')(body):
                if not pre.text and len(pre) == 0:
                    pre.tag = 'div'
    # }}}

    def upshift_markup(self):  # {{{
        'Upgrade markup to comply with XHTML 1.1 where possible'
        from calibre.ebooks.oeb.base import XML, XPath
        for x in self.oeb.spine:
            root = x.data
            if (not root.get(XML('lang'))) and (root.get('lang')):
                root.set(XML('lang'), root.get('lang'))
            body = XPath('//h:body')(root)
            if body:
                body = body[0]

            if not hasattr(body, 'xpath'):
                continue
            for u in XPath('//h:u')(root):
                u.tag = 'span'

            seen_ids, seen_names = set(), set()
            for x in XPath('//*[@id or @name]')(root):
                eid, name = x.get('id', None), x.get('name', None)
                if eid:
                    if eid in seen_ids:
                        del x.attrib['id']
                    else:
                        seen_ids.add(eid)
                if name:
                    if name in seen_names:
                        del x.attrib['name']
                    else:
                        seen_names.add(name)

    # }}}

    def convert(self, oeb, output_path, input_plugin, opts, log):
        self.log, self.opts, self.oeb = log, opts, oeb

        if self.opts.epub_inline_toc:
            from calibre.ebooks.mobi.writer8.toc import TOCAdder
            opts.mobi_toc_at_start = not opts.epub_toc_at_end
            opts.mobi_passthrough = False
            opts.no_inline_toc = False
            TOCAdder(oeb, opts, replace_previous_inline_toc=True, ignore_existing_toc=True)

        if self.opts.epub_flatten:
            from calibre.ebooks.oeb.transforms.filenames import FlatFilenames
            FlatFilenames()(oeb, opts)
        else:
            from calibre.ebooks.oeb.transforms.filenames import UniqueFilenames
            UniqueFilenames()(oeb, opts)

        self.oeb.set_page_progression_direction_if_needed()
        self.workaround_ade_quirks()
        self.workaround_webkit_quirks()
        self.upshift_markup()

        from calibre.ebooks.oeb.transforms.rescale import RescaleImages
        RescaleImages(check_colorspaces=True)(oeb, opts, max_size=self.opts.epub_max_image_size)

        from calibre.ebooks.oeb.transforms.split import Split
        split = Split(not self.opts.dont_split_on_page_breaks,
                max_flow_size=self.opts.flow_size*1024
                )
        split(self.oeb, self.opts)

        from calibre.ebooks.oeb.transforms.cover import CoverManager
        cm = CoverManager(
                no_default_cover=self.opts.no_default_epub_cover,
                no_svg_cover=self.opts.no_svg_cover,
                preserve_aspect_ratio=self.opts.preserve_cover_aspect_ratio)
        cm(self.oeb, self.opts, self.log)

        self.workaround_sony_quirks()

        if self.oeb.toc.count() == 0:
            self.log.warn('This EPUB file has no Table of Contents. '
                    'Creating a default TOC')
            first = next(iter(self.oeb.spine))
            self.oeb.toc.add(_('Start'), first.href)

        from calibre.ebooks.oeb.base import OPF
        identifiers = oeb.metadata['identifier']
        uuid = None
        for x in identifiers:
            if x.get(OPF('scheme'), None).lower() == 'uuid' or str(x).startswith('urn:uuid:'):
                uuid = str(x).split(':')[-1]
                break
        encrypted_fonts = getattr(input_plugin, 'encrypted_fonts', [])

        if uuid is None:
            self.log.warn('No UUID identifier found')
            from uuid import uuid4
            uuid = str(uuid4())
            oeb.metadata.add('identifier', uuid, scheme='uuid', id=uuid)

        if encrypted_fonts and not uuid.startswith('urn:uuid:'):
            # Apparently ADE requires this value to start with urn:uuid:
            # for some absurd reason, or it will throw a hissy fit and refuse
            # to use the obfuscated fonts.
            for x in identifiers:
                if str(x) == uuid:
                    x.content = 'urn:uuid:'+uuid

        with TemporaryDirectory('_epub_output') as tdir:
            from calibre.customize.ui import plugin_for_output_format
            metadata_xml = None
            extra_entries = []
            if self.is_periodical:
                if self.opts.output_profile.epub_periodical_format == 'sony':
                    from calibre.ebooks.epub.periodical import sony_metadata
                    metadata_xml, atom_xml = sony_metadata(oeb)
                    extra_entries = [('atom.xml', 'application/atom+xml', atom_xml)]
            oeb_output = plugin_for_output_format('oeb')
            oeb_output.convert(oeb, tdir, input_plugin, opts, log)
            opf = [x for x in os.listdir(tdir) if x.endswith('.opf')][0]
            self.condense_ncx([os.path.join(tdir, x) for x in os.listdir(tdir)
                    if x.endswith('.ncx')][0])
            encryption = None
            if encrypted_fonts:
                encryption = self.encrypt_fonts(encrypted_fonts, tdir, uuid)
            if self.opts.epub_version == '3':
                encryption = self.upgrade_to_epub3(tdir, opf, encryption)
            else:
                if cb := getattr(self, 'container_callback', None):
                    container, cxpath, encpath = self.create_container(tdir, opf, encryption)
                    cb(container)
                    encryption = self.end_container(cxpath, encpath)

            from calibre.ebooks.epub import initialize_container
            with initialize_container(output_path, os.path.basename(opf),
                    extra_entries=extra_entries) as epub:
                epub.add_dir(tdir)
                if encryption is not None:
                    epub.writestr('META-INF/encryption.xml', as_bytes(encryption))
                if metadata_xml is not None:
                    epub.writestr('META-INF/metadata.xml',
                            metadata_xml.encode('utf-8'))
            if opts.extract_to is not None:
                from calibre.utils.zipfile import ZipFile
                if os.path.exists(opts.extract_to):
                    if os.path.isdir(opts.extract_to):
                        shutil.rmtree(opts.extract_to)
                    else:
                        os.remove(opts.extract_to)
                os.mkdir(opts.extract_to)
                with ZipFile(output_path) as zf:
                    zf.extractall(path=opts.extract_to)
                self.log.info('Book extracted to:', opts.extract_to)

    def create_container(self, tdir, opf, encryption):
        from calibre.ebooks.epub import simple_container_xml
        try:
            os.mkdir(os.path.join(tdir, 'META-INF'))
        except OSError:
            pass
        with open(os.path.join(tdir, 'META-INF', 'container.xml'), 'wb') as f:
            f.write(simple_container_xml(os.path.basename(opf)).encode('utf-8'))
        enc_file_name = ''
        if encryption is not None:
            with open(os.path.join(tdir, 'META-INF', 'encryption.xml'), 'wb') as ef:
                ef.write(as_bytes(encryption))
            enc_file_name = ef.name
        from calibre.ebooks.oeb.polish.container import EpubContainer
        container = EpubContainer(tdir, self.log)
        return container, f.name, enc_file_name

    def end_container(self, cxpath, encpath):
        os.remove(cxpath)
        encryption = None
        if encpath:
            encryption = open(encpath, 'rb').read()
            os.remove(encpath)
        return encryption

    def upgrade_to_epub3(self, tdir, opf, encryption=None):
        self.log.info('Upgrading to EPUB 3...')
        from calibre.ebooks.oeb.polish.cover import fix_conversion_titlepage_links_in_nav
        from calibre.ebooks.oeb.polish.upgrade import epub_2_to_3
        existing_nav = getattr(self.opts, 'epub3_nav_parsed', None)
        nav_href = getattr(self.opts, 'epub3_nav_href', None)
        previous_nav = (nav_href, existing_nav) if existing_nav is not None and nav_href else None
        container, cxpath, encpath = self.create_container(tdir, opf, encryption)
        epub_2_to_3(container, self.log.info, previous_nav=previous_nav)
        fix_conversion_titlepage_links_in_nav(container)
        container.commit()
        if cb := getattr(self, 'container_callback', None):
            cb(container)
        encryption = self.end_container(cxpath, encpath)
        try:
            os.rmdir(os.path.join(tdir, 'META-INF'))
        except OSError:
            pass
        return encryption

    def encrypt_fonts(self, uris, tdir, uuid):  # {{{
        from polyglot.binary import from_hex_bytes

        key = re.sub(r'[^a-fA-F0-9]', '', uuid)
        if len(key) < 16:
            raise ValueError(f'UUID identifier {uuid!r} is invalid')
        key = bytearray(from_hex_bytes((key + key)[:32]))
        paths = []
        with CurrentDir(tdir):
            paths = [os.path.join(*x.split('/')) for x in uris]
            uris = dict(zip(uris, paths))
            fonts = []
            for uri in list(uris.keys()):
                path = uris[uri]
                if not os.path.exists(path):
                    uris.pop(uri)
                    continue
                self.log.debug('Encrypting font:', uri)
                with open(path, 'r+b') as f:
                    data = f.read(1024)
                    if len(data) >= 1024:
                        data = bytearray(data)
                        f.seek(0)
                        f.write(bytes(bytearray(data[i] ^ key[i%16] for i in range(1024))))
                    else:
                        self.log.warn('Font', path, 'is invalid, ignoring')
                if not isinstance(uri, str):
                    uri = uri.decode('utf-8')
                fonts.append('''
                <enc:EncryptedData>
                    <enc:EncryptionMethod Algorithm="http://ns.adobe.com/pdf/enc#RC"/>
                    <enc:CipherData>
                    <enc:CipherReference URI="{}"/>
                    </enc:CipherData>
                </enc:EncryptedData>
                '''.format(uri.replace('"', '\\"')))
            if fonts:
                ans = '''<encryption
                    xmlns="urn:oasis:names:tc:opendocument:xmlns:container"
                    xmlns:enc="http://www.w3.org/2001/04/xmlenc#"
                    xmlns:deenc="http://ns.adobe.com/digitaleditions/enc">
                    '''
                ans += '\n'.join(fonts)
                ans += '\n</encryption>'
                return ans
    # }}}

    def condense_ncx(self, ncx_path):  # {{{
        from lxml import etree
        if not self.opts.pretty_print:
            tree = etree.parse(ncx_path)
            for tag in tree.getroot().iter(tag=etree.Element):
                if tag.text:
                    tag.text = tag.text.strip()
                if tag.tail:
                    tag.tail = tag.tail.strip()
            compressed = etree.tostring(tree.getroot(), encoding='utf-8')
            with open(ncx_path, 'wb') as f:
                f.write(compressed)
    # }}}

    def workaround_ade_quirks(self):  # {{{
        '''
        Perform various markup transforms to get the output to render correctly
        in the quirky ADE.
        '''
        from calibre.ebooks.oeb.base import XHTML, XPath, barename, urlunquote

        stylesheet = self.oeb.manifest.main_stylesheet
        # ADE cries big wet tears when it encounters an invalid fragment
        # identifier in the NCX toc.
        frag_pat = re.compile(r'[-A-Za-z0-9_:.]+$')
        for node in self.oeb.toc.iter():
            href = getattr(node, 'href', None)
            if hasattr(href, 'partition'):
                base, _, frag = href.partition('#')
                frag = urlunquote(frag)
                if frag and frag_pat.match(frag) is None:
                    self.log.warn(
                            f'Removing fragment identifier {frag!r} from TOC as Adobe Digital Editions cannot handle it')
                    node.href = base

        for x in self.oeb.spine:
            root = x.data
            body = XPath('//h:body')(root)
            if body:
                body = body[0]

            if hasattr(body, 'xpath'):
                # remove <img> tags with empty src elements
                bad = []
                for x in XPath('//h:img')(body):
                    src = x.get('src', '').strip()
                    if src in ('', '#') or src.startswith('http:'):
                        bad.append(x)
                for img in bad:
                    img.getparent().remove(img)

                # Add id attribute to <a> tags that have name
                for x in XPath('//h:a[@name]')(body):
                    if not x.get('id', False):
                        x.set('id', x.get('name'))
                    # The delightful epubcheck has started complaining about <a> tags that
                    # have name attributes.
                    x.attrib.pop('name')

                # Replace <br> that are children of <body> as ADE doesn't handle them
                for br in XPath('./h:br')(body):
                    if br.getparent() is None:
                        continue
                    try:
                        prior = next(br.itersiblings(preceding=True))
                        priortag = barename(prior.tag)
                        priortext = prior.tail
                    except Exception:
                        priortag = 'body'
                        priortext = body.text
                    if priortext:
                        priortext = priortext.strip()
                    br.tag = XHTML('p')
                    br.text = '\u00a0'
                    style = br.get('style', '').split(';')
                    style = list(filter(None, (x.strip() for x in style)))
                    style.append('margin:0pt; border:0pt')
                    # If the prior tag is a block (including a <br> we replaced)
                    # then this <br> replacement should have a 1-line height.
                    # Otherwise it should have no height.
                    if not priortext and priortag in block_level_tags:
                        style.append('height:1em')
                    else:
                        style.append('height:0pt')
                    br.set('style', '; '.join(style))

            for tag in XPath('//h:embed')(root):
                tag.getparent().remove(tag)
            for tag in XPath('//h:object')(root):
                if tag.get('type', '').lower().strip() in {'image/svg+xml', 'application/svg+xml'}:
                    continue
                tag.getparent().remove(tag)

            for tag in XPath('//h:title|//h:style')(root):
                if not tag.text:
                    tag.getparent().remove(tag)
            for tag in XPath('//h:script')(root):
                if (not tag.text and not tag.get('src', False) and tag.get('type', None) != 'text/x-mathjax-config'):
                    tag.getparent().remove(tag)
            for tag in XPath('//h:body/descendant::h:script')(root):
                tag.getparent().remove(tag)

            formchildren = XPath('./h:input|./h:button|./h:textarea|'
                    './h:label|./h:fieldset|./h:legend')
            for tag in XPath('//h:form')(root):
                if formchildren(tag):
                    tag.getparent().remove(tag)
                else:
                    # Not a real form
                    tag.tag = XHTML('div')

            for tag in XPath('//h:center')(root):
                tag.tag = XHTML('div')
                tag.set('style', 'text-align:center')
            # ADE can't handle &amp; in an img url
            for tag in XPath('//h:img[@src]')(root):
                tag.set('src', tag.get('src', '').replace('&', ''))

            # ADE whimpers in fright when it encounters a <td> outside a
            # <table>
            in_table = XPath('ancestor::h:table')
            for tag in XPath('//h:td|//h:tr|//h:th')(root):
                if not in_table(tag):
                    tag.tag = XHTML('div')

            # ADE fails to render non breaking hyphens/soft hyphens/zero width spaces
            special_chars = re.compile(r'[\u200b\u00ad]')
            for elem in root.iterdescendants('*'):
                if elem.text:
                    elem.text = special_chars.sub('', elem.text)
                    elem.text = elem.text.replace('\u2011', '-')
                if elem.tail:
                    elem.tail = special_chars.sub('', elem.tail)
                    elem.tail = elem.tail.replace('\u2011', '-')

            if stylesheet is not None:
                # ADE doesn't render lists correctly if they have left margins
                from css_parser.css import CSSRule
                for lb in XPath('//h:ul[@class]|//h:ol[@class]')(root):
                    sel = '.'+lb.get('class')
                    for rule in stylesheet.data.cssRules.rulesOfType(CSSRule.STYLE_RULE):
                        if sel == rule.selectorList.selectorText:
                            rule.style.removeProperty('margin-left')
                            # padding-left breaks rendering in webkit and gecko
                            rule.style.removeProperty('padding-left')
                # Change whitespace:pre to pre-wrap to accommodate readers that
                # cannot scroll horizontally
                for rule in stylesheet.data.cssRules.rulesOfType(CSSRule.STYLE_RULE):
                    style = rule.style
                    ws = style.getPropertyValue('white-space')
                    if ws == 'pre':
                        style.setProperty('white-space', 'pre-wrap')

    # }}}

    def workaround_sony_quirks(self):  # {{{
        '''
        Perform toc link transforms to alleviate slow loading.
        '''
        from calibre.ebooks.oeb.base import XPath, urldefrag
        from calibre.ebooks.oeb.polish.toc import item_at_top

        def frag_is_at_top(root, frag):
            elem = XPath(f'//*[@id="{frag}" or @name="{frag}"]')(root)
            if elem:
                elem = elem[0]
            else:
                return False
            return item_at_top(elem)

        def simplify_toc_entry(toc):
            if toc.href:
                href, frag = urldefrag(toc.href)
                if frag:
                    for x in self.oeb.spine:
                        if x.href == href:
                            if frag_is_at_top(x.data, frag):
                                self.log.debug('Removing anchor from TOC href:',
                                        href+'#'+frag)
                                toc.href = href
                            break
            for x in toc:
                simplify_toc_entry(x)

        if self.oeb.toc:
            simplify_toc_entry(self.oeb.toc)

    # }}}


class KEPUBOutput(OutputFormatPlugin):

    name = 'KEPUB Output'
    author = 'Kovid Goyal'
    file_type = 'kepub'
    commit_name = 'kepub_output'

    options = {
        dont_split_on_page_breaks,
        extract_to,

        OptionRecommendation(name='flow_size', recommended_value=512,
            help=_('Split all HTML files larger than this size (in KB). '
                'This is necessary as some devices cannot handle large '
                'file sizes. Set to 0 to disable size based splitting.')
        ),

        OptionRecommendation(name='kepub_max_image_size', recommended_value='none',
            help=max_image_size_help
        ),

        OptionRecommendation(name='kepub_prefer_justification', recommended_value=False,
            help=_(
                'The KEPUB renderer on the Kobo has a bug when text justification is turned on.'
                ' It will either not justify text properly or when highlighting there will be gaps'
                ' between neighboring highlighted parts of text. By default, calibre generates'
                ' KEPUB that avoid the highlighting gaps at the expense of worse text justification.'
                ' This option reverses that tradeoff. Use this option if you use justification when'
                ' reading on your Kobo device.'
        )),

        OptionRecommendation(name='kepub_affect_hyphenation', recommended_value=False,
            help=_('Modify how hyphenation is performed for this book. Note that hyphenation'
                   ' does not perform well for all languages, as it depends on the dictionaries'
                   ' present on the device, which are not always of the highest quality.')
        ),

        OptionRecommendation(name='kepub_disable_hyphenation', recommended_value=False,
            help=_('Override all hyphenation settings in book, forcefully disabling hyphenation completely.')
        ),

        OptionRecommendation(name='kepub_hyphenation_min_chars', recommended_value=6,
            help=_('Minimum word length to hyphenate, in characters.')
        ),

        OptionRecommendation(name='kepub_hyphenation_min_chars_before', recommended_value=3,
            help=_('Minimum characters before hyphens.')
        ),

        OptionRecommendation(name='kepub_hyphenation_min_chars_after', recommended_value=3,
            help=_('Minimum characters after hyphens.')
        ),

        OptionRecommendation(name='kepub_hyphenation_limit_lines', recommended_value=2,
            help=_('Maximum consecutive hyphenated lines.')
        ),
    }

    recommendations = set(EPUBOutput.recommendations)

    def convert(self, oeb, output_path, input_plugin, opts, log):
        from calibre.customize.ui import plugin_for_output_format
        from calibre.ebooks.oeb.polish.kepubify import kepubify_container, make_options

        def kepubify(container):
            log.info('Adding Kobo markup...')
            kopts = make_options(
                affect_hyphenation=opts.kepub_affect_hyphenation,
                disable_hyphenation=opts.kepub_disable_hyphenation,
                hyphenation_min_chars=opts.kepub_hyphenation_min_chars,
                hyphenation_min_chars_before=opts.kepub_hyphenation_min_chars_before,
                hyphenation_min_chars_after=opts.kepub_hyphenation_min_chars_after,
                hyphenation_limit_lines=opts.kepub_hyphenation_limit_lines,
                prefer_justification=opts.kepub_prefer_justification,
            )
            kepubify_container(container, kopts)
            container.commit()

        epub_output = plugin_for_output_format('epub')
        dp, et, fs = opts.dont_split_on_page_breaks, opts.extract_to, opts.flow_size
        for opt in epub_output.options:
            setattr(opts, opt.option.name, opt.recommended_value)
        opts.epub_version = '3'
        opts.dont_split_on_page_breaks = dp
        opts.extract_to = et
        opts.flow_size = fs
        opts.epub_max_image_size = opts.kepub_max_image_size
        epub_output.container_callback = kepubify
        try:
            epub_output.convert(oeb, output_path, input_plugin, opts, log)
        finally:
            del epub_output.container_callback
