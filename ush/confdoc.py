#! /usr/bin/env python

##@namespace confdoc
# Generates the doc/config-files.dox, which documents configuration files.
#
# Run by the documentation generator in @c sorc/doc/compile.  Syntax:
#
#     ../../ush/confdoc.py ../../parm/metplus.conf ... more ... > ../../doc/config-files.dox
#
# That will read in the listed conf files, process Doxygen-like
# comments, and generate multiple pages of documentation.  There will
# be one page for each conf file, another page listing all sections
# and options, and a final top-level page
#
# The documentation comments are similar to the syntax Doxygen uses
# for Python, but with the addition of ";;" comments for documenting
# options on the same line they are defined:
#
#     ## Brief description of section
#     #
#     # Detailed description of section
#     [section]
#     option1 = value ;; Brief description of option1
#     
#     ## Brief description of option2
#     # 
#     # Detailed description of option2
#     option2 = value
#
# The descriptions can contain the usual Doxygen and Markdown syntax.
#
# There are a number of pages and sections generated with the
# following anchors.  These are the page anchors:
#
#  + conf-files --- Main page that lists all subpages.
#  + conf-options --- Subpage that contains all section and option 
#      documentation
#  + conf-file-[filename] --- Page for the specified file.  Any dots
#      (".") are replaced with underscores ("_") in the filename.
#
# These are the section anchors:
#
#  + conf-sec-runwrf --- Documentation section for the [runwrf] section
#  + conf-sec-runwrf-wm3c_ranks --- Documentation subsection for the
#       wm3c_ranks option in the [runwrf] section.  Any percent signs
#       ("%") in the option name are replaced with "-P-"
#  + conf-[filename]-runwrf --- Documentation for the [runwrf] section
#       in the specified file
#  + conf-[filename]-runwrf-wm3c_ranks --- Documentation for the
#       [runwrf] section's wm3c_ranks option in the specified file.

import re, os, collections, sys
from io import StringIO

########################################################################

class docbase(object):
    """!Stores documentation for all configuration options and sections."""
    def __init__(self):
        """!docbase constructor

        Initializes the documentation to an empty configuration suite.
        No sections, no options, no files, etc."""
        self.sections=dict()
        self.secref=collections.defaultdict(list)
        self.secrefset=collections.defaultdict(set)
        self.secfile=collections.defaultdict(list)
        self.secinc=collections.defaultdict(list)
        self.seclist=list()
        self.options=dict()
        self.optbrief=dict()
        self.secbrief=dict()
        self.fileset=set()
        self.filelist=list()
        self.__subdoc=dict()
        self.blocks=collections.defaultdict(list)

    def set_subdoc(self,basename,doc):
        """!Sets the documentation object that will contain
        file-specific information for the given file.

        @param basename The file basename
        @param doc The documentation object, a subclass of docbase"""
        if basename is not None and basename not in self.fileset:
            self.fileset.add(basename)
            self.filelist.append(basename)
        self.__subdoc[basename]=doc

    ##@var sections
    # Mapping of section name to description
    
    ##@var secref
    # Mapping from section name to anchor name
    
    ##@var secfile
    # Mapping from doxified filename to list of sections in that file
    
    ##@var secinc
    # Mapping from section name to the list of sections that are \@inc
    # included by that section
    
    ##@var seclist
    # List of section names, in the order they were first seen
    
    ##@var options
    # Mapping from option anchor name to the description of the option
    
    ##@var secbrief
    # Mapping from section name to the section's brief description

    ##@var optbrief
    # Mapping from option anchor to the option's brief description
    
    ##@var blocks
    # Mapping from file basename to the list of documentation blocks in
    # that file that were not associated with any section or option.
    # These blocks are placed at the top of that file's documentation page.

    def fileanch(self,basename):
        """!Returns the anchor for a configuration file.
        @param basename the basename of the configuration file."""
        return "conf-file-%s"%(basename.replace('.','_'),)

    def secanch(self,section,where='sec'):
        """!Returns the anchor for a specified section.
        @param section The conf file section name.
        @param where Configuration override file name.  Default: "sec"
          which is the special name used for the page that stores
          information about ALL configuration options."""
        assert(section is not None)
        return 'conf-%s-%s'%(where,section)

    def optanch(self,section,option,where='sec'):
        """!Returns the anchor for a specified option.
        @param section The conf file section name.
        @param option The option name.
        @param where Configuration override file name.  Default: "sec"
          which is the special name used for the page that stores
          information about ALL configuration options."""
        assert(section is not None)
        assert(option is not None)
        return( ('conf-%s-%s-%s'%(where,section,option)).replace('%','-P-') )

    def _secsec(self,section,brief,detail):
        """!Generates a Doxygen section to represent a configuration
        file section."""
        anchor=self.secanch(section)
        if brief:
            out='@section %s Section [%s]\n%s\n\n'%(anchor,section,brief)
        else:
            out='@section %s Section [%s]\n\n'%(anchor,section)
        if detail:
            out+="%s\n\n"%(detail,)
        return out

    def _optpar(self,section,name,ivalue,brief,detail=None,basename=None):
        """!Generates a Doxygen subsection to represent a configuration
        option in the specified section.

        @todo Allow documentation of options that are not in sections.

        @param section The section name.  If this is None or blank
          then an empty string is returned so that confdoc will not
          abort when it sees an option outside of a section.  (The
          Python ConfigParser uses such options to set default
          values.)
        @param name The option name.
        @param ivalue The first line of the option value, with an
          ellipsis at the end if it is multiple lines.
        @param brief The brief documentation, or None if it is absent.
        @param detail The detailed documentation, or None if it is absent.
        @param basename The conf file basename, or None if absent."""
        if not section:
            # Ignore options that are outside of sections since we
            # have no good way of dealing with this in the
            # documentation structure yet.
            return ''
        anchor=self.optanch(section,name)
        if brief:
            out="@subsection %s [%s] %s\n %s\n\n"%(anchor,section,name,brief)
        else:
            out="@subsection %s [%s] %s\n\n"%(anchor,section,name)
        if ivalue is not None:
            out+='@code{.conf}\n[%s]\n%s = %s\n\endcode\n\n'%(section,name,ivalue)
        if detail:
            out+="%s\n\n"%(detail,)
        if basename:
            out+="Defined in @ref %s\n\n"%(self.fileanch(basename),)
        return out

    def make_brief(self,detail):
        """!Given a detailed description for something that has no
        brief description, return the brief description.
        @param detail the detailed description
        @returns A brief description, or None if no suitable 
          description was found."""
        dlines=detail.split('\n')
        for line in dlines:
            tline=line.strip()
            if len(tline)>2: 
                if len(dlines)>1:
                    return tline+'...'
                return tline
        return None

    def add_section(self,section,brief,detail,replace=None):
        """!Adds documentation for a conf section

        @param section The conf section name
        @param brief The brief documentation
        @param detail The detailed documentation or None
        @param replace If True, any existing documentation is
           replaced.  Otherwise, it is ignored."""
        if replace is None:
            replace=brief or detail
        if detail and not brief: 
            brief=self.make_brief(detail)
        replaceokay = replace and (brief or detail)
        if section not in self.sections or replaceokay:
            anchor=self.secanch(section)
            self.sections[section]=self._secsec(section,brief,detail)
            self.seclist.append(section)
            if brief:
                self.secbrief[section]=brief
            self.secfile[anchor].append(section)

    def section_inc(self,section,inc):
        """!Sets the \@inc list for a conf section

        @param section The conf section name
        @param inc The contents of the \@inc= option"""
        splat=re.split('\s*,\s*',inc)
        if splat and splat[0]:
            self.secinc[section]=splat
        else:
            self.secinc[section]=list()

    def file_block(self,basename,brief,detail):
        """!Adds a documentation block that is not associated with any
        section or option.  

        @param basename the file that contains the block
        @param brief the brief documentation
        @param detail the detailed documentation"""
        if basename not in self.fileset:
            self.fileset.add(basename)
            self.filelist.append(basename)
        if brief or detail:
            s= (brief if brief else '') + '\n\n' + \
               (detail if detail else '')
            self.blocks[basename].append(s)

    def add_option(self,section,option,ivalue,brief,detail,basename=None,replace=None):
        """!Adds documentation for an option in a conf section

        @param section The conf section name
        @param option The name of the option in that section
        @param ivalue A shortened form of the option value
        @param brief The brief documentation
        @param detail The detailed documentation
        @param basename The file basename
        @param replace If True, any existing documentation is
           replaced.  Otherwise, it is ignored."""
        if replace is None:
            replace=brief or detail
        if basename is not None and basename not in self.fileset:
            self.fileset.add(basename)
            self.filelist.append(basename)
        anchor=self.optanch(section,option)
        replaceokay = replace and (brief or detail)
        if anchor in self.options and not replaceokay:
            return
        self.options[anchor]=self._optpar(section,option,ivalue,brief,detail,basename)
        self.optbrief[anchor]=brief
        if section and anchor not in self.secrefset[section]:
            self.secref[section].append([anchor,option])
            self.secrefset[section].add(anchor)

    def print_doc(self,s):
        """!Writes Doxygen documentation to the stream "s" which is
        assumed to be a io.StringIO.

        @param s a io.StringIO to receive documentation."""
        s.write('Documentation for all configuration files in the parm/ directory.  Subpages include:\n\n');
        s.write(' + @ref conf-options "All configuration sections and options."\n\n')
        for basename in self.filelist:
            #for basename,brdet in self.blocks.items():
            doxified=basename.replace('.','_')
            s.write(' + @subpage conf-file-%s "File parm/%s"\n\n'%(
                    doxified,basename))

        for basename in self.filelist:
            #for basename,brdet in self.blocks.items():
            doxified=basename.replace('.','_')
            s.write('\n@page conf-file-%s File parm/%s\n\n'%(
                    doxified,basename))
            if basename in self.blocks and self.blocks[basename]:
                brdet=self.blocks[basename]
                s.write('\n\n'.join(brdet) + '\n\n')
            if basename in self.__subdoc:
                self.__subdoc[basename].print_subdoc(s)
            elif doxified in self.secfile:
                s.write('Sections in this file:\n\n')
                for sec in sorted(self.secfile[doxified]):
                    if sec in self.secbrief:
                        s.write(' + @ref conf-sec-%s "[%s]" --- %s\n\n'%(
                                sec,sec,self.secbrief[sec]))
                    else:
                        s.write(' + @ref conf-sec-%s "[%s]"\n\n'%(
                                sec,sec))

        for sec in self.secref:
            if sec not in self.sections:
                self.add_section(sec,None,None,replace=False)

        seclist=sorted(list(set(self.seclist)))

        s.write('@page conf-options All Configuration Options\n\n')
        s.write('This page documents configuration options for all known sections:\n\n')
        for sec in seclist:
            if sec in self.secbrief:
                s.write(' + @ref conf-sec-%s "[%s]" --- %s\n\n'
                        %(sec,sec,self.secbrief[sec]))
            else:
                s.write(' + @ref conf-sec-%s "[%s]"\n\n'%(sec,sec))
                
        for sec in seclist:
            if sec in self.sections:
                text=self.sections[sec]
                s.write('\n\n%s\n\n'%(text,))
            if self.secref[sec]:
                s.write('\n\nOptions in this section:\n\n')
                for fullopt,name in self.secref[sec]:
                    if fullopt in self.optbrief and self.optbrief[fullopt]:
                        s.write(' + @ref %s "%s" --- %s\n\n'%(
                                fullopt,name,self.optbrief[fullopt]))
                    else:
                        s.write(' + @ref %s "%s"\n\n'%(fullopt,name))
                if sec in self.secinc and self.secinc[sec]:
                    s.write('Inherits from the following sections:\n\n')
                    for isec in self.secinc[sec]:
                        if isec in self.secbrief:
                            s.write(' + @ref conf-sec-%s "[%s]" --- %s\n\n'
                                    %(isec,isec,self.secbrief[isec]))
                        else:
                            s.write(' + @ref conf-sec-%s "[%s]"\n\n'%(isec,isec))
                s.write('\n\n')
                for fullopt,name in self.secref[sec]:
                    if fullopt in self.options and self.options[fullopt]:
                        s.write(self.options[fullopt]+'\n\n')


########################################################################

class override(docbase):
    """!Subclass of docbase for documenting files that override the
    base configuration."""
    def __init__(self,basename,parent,filepart=None,replace=False):
        """!Class override constructor
        @param basename The file basename
        @param parent The parent docbase object that documents this
            group of conf files, or all conf options.
        @param filepart The modified filename for anchors.  
            This should be the basename with "." replaced by "_".
        @param replace If True, replace existing documentation when
            new values are found, otherwise ignore new docs"""
        if not isinstance(parent,docbase):
            raise TypeError('parent argument to override.__init__ must be a docbase')
        self.__parent=parent
        self.__basename=basename
        self.__replace=replace
        super(override,self).__init__()
        self.__filepart=filepart
        if not self.__filepart:
            self.__filepart=basename.replace('.','_')
        self.__parent.set_subdoc(basename,self)
        
    def secanch(self,section,where=None):
        """!Returns the anchor for the specified section

        @param section The conf section name
        @param where Optional: the conf file basename."""
        if where is None: 
            where=self.__filepart
        return super(override,self).secanch(section,where)

    def optanch(self,section,option,where=None):
        """!Returns the anchor for a specified section and option

        @param option the option of interest
        @param section the section that contains the option
        @param Optional: the conf file basename"""
        if where is None: 
            where=self.__filepart
        return super(override,self).optanch(section,option,where)


    def _secsec(self,section,brief,detail):
        """!Generates the contents of the documentation section that
        documents the specified conf section.

        @protected
        @param section the conf section name
        @param brief the brief documentation
        @param detail the detailed documentation
        @returns the section text"""
        if not brief:
            (brief,detail)=self.find_secdoc(section,detail)
        return super(override,self)._secsec(section,brief,detail)

    def section_inc(self,section,inc):
        """!Sets the \@inc list for a conf section

        @param section The conf section name
        @param inc The contents of the \@inc= option"""
        self.__parent.section_inc(section,inc)
        super(override,self).section_inc(section,inc)

    def file_block(self,basename,brief,detail):
        """!Adds a documentation block that is not associated with any
        section or option.  

        @param basename the file that contains the block
        @param brief the brief documentation
        @param detail the detailed documentation"""
        self.__parent.file_block(basename,brief,detail)

    def add_section(self,section,brief,detail,replace=True):
        """!Adds documentation for a conf section

        @param section The conf section name
        @param brief The brief documentation
        @param detail The detailed documentation or None
        @param replace If True, any existing documentation is
           replaced.  Otherwise, it is ignored."""
        self.__parent.add_section(section,brief,detail,self.__replace)
        super(override,self).add_section(section,brief,detail,replace)

    def add_option(self,section,option,ivalue,brief,detail,basename=None,
                   replace=True):
        """!Adds documentation for an option in a conf section

        @param section The conf section name
        @param option The name of the option in that section
        @param ivalue A shortened form of the option value
        @param brief The brief documentation
        @param detail The detailed documentation
        @param basename The file basename
        @param replace If True, any existing documentation is
           replaced.  Otherwise, it is ignored."""
        self.__parent.add_option(
            section,option,ivalue,brief,detail,basename,self.__replace)
        super(override,self).add_option(
            section,option,ivalue,brief,detail,basename,replace)

    def find_optbrief(self,section,option):
        """!Finds the brief documentation for a section

        Checks first this documentation object, and then the parent,
        searching for something that has documentation for the option.
        @param section The conf section name
        @param option The name of the option in that section"""
        anchor=self.optanch(section,option)
        if anchor in self.optbrief and self.optbrief[anchor]:
            return self.optbrief[anchor]
        anchor=self.__parent.optanch(section,option)
        if anchor in self.__parent.optbrief and self.__parent.optbrief[anchor]:
            return self.__parent.optbrief[anchor]
        return None

    def find_secbrief(self,section):
        """!Finds the brief documentation for a section

        Checks first this documentation object, and then the parent,
        searching for something that has documentation for a section.
        @param section The conf section name"""
        if section in self.secbrief and self.secbrief[section]:
            return self.secbrief[section]
        if section in self.__parent.secbrief and \
                self.__parent.secbrief[section]:
            return self.__parent.secbrief[section]
        if section=='namelist_outer':
            print('Could not find %s in self or parent.  Gave up.'%(section,), file=sys.stderr)
        return None

    def find_secdoc(self,section,detail):
        """!Finds the brief and detailed documentation for a section

        Checks first this documentation object, and then the parent,
        searching for something that has documentation for a section.
        @param section The conf section name
        @param detail detailed documentation, if available, and None otherwise
        @returns A tuple (brief,detail) containing any documentation found."""
        if section in self.secbrief and self.secbrief[section]:
            if section=='namelist_outer':
                print('Found %s in self'%(section,), file=sys.stderr)
            return (self.secbrief[section],detail)
        if section in self.__parent.secbrief and self.__parent.secbrief[section]:
            detail='See the @ref conf-sec-%s "main documentation for [%s]" '\
              'for details.'%(section,section)
            if section=='namelist_outer':
                print('Found %s in parent'%(section,), file=sys.stderr)
            return (self.__parent.secbrief[section],detail)
        if section=='namelist_outer':
            print('Could not find %s in self or parent.  Gave up.'%(section,), file=sys.stderr)
        return (None,None)

    def print_subdoc(self,s):
        """!Prints the documentation to the specified stream
        @param s The stream, ideally a io.StringIO."""
        s.write('This is a configuration override file.\n')
        self.print_sec_opt(s)

    def print_sec_opt(self,s):
        """!Prints the section and option part of the documentation to
        the given stream.
        @param s The stream, ideally a io.StringIO."""
        if not self.seclist:
            s.write('This file does not override any options.\n\n')
            return

        seclist=sorted(list(set(self.seclist)))
        s.write('This file sets options in the following sections:\n\n')
        for sec in seclist:
            a=self.secanch(sec)
            brief=self.find_secbrief(sec)
            if brief:
                s.write(' + @ref %s "[%s]" --- %s\n\n'%(a,sec,brief))
            else:
                s.write(' + @ref %s "[%s]"\n\n'%(a,sec))

        for sec,text in self.sections.items():
            s.write('\n\n%s\n\n'%(text,))
            if self.secref[sec]:
                s.write('\n\nOptions in this section:\n\n')
                for fullopt,name in self.secref[sec]:
                    brief=self.find_optbrief(sec,name)
                    if brief:
                        s.write(' + @ref %s "%s" --- %s\n\n'%(
                                fullopt,name,brief))
                    else:
                        s.write(' + @ref %s "%s"\n\n'%(fullopt,name))
                s.write('\n\n')
                for fullopt,name in self.secref[sec]:
                    if fullopt in self.options and self.options[fullopt]:
                        s.write(self.options[fullopt]+'\n\n')

########################################################################

class coredoc(override):
    """!Subclass of override, for documenting the core configuration
     files."""
    def __init__(self,basename,parent):
        """!coredoc constructor
        @param basename the file basename
        @param parent The parent docbase"""
        super(coredoc,self).__init__(basename,parent,None,True)
    def print_subdoc(self,s):
        """!Prints the documentation to the specified stream
        @param s The stream, ideally a io.StringIO."""
        s.write('This is one of the core configuration files, read in by all METplus configurations.\n')
        self.print_sec_opt(s)

########################################################################

class parsefile(object):
    """!Config file parser.  Parses comment blocks as described in the
    confdoc."""
    def __init__(self,filename,doc,maxread=500000):
        """!Opens the specified file, prepares to parse.  Only the
        first maxread bytes are read.
        @param filename the *.conf file to read
        @param doc the docbase object to receive documentation
        @param maxread maximum number of lines to read"""
        self.doc=doc
        with open(filename,'rt') as f:
            self.lines=f.readlines(maxread)
        self.iline=0
        self.basename=os.path.basename(filename)
        self.doxified=self.basename.replace('.','_')
        self.brief=None
        self.detail=None
        self.section=None

    ##@var iline
    # Current line number counting from 0

    ##@var basename
    # Basename of the current file

    ##@var doxified
    # The basename with "." replaced with "_"

    ##@var brief
    # Brief portion of description that has not yet been assigned to
    # an option or section.

    ##@var detail
    # Detailed portion of description that has not yet been assigned to
    # an option or section.

    ##@var section
    # Section being parsed

    def eot(self):
        """!Have we run out of lines to parse?"""
        return self.iline>=len(self.lines)
    def match(self,pattern):
        """!Calls re.match(pattern,...) on the current line, returning
        the result.
        @param pattern argument to re.match: the pattern to match"""
        if self.iline>=len(self.lines): 
            raise Exception('Internal error: line %d is beyond last line %d'%(
                    self.iline+1,len(self.lines)))
        return re.match(pattern,self.lines[self.iline])
    def parse(self):
        """!Loops over all lines, parsing text and sending the result
        to global variables."""
        while not self.eot():

            # Is it a block comment start?
            m=self.match('^#[#!]\s*(\S.*?)\s*$')
            if m:
                self.brief=m.groups()[0]
                self.iline+=1
                self.readblock()
                continue

            # Is it a [section] start line?
            m=self.match('^\s*\[\s*([a-zA-Z][a-zA-Z0-9_-]*)\s*\].*$')
            if m:
                self.section=m.groups()[0]
                assert(self.section)
                if self.section:
                    assert(self.detail != 'None')
                    assert(self.brief != 'None')
                    self.doc.add_section(self.section,self.brief,self.detail)
                self.iline+=1
                self.brief=None
                self.detail=None
                continue
 
            # Is it an @inc= line?
            m=self.match('^@inc\s*=\s*(\S+)\s*$')
            if m and self.section:
                self.doc.section_inc(self.section,m.groups()[0])
                self.iline+=1
                continue
           
            # Is it an option=value line?
            m=self.match('''(?ix)
^
(
  [a-zA-Z][a-zA-Z0-9_%-]*
)

\s* = \s*

( 
  (?: [^"' \t]+
  |      \\047(?:[^\\047\\134]|\\134\\134|\\134\\047)*\\047
  |      \\042(?:[^\\042\\134]|\\134\\134|\\134\\042)*\\042
  )
)?
(?:\s+
        (;[;!]\s*.*?)\s*
   |    ;[^;!].*
   |    \s*
)
$''')
            if m:
                g=m.groups()
                if len(g)>2 and g[2] and len(g[2])>2:
                    self.brief=g[2][2:].strip()
                self.value=g[1]
                self.iline+=1
                self.readoption(g[0])
                continue

            m=self.match('''(?ix)
^
(
  [a-zA-Z][a-zA-Z0-9_%-]*
)

\s* = \s*

( 
  (?: [^"' \t]+
  |      \\047(?:[^\\047\\134]|\\134\\134|\\134\\047)*\\047
  |      \\042(?:[^\\042\\134]|\\134\\134|\\134\\042)*\\042
  )
)?
(?:\s+
        ;[^;!].*
   |    \s*
)?
$''')
            if m:
                g=m.groups()
                self.value=g[1]
                self.iline+=1
                self.readoption(g[0])
                continue


            # Otherwise, ignore the line and store unused
            # documentation blocks:
            if self.brief or self.detail:
                self.doc.file_block(self.basename,self.brief,self.detail)
            self.brief=None
            self.detail=None

            self.iline+=1

        # Send any unused comment blocks:
        if self.brief or self.detail:
            self.doc.file_block(self.basename,self.brief,self.detail)

    def readoption(self,name):
        """!Reads later lines of a multi-line option=value assignment
        @param name the option name"""
        (brief,detail)=(self.brief,self.detail)
        self.brief=None
        self.detail=None
        nlines=1
        while not self.eot():
            if not self.match('^\s+(\S.*?)\s*$'): 
                break
            self.iline+=1
            nlines+=1
        ivalue=self.value
        if nlines>1: ivalue=ivalue+'...'
        self.doc.add_option(self.section,name,ivalue,brief,detail,self.basename)

    def readblock(self):
        """!Reads the second and later lines of a multi-line comment
        block.  Assumes data is already in the self.brief variable."""
        isbrief=True
        detail=list()
        self.detail=None
        if self.brief is None: self.brief=''
        while not self.eot():
            if self.match('^#+!?\s*$'):
                if isbrief:
                    isbrief=False
                else:
                    detail.append(' ')
                self.iline+=1
                continue
            m=self.match('^#+!?\s?(.*)$')
            if m:
                doc=m.groups()[0]
                if not doc: doc=' '
                if isbrief: 
                    self.brief=self.brief+' '+doc
                else:
                    detail.append(doc)
                self.iline+=1
                continue

            # Do NOT consume any other type of line or the logic in
            # parse() will break:
            break
        if not self.brief and detail:
            self.brief=(detail[0]+'...').replace('\n','')
        if not isbrief and detail:
            self.detail='\n'.join(detail)
            assert(self.detail != 'None')

########################################################################

def main(args):
    """!Main program for confdoc.  See the confdoc documentation for
    details."""
    s=StringIO()
    doc=docbase()
    for arg in args:
        bn=os.path.basename(arg)
        if bn=='metplus.conf' or bn=='another.conf':
            subdoc=coredoc(bn,doc)
        else:
            subdoc=override(bn,doc)
        parsefile(arg,subdoc).parse()
    s.write('/** @page conf-files All Configuration Files\n')
    doc.print_doc(s)
    out=s.getvalue()
    s.close()
    out=out.replace('*/','* /')+'\n\n*/'
    print ('/* WARNING: DO NOT EDIT THIS FILE.\nIt is automatically generated from the parm *.conf files.\nEdit those files instead.\n*/\n\n')
    print (out)

if __name__=='__main__':
    main(sys.argv[1:])
