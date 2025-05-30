#!/usr/bin/env python


__license__ = 'GPL v3'
__copyright__ = '2013, Kovid Goyal <kovid at kovidgoyal.net>'

from collections import namedtuple

from qt.core import (
    QApplication,
    QBrush,
    QCheckBox,
    QColor,
    QColorDialog,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFont,
    QFormLayout,
    QHBoxLayout,
    QIcon,
    QLabel,
    QLineEdit,
    QPalette,
    QPixmap,
    QPushButton,
    QScrollArea,
    QSize,
    QSplitter,
    Qt,
    QTextCharFormat,
    QToolButton,
    QVBoxLayout,
    QWidget,
    pyqtSignal,
)

from calibre.gui2 import error_dialog
from calibre.gui2.tweak_book import tprefs
from calibre.gui2.tweak_book.editor import syntax_text_char_format
from calibre.gui2.tweak_book.widgets import Dialog
from polyglot.builtins import iteritems

underline_styles = {'single', 'dash', 'dot', 'dash_dot', 'dash_dot_dot', 'wave', 'spell'}

_default_theme = None


def default_theme():
    global _default_theme
    if _default_theme is None:
        isdark = QApplication.instance().palette().color(QPalette.ColorRole.WindowText).lightness() > 128
        _default_theme = 'wombat-dark' if isdark else 'pyte-light'
    return _default_theme


# The solarized themes {{{
SLDX = {'base03':'1c1c1c', 'base02':'262626', 'base01':'585858', 'base00':'626262', 'base0':'808080', 'base1':'8a8a8a', 'base2':'e4e4e4', 'base3':'ffffd7', 'yellow':'af8700', 'orange':'d75f00', 'red':'d70000', 'magenta':'af005f', 'violet':'5f5faf', 'blue':'0087ff', 'cyan':'00afaf', 'green':'5f8700'}  # noqa: E501
SLD  = {'base03':'002b36', 'base02':'073642', 'base01':'586e75', 'base00':'657b83', 'base0':'839496', 'base1':'93a1a1', 'base2':'eee8d5', 'base3':'fdf6e3', 'yellow':'b58900', 'orange':'cb4b16', 'red':'dc322f', 'magenta':'d33682', 'violet':'6c71c4', 'blue':'268bd2', 'cyan':'2aa198', 'green':'859900'}  # noqa: E501
m = {f'base{n}':f'base{n:02}' for n in range(1, 4)}
m.update({f'base{n:02}':f'base{n}' for n in range(1, 4)})
SLL =  {m.get(k, k): v for k, v in iteritems(SLD)}
SLLX = {m.get(k, k): v for k, v in iteritems(SLDX)}
SOLARIZED = \
    '''
    CursorLine   bg={base02}
    CursorColumn bg={base02}
    ColorColumn  bg={base02}
    HighlightRegion bg={base00}
    MatchParen   bg={base02} fg={magenta}
    Pmenu        fg={base0} bg={base02}
    PmenuSel     fg={base01} bg={base2}

    Cursor       fg={base03} bg={base0}
    Normal       fg={base0} bg={base02}
    LineNr       fg={base01} bg={base02}
    LineNrC      fg={magenta}
    Visual       fg={base01} bg={base03}

    Comment      fg={base01} italic
    Todo         fg={magenta} bold
    String       fg={cyan}
    Constant     fg={cyan}
    Number       fg={cyan}
    PreProc      fg={orange}
    Identifier   fg={blue}
    Function     fg={blue}
    Type         fg={yellow}
    Statement    fg={green} bold
    Keyword      fg={green}
    Special      fg={red}
    SpecialCharacter bg={base03}

    Error        us=wave uc={red}
    SpellError   us=wave uc={orange}
    Tooltip      fg=black bg=ffffed
    Link         fg={blue}
    BadLink      fg={cyan} us=wave uc={red}

    DiffDelete   bg={base02} fg={red}
    DiffInsert   bg={base02} fg={green}
    DiffReplace  bg={base02} fg={blue}
    DiffReplaceReplace bg={base03}
    '''
# }}}

THEMES = {
    'wombat-dark':  # {{{
    '''
    CursorLine   bg={cursor_loc}
    CursorColumn bg={cursor_loc}
    ColorColumn  bg={cursor_loc}
    HighlightRegion bg=3d3d3d
    MatchParen   bg=444444
    Pmenu        fg=f6f3e8 bg=444444
    PmenuSel     fg=yellow bg={identifier}
    Tooltip      fg=black bg=ffffed

    Cursor       bg=656565
    Normal       fg=f6f3e8 bg=242424
    LineNr       fg=857b6f bg=000000
    LineNrC      fg=yellow
    Visual       fg=black bg=888888

    Comment      fg={comment}
    Todo         fg=8f8f8f
    String       fg={string}
    Constant     fg={constant}
    Number       fg={constant}
    PreProc      fg={constant}
    Identifier   fg={identifier}
    Function     fg={identifier}
    Type         fg={identifier}
    Statement    fg={keyword}
    Keyword      fg={keyword}
    Special      fg={special}
    Error        us=wave uc=red
    SpellError   us=wave uc=orange
    SpecialCharacter bg=666666
    Link         fg=cyan
    BadLink      fg={string} us=wave uc=red

    DiffDelete   bg=341414 fg=642424
    DiffInsert   bg=143414 fg=246424
    DiffReplace  bg=141434 fg=242464
    DiffReplaceReplace bg=002050

    '''.format(
        cursor_loc='323232',
        identifier='cae682',
        comment='99968b',
        string='95e454',
        keyword='8ac6f2',
        constant='e5786d',
        special='e7f6da'),  # }}}

    'pyte-light':  # {{{
    '''
    CursorLine   bg={cursor_loc}
    CursorColumn bg={cursor_loc}
    ColorColumn  bg={cursor_loc}
    HighlightRegion bg=E3F988
    MatchParen   bg=cfcfcf
    Pmenu        fg=white bg=808080
    PmenuSel     fg=white bg=808080
    Tooltip      fg=black bg=ffffed

    Cursor       fg=black bg=b0b4b8
    Normal       fg=404850 bg=f0f0f0
    LineNr       fg=white bg=8090a0
    LineNrC      fg=yellow
    Visual       fg=white bg=8090a0

    Comment      fg={comment} italic
    Todo         fg={comment} italic bold
    String       fg={string}
    Constant     fg={constant}
    Number       fg={constant}
    PreProc      fg={constant}
    Identifier   fg={identifier}
    Function     fg={identifier}
    Type         fg={identifier}
    Statement    fg={keyword}
    Keyword      fg={keyword}
    Special      fg={special} italic
    SpecialCharacter bg=afafaf
    Error        us=wave uc=red
    SpellError   us=wave uc=magenta
    Link         fg=blue
    BadLink      fg={string} us=wave uc=red

    DiffDelete   bg=rgb(255,180,200) fg=rgb(200,80,110)
    DiffInsert   bg=rgb(180,255,180) fg=rgb(80,210,80)
    DiffReplace  bg=rgb(206,226,250) fg=rgb(90,130,180)
    DiffReplaceReplace bg=rgb(180,210,250)

    '''.format(
        cursor_loc='F8DE7E',
        identifier='7b5694',
        comment='a0b0c0',
        string='4070a0',
        keyword='007020',
        constant='a07040',
        special='70a0d0'),  # }}}

    'solarized-x-dark': SOLARIZED.format(**SLDX),
    'solarized-dark': SOLARIZED.format(**SLD),
    'solarized-light': SOLARIZED.format(**SLL),
    'solarized-x-light': SOLARIZED.format(**SLLX),

}


def read_color(col):
    if QColor.isValidColor(col):
        return QBrush(QColor(col))
    if col.startswith('rgb('):
        r, g, b = map(int, (x.strip() for x in col[4:-1].split(',')))
        return QBrush(QColor(r, g, b))
    try:
        r, g, b = col[0:2], col[2:4], col[4:6]
        r, g, b = int(r, 16), int(g, 16), int(b, 16)
        return QBrush(QColor(r, g, b))
    except Exception:
        pass


Highlight = namedtuple('Highlight', 'fg bg bold italic underline underline_color')


def read_theme(raw):
    ans = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        bold = italic = False
        fg = bg = name = underline = underline_color = None
        line = line.partition('#')[0]
        for i, token in enumerate(line.split()):
            if i == 0:
                name = token
            else:
                if token == 'bold':
                    bold = True
                elif token == 'italic':
                    italic = True
                elif '=' in token:
                    prefix, val = token.partition('=')[0::2]
                    if prefix == 'us':
                        underline = val if val in underline_styles else None
                    elif prefix == 'uc':
                        underline_color = read_color(val)
                    elif prefix == 'fg':
                        fg = read_color(val)
                    elif prefix == 'bg':
                        bg = read_color(val)
        if name is not None:
            ans[name] = Highlight(fg, bg, bold, italic, underline, underline_color)
    return ans


THEMES = {k:read_theme(raw) for k, raw in iteritems(THEMES)}


def u(x):
    x = {'spell':'SpellCheck', 'dash_dot':'DashDot', 'dash_dot_dot':'DashDotDot'}.get(x, x.capitalize())
    if 'Dot' in x:
        return x + 'Line'
    return x + 'Underline'


underline_styles = {x:getattr(QTextCharFormat.UnderlineStyle, u(x)) for x in underline_styles}


def to_highlight(data):
    data = data.copy()
    for c in ('fg', 'bg', 'underline_color'):
        data[c] = read_color(data[c]) if data.get(c, None) is not None else None
    return Highlight(**data)


def read_custom_theme(data):
    dt = THEMES[default_theme()].copy()
    dt.update({k:to_highlight(v) for k, v in iteritems(data)})
    return dt


def get_theme(name):
    try:
        return THEMES[name]
    except KeyError:
        try:
            ans = tprefs['custom_themes'][name]
        except KeyError:
            return THEMES[default_theme()]
        else:
            return read_custom_theme(ans)


def highlight_to_char_format(h):
    ans = syntax_text_char_format()
    if h.bold:
        ans.setFontWeight(QFont.Weight.Bold)
    if h.italic:
        ans.setFontItalic(True)
    if h.fg is not None:
        ans.setForeground(h.fg)
    if h.bg is not None:
        ans.setBackground(h.bg)
    if h.underline:
        ans.setUnderlineStyle(underline_styles[h.underline])
        if h.underline_color is not None:
            ans.setUnderlineColor(h.underline_color.color())
    return ans


def theme_color(theme, name, attr):
    try:
        return getattr(theme[name], attr).color()
    except (KeyError, AttributeError):
        return getattr(THEMES[default_theme()][name], attr).color()


def theme_format(theme, name):
    try:
        h = theme[name]
    except KeyError:
        h = THEMES[default_theme()][name]
    return highlight_to_char_format(h)


def custom_theme_names():
    return tuple(tprefs['custom_themes'])


def builtin_theme_names():
    return tuple(THEMES)


def all_theme_names():
    return builtin_theme_names() + custom_theme_names()


# Custom theme creation/editing {{{

class CreateNewTheme(Dialog):

    def __init__(self, parent=None):
        Dialog.__init__(self, _('Create custom theme'), 'custom-theme-create', parent=parent)

    def setup_ui(self):
        self.l = l = QFormLayout(self)
        self.setLayout(l)

        self._name = n = QLineEdit(self)
        l.addRow(_('&Name of custom theme:'), n)

        self.base = b = QComboBox(self)
        b.addItems(sorted(builtin_theme_names()))
        l.addRow(_('&Builtin theme to base on:'), b)
        idx = b.findText(tprefs['editor_theme'] or default_theme())
        if idx == -1:
            idx = b.findText(default_theme())
        b.setCurrentIndex(idx)

        l.addRow(self.bb)

    @property
    def theme_name(self):
        return str(self._name.text()).strip()

    def accept(self):
        if not self.theme_name:
            return error_dialog(self, _('No name specified'), _(
                'You must specify a name for your theme'), show=True)
        if '*' + self.theme_name in custom_theme_names():
            return error_dialog(self, _('Name already used'), _(
                'A custom theme with the name %s already exists') % self.theme_name, show=True)
        return Dialog.accept(self)


def col_to_string(color):
    return '{:02X}{:02X}{:02X}'.format(*color.getRgb()[:3])


class ColorButton(QPushButton):

    changed = pyqtSignal()

    def __init__(self, data, name, text, parent):
        QPushButton.__init__(self, text, parent)
        self.ic = QPixmap(self.iconSize())
        color = data[name]
        self.data, self.name = data, name
        if color is not None:
            self.current_color = read_color(color).color()
            self.ic.fill(self.current_color)
        else:
            self.ic.fill(Qt.GlobalColor.transparent)
            self.current_color = color
        self.update_tooltip()
        self.setIcon(QIcon(self.ic))
        self.clicked.connect(self.choose_color)

    def clear(self):
        self.current_color = None
        self.update_tooltip()
        self.ic.fill(Qt.GlobalColor.transparent)
        self.setIcon(QIcon(self.ic))
        self.data[self.name] = self.value
        self.changed.emit()

    def choose_color(self):
        col = QColorDialog.getColor(self.current_color or Qt.GlobalColor.black, self, _('Choose color'))
        if col.isValid():
            self.current_color = col
            self.update_tooltip()
            self.ic.fill(col)
            self.setIcon(QIcon(self.ic))
            self.data[self.name] = self.value
            self.changed.emit()

    def update_tooltip(self):
        self.setToolTip(_('Red: {0} Green: {1} Blue: {2}').format(*self.current_color.getRgb()[:3]) if self.current_color else _('No color'))

    @property
    def value(self):
        if self.current_color is None:
            return None
        return col_to_string(self.current_color)


class Bool(QCheckBox):

    changed = pyqtSignal()

    def __init__(self, data, key, text, parent):
        QCheckBox.__init__(self, text, parent)
        self.data, self.key = data, key
        self.setChecked(data.get(key, False))
        self.stateChanged.connect(self._changed)

    def _changed(self, state):
        self.data[self.key] = self.value
        self.changed.emit()

    @property
    def value(self):
        return self.checkState() == Qt.CheckState.Checked


class Property(QWidget):

    changed = pyqtSignal()

    def __init__(self, name, data, parent=None):
        QWidget.__init__(self, parent)
        self.l = l = QHBoxLayout(self)
        self.setLayout(l)
        self.label = QLabel(name)
        l.addWidget(self.label)
        self.data = data

        def create_color_button(key, text):
            b = ColorButton(data, key, text, self)
            b.changed.connect(self.changed), l.addWidget(b)
            bc = QToolButton(self)
            bc.setIcon(QIcon.ic('clear_left.png'))
            bc.setToolTip(_('Remove color'))
            bc.clicked.connect(b.clear)
            h = QHBoxLayout()
            h.addWidget(b), h.addWidget(bc)
            return h

        for k, text in (('fg', _('&Foreground')), ('bg', _('&Background'))):
            h = create_color_button(k, text)
            l.addLayout(h)

        for k, text in (('bold', _('B&old')), ('italic', _('&Italic'))):
            w = Bool(data, k, text, self)
            w.changed.connect(self.changed)
            l.addWidget(w)

        self.underline = us = QComboBox(self)
        us.addItems(sorted(tuple(underline_styles) + ('',)))
        idx = us.findText(data.get('underline', '') or '')
        us.setCurrentIndex(max(idx, 0))
        us.currentIndexChanged.connect(self.us_changed)
        self.la = la = QLabel(_('&Underline:'))
        la.setBuddy(us)
        h = QHBoxLayout()
        h.addWidget(la), h.addWidget(us), l.addLayout(h)

        h = create_color_button('underline_color', _('Color'))
        l.addLayout(h)
        l.addStretch(1)

    def us_changed(self):
        self.data['underline'] = str(self.underline.currentText()) or None
        self.changed.emit()


# Help text {{{

HELP_TEXT = _('''\
<h2>Creating a custom theme</h2>

<p id="attribute" lang="und">You can create a custom syntax highlighting theme, \
with your own colors and font styles. The most important types of highlighting \
rules are described below. Note that not every rule supports every kind of \
customization, for example, changing font or underline styles for the \
<code>Cursor</code> rule does not have any effect as that rule is used only for \
the color of the blinking cursor.</p>

<p>As you make changes to your theme on the left, the changes will be reflected live in this panel.</p>

<p xml:lang="und">
{Normal}
    The most important rule. Sets the foreground and background colors for the \
    editor as well as the style of "normal" text, that is, text that does not match any special syntax.

{Visual}
    Defines the colors for text selected by the mouse.

{CursorLine}
    Defines the color for the line containing the cursor.

{LineNr}
    Defines the colors for the line numbers on the left.

{MatchParen}
    Defines the colors for matching tags in HTML and matching
    braces in CSS.

{Function}
    Used for highlighting tags in HTML

{Type}
    Used for highlighting attributes in HTML

{Statement}
    Tag names in HTML

{Constant}
    Namespace prefixes in XML and constants in CSS

{SpecialCharacter}
    Non{endash}breaking{nbsp}spaces/hyphens in HTML

{Error}
    Syntax errors such as <this <>

{SpellError}
    Misspelled words such as <span lang="en">thisword</span>

{Comment}
    Comments like <!-- this one -->

</p>

<style type="text/css">
/* Some CSS so you can see how the highlighting rules affect it */

p.someclass {{
    font-family: serif;
    font-size: 12px;
    line-height: 1.2;
}}
</style>
''')  # }}}


class ThemeEditor(Dialog):

    def __init__(self, parent=None):
        Dialog.__init__(self, _('Create/edit custom theme'), 'custom-theme-editor', parent=parent)

    def setup_ui(self):
        self.block_show = False
        self.properties = []
        self.l = l  = QVBoxLayout(self)
        self.setLayout(l)
        h = QHBoxLayout()
        l.addLayout(h)
        self.la = la = QLabel(_('&Edit theme:'))
        h.addWidget(la)
        self.theme = t = QComboBox(self)
        la.setBuddy(t)
        t.addItems(sorted(custom_theme_names()))
        t.setMinimumWidth(200)
        if t.count() > 0:
            t.setCurrentIndex(0)
        t.currentIndexChanged.connect(self.show_theme)
        h.addWidget(t)

        self.add_button = b = QPushButton(QIcon.ic('plus.png'), _('Add &new theme'), self)
        b.clicked.connect(self.create_new_theme)
        h.addWidget(b)

        self.remove_button = b = QPushButton(QIcon.ic('minus.png'), _('&Remove theme'), self)
        b.clicked.connect(self.remove_theme)
        h.addWidget(b)
        h.addStretch(1)

        self.scroll = s = QScrollArea(self)
        self.w = w = QWidget(self)
        s.setWidget(w), s.setWidgetResizable(True)
        self.cl = cl = QVBoxLayout()
        w.setLayout(cl)

        from calibre.gui2.tweak_book.editor.text import TextEdit
        self.preview = p = TextEdit(self, expected_geometry=(73, 50))
        t = {x: f'<b>{x}</b>' for x in (
            'Normal', 'Visual', 'CursorLine', 'LineNr', 'MatchParen',
            'Function', 'Type', 'Statement', 'Constant', 'SpecialCharacter',
            'Error', 'SpellError', 'Comment')
        }
        t['nbsp'] = '\xa0'
        t['endash'] = '–'
        p.load_text(HELP_TEXT.format(**t))
        p.setMaximumWidth(p.size_hint.width() + 5)
        s.setMinimumWidth(600)
        self.splitter = sp = QSplitter(self)
        l.addWidget(sp)
        sp.addWidget(s), sp.addWidget(p)

        self.bb.clear()
        self.bb.addButton(QDialogButtonBox.StandardButton.Close)
        l.addWidget(self.bb)

        if self.theme.count() > 0:
            self.show_theme()

    def update_theme(self, name):
        data = tprefs['custom_themes'][name]
        extra = set(data) - set(THEMES[default_theme()])
        missing = set(THEMES[default_theme()]) - set(data)
        for k in extra:
            data.pop(k)
        for k in missing:
            data[k] = dict(THEMES[default_theme()][k]._asdict())
            for nk, nv in iteritems(data[k]):
                if isinstance(nv, QBrush):
                    data[k][nk] = str(nv.color().name())
        if extra or missing:
            tprefs['custom_themes'][name] = data
        return data

    def show_theme(self):
        if self.block_show:
            return
        for c in self.properties:
            c.changed.disconnect()
            self.cl.removeWidget(c)
            c.setParent(None)
            c.deleteLater()
        self.properties = []
        name = str(self.theme.currentText())
        if not name:
            return
        data = self.update_theme(name)
        maxw = 0
        for k in sorted(data):
            w = Property(k, data[k], parent=self)
            w.changed.connect(self.changed)
            self.properties.append(w)
            maxw = max(maxw, w.label.sizeHint().width())
            self.cl.addWidget(w)
        for p in self.properties:
            p.label.setMinimumWidth(maxw), p.label.setMaximumWidth(maxw)
        self.preview.apply_theme(read_custom_theme(data))

    @property
    def theme_name(self):
        return str(self.theme.currentText())

    def changed(self):
        name = self.theme_name
        data = self.update_theme(name)
        self.preview.apply_theme(read_custom_theme(data))

    def create_new_theme(self):
        d = CreateNewTheme(self)
        if d.exec() == QDialog.DialogCode.Accepted:
            name = '*' + d.theme_name
            base = str(d.base.currentText())
            theme = {}
            for key, val in iteritems(THEMES[base]):
                theme[key] = {k:col_to_string(v.color()) if isinstance(v, QBrush) else v for k, v in iteritems(val._asdict())}
            tprefs['custom_themes'][name] = theme
            tprefs['custom_themes'] = tprefs['custom_themes']
            t = self.theme
            self.block_show = True
            t.clear(), t.addItems(sorted(custom_theme_names()))
            t.setCurrentIndex(t.findText(name))
            self.block_show = False
            self.show_theme()

    def remove_theme(self):
        name = self.theme_name
        if name:
            tprefs['custom_themes'].pop(name, None)
            tprefs['custom_themes'] = tprefs['custom_themes']
            t = self.theme
            self.block_show = True
            t.clear(), t.addItems(sorted(custom_theme_names()))
            if t.count() > 0:
                t.setCurrentIndex(0)
            self.block_show = False
            self.show_theme()

    def sizeHint(self):
        g = self.screen().availableSize()
        return QSize(min(1500, g.width() - 25), 650)
# }}}


if __name__ == '__main__':
    from calibre.gui2 import Application
    app = Application([])
    d = ThemeEditor()
    d.exec()
    del app
