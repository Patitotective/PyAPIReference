#!/usr/bin/python
# -*- coding: utf-8 -*-

# MarkdownHighlighter is a simple syntax highlighter for Markdown syntax.
# The initial code for MarkdownHighlighter was taken from niwmarkdowneditor by John Schember
# Copyright 2009 John Schember, Copyright 2012 Rupesh Kumar

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

'''
Highlight Markdown text
'''

import sys
import re
from PyQt5.QtGui import QBrush, QSyntaxHighlighter, QTextCharFormat, QColor, QPalette, QFont, QTextCursor, QTextLayout
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTextEdit, QMainWindow, QApplication

class MarkdownHighlighter(QSyntaxHighlighter):

    MARKDOWN_KEYS_REGEX = {
        'Bold' : re.compile(u'(?P<delim>\*\*)(?P<text>.+)(?P=delim)'), # **Bold**
       
        'uBold': re.compile(u'(?P<delim>__)(?P<text>[^_]{2,})(?P=delim)'), # __uBold__
       
        'Italic': re.compile(u'(?P<delim>\*)(?P<text>[^*]{2,})(?P=delim)'), # *Italic*
       
        'uItalic': re.compile(u'(?P<delim>_)(?P<text>[^_]+)(?P=delim)'), # _uItalic_
       
        'Link': re.compile(u'(?u)\[.*?\]\(.*\)'), #u'(?u)(^|(?P<pre>[^!]))\[.*?\]:?[ \t]*\(?[^)]+\)?'), # [Link alt text](Link)
       
        'Image': re.compile(u'(?u)!\[.*?\]\(.+?\)'), # ![Image alt text](Image)
       
        'HeaderAtx': re.compile(u'(?u)^\#{1,6}(.*?)\#*(\n|$)'), # ## Header
       
        'Header': re.compile(u'^(.+)[ \t]*\n(=+|-+)[ \t]*\n+'), # Header level 1\n=============== or Header level 2\n---------------
       
        'CodeBlock': re.compile(u'(?P<delim>\`\`\`\n)(?P<text>.+)(?P=delim)'), # ```This is a\nmultiline\ncode block```
       
        'CodeBlockTab': re.compile(u'^([ ]{4,}|\t).*'), #\tThis is also a\n\tmultiline code block using\n\ttabs
       
        'UnorderedList': re.compile(u'(?u)^\s*(\* |\+ |- )+\s*'), # - Element 1\n+ Element 2
       
        'UnorderedListStar': re.compile(u'^\s*(\* )+\s*'), # * Element 2
       
        'OrderedList': re.compile(u'(?u)^\s*(\d+\. )\s*'), # 1. First element\n2. Second element
       
        'BlockQuote': re.compile(u'(?u)^\s*>+\s*'), # > This is a quote
       
        'BlockQuoteCount': re.compile(u'^[ \t]*>[ \t]?'), # 
       
        'CodeSpan': re.compile(u'(?P<delim>`+).+?(?P=delim)'), # `This is a inline code block`
       
        'HR': re.compile(u'(?u)^(\s*(\*|-)\s*){3,}$'), # 
       
        'eHR': re.compile(u'(?u)^(\s*(\*|=)\s*){3,}$'), # 
       
        'Html': re.compile(u'<.+?>') # This is an html tag
    }

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        parent.setTabStopWidth(parent.fontMetrics().width(' ') * 6)

        self.defaultTheme =  {
            "background-color":"#3e3d32", 
            "color":"#ffffff", 
            "bold": {
                "color":"#ffffff", 
                "font-weight":"bold", 
                "font-style":"normal"
            }, 
            "emphasis": {
                "color":"#ffffff", 
                "font-weight":"normal", 
                "font-style":"italic"
            }, 
            "link": {
                "color":"#66d9ef", 
                "font-weight":"normal", 
                "font-style":"normal"
            }, 
            "image": {
                "color":"#cb4b16", 
                "font-weight":"normal", 
                "font-style":"normal"
            }, 
            "header": {
                "color":"#fd971f", 
                "font-weight":"bold", 
                "font-style":"normal"
            }, 
            "unorderedlist": {
                "color":"#fd971f", 
                "font-weight":"normal", 
                "font-style":"normal"
            }, 
            "orderedlist": {
                "color":"#ae81ff", 
                "font-weight":"normal", 
                "font-style":"normal"
            }, 
            "blockquote": {
                "color":"#dc322f", 
                "font-weight":"normal", 
                "font-style":"normal"
            }, 
            "codespan": {
                "color":"#dc322f", 
                "font-weight":"normal", 
                "font-style":"normal"
            }, 
            "codeblock": {
                "color":"#cfcfc2", 
                "font-weight":"normal", 
                "font-style":"normal", 
                #"background-color": "#3b3c37", 
            }, 
            "line": {
                "color":"#fd971f", 
                "font-weight":"bold", 
                "font-style":"normal"
            }, 
            "html": {
                "color":"#f92672", 
                "font-weight":"normal", 
                "font-style":"normal"
            }
        }
        
        self.setTheme(self.defaultTheme)

    def setTheme(self, theme):
        self.theme = theme
        self.MARKDOWN_KWS_FORMAT = {}

        pal = self.parent.palette()
        pal.setColor(QPalette.Base, QColor(theme['background-color']))
        self.parent.setPalette(pal)
        self.parent.setTextColor(QColor(theme['color']))

        text_char_format = QTextCharFormat()
        text_char_format.setForeground(QBrush(QColor(theme['bold']['color'])))
        text_char_format.setFontWeight(QFont.Bold if theme['bold']['font-weight']=='bold' else QFont.Normal)
        text_char_format.setFontItalic(True if theme['bold']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['Bold'] = text_char_format

        text_char_format = QTextCharFormat()
        text_char_format.setForeground(QBrush(QColor(theme['bold']['color'])))
        text_char_format.setFontWeight(QFont.Bold if theme['bold']['font-weight']=='bold' else QFont.Normal)
        text_char_format.setFontItalic(True if theme['bold']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['uBold'] = text_char_format

        text_char_format = QTextCharFormat()
        text_char_format.setForeground(QBrush(QColor(theme['emphasis']['color'])))
        text_char_format.setFontWeight(QFont.Bold if theme['emphasis']['font-weight']=='bold' else QFont.Normal)
        text_char_format.setFontItalic(True if theme['emphasis']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['Italic'] = text_char_format

        text_char_format = QTextCharFormat()
        text_char_format.setForeground(QBrush(QColor(theme['emphasis']['color'])))
        text_char_format.setFontWeight(QFont.Bold if theme['emphasis']['font-weight']=='bold' else QFont.Normal)
        text_char_format.setFontItalic(True if theme['emphasis']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['uItalic'] = text_char_format

        text_char_format = QTextCharFormat()
        text_char_format.setForeground(QBrush(QColor(theme['link']['color'])))
        text_char_format.setFontWeight(QFont.Bold if theme['link']['font-weight']=='bold' else QFont.Normal)
        text_char_format.setFontItalic(True if theme['link']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['Link'] = text_char_format

        text_char_format = QTextCharFormat()
        text_char_format.setForeground(QBrush(QColor(theme['image']['color'])))
        text_char_format.setFontWeight(QFont.Bold if theme['image']['font-weight']=='bold' else QFont.Normal)
        text_char_format.setFontItalic(True if theme['image']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['Image'] = text_char_format

        text_char_format = QTextCharFormat()
        text_char_format.setForeground(QBrush(QColor(theme['header']['color'])))
        text_char_format.setFontWeight(QFont.Bold if theme['header']['font-weight']=='bold' else QFont.Normal)
        text_char_format.setFontItalic(True if theme['header']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['Header'] = text_char_format

        text_char_format = QTextCharFormat()
        text_char_format.setForeground(QBrush(QColor(theme['header']['color'])))
        text_char_format.setFontWeight(QFont.Bold if theme['header']['font-weight']=='bold' else QFont.Normal)
        text_char_format.setFontItalic(True if theme['header']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['HeaderAtx'] = text_char_format

        text_char_format = QTextCharFormat()
        text_char_format.setForeground(QBrush(QColor(theme['unorderedlist']['color'])))
        text_char_format.setFontWeight(QFont.Bold if theme['unorderedlist']['font-weight']=='bold' else QFont.Normal)
        text_char_format.setFontItalic(True if theme['unorderedlist']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['UnorderedList'] = text_char_format

        text_char_format = QTextCharFormat()
        text_char_format.setForeground(QBrush(QColor(theme['orderedlist']['color'])))
        text_char_format.setFontWeight(QFont.Bold if theme['orderedlist']['font-weight']=='bold' else QFont.Normal)
        text_char_format.setFontItalic(True if theme['orderedlist']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['OrderedList'] = text_char_format

        text_char_format = QTextCharFormat()
        text_char_format.setForeground(QBrush(QColor(theme['blockquote']['color'])))
        text_char_format.setFontWeight(QFont.Bold if theme['blockquote']['font-weight']=='bold' else QFont.Normal)
        text_char_format.setFontItalic(True if theme['blockquote']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['BlockQuote'] = text_char_format

        text_char_format = QTextCharFormat()
        text_char_format.setForeground(QBrush(QColor(theme['codespan']['color'])))
        text_char_format.setFontWeight(QFont.Bold if theme['codespan']['font-weight']=='bold' else QFont.Normal)
        text_char_format.setFontItalic(True if theme['codespan']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['CodeSpan'] = text_char_format

        text_char_format = QTextCharFormat()
        text_char_format.setForeground(QBrush(QColor(theme['codeblock']['color'])))
        text_char_format.setFontWeight(QFont.Bold if theme['codeblock']['font-weight']=='bold' else QFont.Normal)
        text_char_format.setFontItalic(True if theme['codeblock']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['CodeBlockTab'] = text_char_format

        text_char_format = QTextCharFormat()
        text_char_format.setForeground(QBrush(QColor(theme['codeblock']['color'])))
        text_char_format.setFontWeight(QFont.Bold if theme['codeblock']['font-weight']=='bold' else QFont.Normal)
        text_char_format.setFontItalic(True if theme['codeblock']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['CodeBlock'] = text_char_format

        text_char_format = QTextCharFormat()
        text_char_format.setForeground(QBrush(QColor(theme['line']['color'])))
        text_char_format.setFontWeight(QFont.Bold if theme['line']['font-weight']=='bold' else QFont.Normal)
        text_char_format.setFontItalic(True if theme['line']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['HR'] = text_char_format

        text_char_format = QTextCharFormat()
        text_char_format.setForeground(QBrush(QColor(theme['line']['color'])))
        text_char_format.setFontWeight(QFont.Bold if theme['line']['font-weight']=='bold' else QFont.Normal)
        text_char_format.setFontItalic(True if theme['line']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['eHR'] = text_char_format

        text_char_format = QTextCharFormat()
        text_char_format.setForeground(QBrush(QColor(theme['html']['color'])))
        text_char_format.setFontWeight(QFont.Bold if theme['html']['font-weight']=='bold' else QFont.Normal)
        text_char_format.setFontItalic(True if theme['html']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['HTML'] = text_char_format

        self.rehighlight()

    def highlightBlock(self, text):
        text = str(text)
        self.highlightMarkdown(text,0)
        self.highlightHtml(text)

    def highlightMarkdown(self, text, strt):
        cursor = QTextCursor(self.document())
        bf = cursor.blockFormat()
        self.setFormat(0, len(text), QColor(self.theme['color']))
        #bf.clearBackground()
        #cursor.movePosition(QTextCursor.End)
        #cursor.setBlockFormat(bf)

        #Block quotes can contain all elements so process it first
        self.highlightBlockQuote(text, cursor, bf, strt)

        #If empty line no need to check for below elements just return
        if self.highlightEmptyLine(text, cursor, bf, strt):
            return

        #If horizontal line, look at pevious line to see if its a header, process and return
        if self.highlightHorizontalLine(text, cursor, bf, strt):
            return

        if self.highlightAtxHeader(text, cursor, bf, strt):
            return

        self.highlightList(text, cursor, bf, strt)

        self.highlightLink(text, cursor, bf, strt)

        self.highlightImage(text, cursor, bf, strt)

        self.highlightCodeSpan(text, cursor, bf, strt)

        self.highlightEmphasis(text, cursor, bf, strt)

        self.highlightBold(text, cursor, bf, strt)

        self.highlightCodeBlock(text, cursor, bf, strt)

    def highlightBlockQuote(self, text, cursor, bf, strt):
        found = False
        mo = re.search(self.MARKDOWN_KEYS_REGEX['BlockQuote'],text)
        if mo:
            self.setFormat(mo.start(), mo.end() - mo.start(), self.MARKDOWN_KWS_FORMAT['BlockQuote'])
            unquote = re.sub(self.MARKDOWN_KEYS_REGEX['BlockQuoteCount'],'',text)
            spcs = re.match(self.MARKDOWN_KEYS_REGEX['BlockQuoteCount'],text)
            spcslen = 0
            if spcs:
                spcslen = len(spcs.group(0))
            self.highlightMarkdown(unquote,spcslen)
            found = True
        return found

    def highlightEmptyLine(self, text, cursor, bf, strt):
        textAscii = str(text.replace(u'\u2029','\n'))
        if textAscii.strip():
            return False
        else:
            return True

    def highlightHorizontalLine(self, text, cursor, bf, strt):
        found = False
        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['HR'],text):
            prevBlock = self.currentBlock().previous()
            prevCursor = QTextCursor(prevBlock)
            prev = prevBlock.text()
            prevAscii = str(prev.replace(u'\u2029','\n'))
            if prevAscii.strip():
                #print "Its a header"
                prevCursor.select(QTextCursor.LineUnderCursor)
                #prevCursor.setCharFormat(self.MARKDOWN_KWS_FORMAT['Header'])
                formatRange = QTextLayout.FormatRange()
                formatRange.text_char_format = self.MARKDOWN_KWS_FORMAT['Header']
                formatRange.length = prevCursor.block().length()
                formatRange.start = 0
                prevCursor.block().layout().setAdditionalFormats([formatRange])
            self.setFormat(mo.start()+strt, mo.end() - mo.start(), self.MARKDOWN_KWS_FORMAT['HR'])

        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['eHR'],text):
            prevBlock = self.currentBlock().previous()
            prevCursor = QTextCursor(prevBlock)
            prev = prevBlock.text()
            prevAscii = str(prev.replace(u'\u2029','\n'))
            if prevAscii.strip():
                #print "Its a header"
                prevCursor.select(QTextCursor.LineUnderCursor)
                #prevCursor.setCharFormat(self.MARKDOWN_KWS_FORMAT['Header'])
                formatRange = QTextLayout.FormatRange()
                formatRange.text_char_format = self.MARKDOWN_KWS_FORMAT['Header']
                formatRange.length = prevCursor.block().length()
                formatRange.start = 0
                prevCursor.block().layout().setAdditionalFormats([formatRange])
            self.setFormat(mo.start()+strt, mo.end() - mo.start(), self.MARKDOWN_KWS_FORMAT['HR'])
        return found

    def highlightAtxHeader(self, text, cursor, bf, strt):
        found = False
        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['HeaderAtx'],text):
            #bf.setBackground(QBrush(QColor(7,54,65)))
            #cursor.movePosition(QTextCursor.End)
            #cursor.mergeBlockFormat(bf)
            self.setFormat(mo.start()+strt, mo.end() - mo.start(), self.MARKDOWN_KWS_FORMAT['HeaderAtx'])
            found = True
        return found

    def highlightList(self, text, cursor, bf, strt):
        found = False
        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['UnorderedList'],text):
            self.setFormat(mo.start()+strt, mo.end() - mo.start()-strt, self.MARKDOWN_KWS_FORMAT['UnorderedList'])
            found = True

        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['OrderedList'],text):
            self.setFormat(mo.start()+strt, mo.end() - mo.start()-strt, self.MARKDOWN_KWS_FORMAT['OrderedList'])
            found = True
        return found

    def highlightLink(self, text, cursor, bf, strt):
        found = False
        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['Link'],text):
            self.setFormat(mo.start()+strt, mo.end() - mo.start()-strt, self.MARKDOWN_KWS_FORMAT['Link'])
            found = True
        return found

    def highlightImage(self, text, cursor, bf, strt):
        found = False
        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['Image'],text):
            self.setFormat(mo.start()+strt, mo.end() - mo.start()-strt, self.MARKDOWN_KWS_FORMAT['Image'])
            found = True
        return found

    def highlightCodeSpan(self, text, cursor, bf, strt):
        found = False
        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['CodeSpan'],text):
            self.setFormat(mo.start()+strt, mo.end() - mo.start()-strt, self.MARKDOWN_KWS_FORMAT['CodeSpan'])
            found = True
        return found

    def highlightBold(self, text, cursor, bf, strt):
        found = False
        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['Bold'],text):
            self.setFormat(mo.start()+strt, mo.end() - mo.start()-strt, self.MARKDOWN_KWS_FORMAT['Bold'])
            found = True

        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['uBold'],text):
            self.setFormat(mo.start()+strt, mo.end() - mo.start()-strt, self.MARKDOWN_KWS_FORMAT['uBold'])
            found = True
        return found

    def highlightEmphasis(self, text, cursor, bf, strt):
        found = False
        unlist = re.sub(self.MARKDOWN_KEYS_REGEX['UnorderedListStar'],'',text)
        spcs = re.match(self.MARKDOWN_KEYS_REGEX['UnorderedListStar'],text)
        spcslen = 0
        if spcs:
            spcslen = len(spcs.group(0))
        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['Italic'],unlist):
            self.setFormat(mo.start()+strt+spcslen, mo.end() - mo.start()-strt, self.MARKDOWN_KWS_FORMAT['Italic'])
            found = True
        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['uItalic'],text):
            self.setFormat(mo.start()+strt, mo.end() - mo.start()-strt, self.MARKDOWN_KWS_FORMAT['uItalic'])
            found = True
        return found

    def highlightCodeBlock(self, text, cursor, bf, strt):
        found = False
        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['CodeBlock'], text):
            stripped = text.lstrip()
            if stripped[0] not in ('*','-','+','>'):
                self.setFormat(mo.start() + strt, mo.end() - mo.start(), self.MARKDOWN_KWS_FORMAT['CodeBlock'])
                found = True
        
        return found

    def highlightHtml(self, text):
        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['Html'], text):
            self.setFormat(mo.start(), mo.end() - mo.start(), self.MARKDOWN_KWS_FORMAT['HTML'])

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        text_edit = QTextEdit("## Some header<br>Some paragraph")

        syntax_highlighter = MarkdownHighlighter(text_edit)

        self.setCentralWidget(text_edit)

        self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    main_window = MainWindow()

    sys.exit(app.exec_())
