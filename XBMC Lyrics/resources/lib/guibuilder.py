"""
This module creates your scripts GUI from a standard XBMC skinfile.xml. It works for both Windows and
WindowDialogs. Hopefully it will make it easier to skin your scripts for different XBMC skins.

Credits:
GetConditionalVisibility(), GetSkinPath(), LoadIncludes(), LoadIncludesFromXML(), ResolveIncludes()
The above functions were translated from Xbox Media Center"s source, thanks Developers.
A special thanks to elupus for shaming me into doing it the right way. :)

Nuka1195
"""

import os
import xbmc
import xbmcgui
import xml.dom.minidom
#import traceback


class GUIBuilder:
    """ Class to create a dictionary of controls and add them to a Window or WindowDialog """
    def create_gui( self,
        win, skin="Default", xml_name="skin", skin_path="resources\\skins", image_path="gfx",
        use_desc_as_key=True, language=False
        ):
        """ main function to create the GUI """
        try:
            succeeded = True
            self.win = win
            xml_file, image_path = self._get_skin_path( skin, xml_name, skin_path, image_path )
            self.use_desc_as_key = use_desc_as_key
            self._ = language
            self._setup_variables()
            self.ClearIncludes()
            succeeded = self._parse_xml_file( xml_file, image_path )
            if ( succeeded ):
                self._set_navigation()
                if ( self.defaultControl and self.defaultControl in self.navigation and self.navigation[ self.defaultControl ][ 0 ] in self.win.controls ):
                    self.win.setFocus( self.win.controls[ self.navigation[ self.defaultControl ][ 0 ] ][ "control" ] )
                self._set_visibility_and_animations()
                self._clear_variables()
            else: raise
        except:
            #traceback.print_exc()
            succeeded = False
        return succeeded, image_path

    def _get_skin_path( self, skin, xml_name, skin_path, image_path ):
        """ determines the skin and image path """
        base_path = os.path.join( os.getcwd().replace( ";", "" ), skin_path )
        if ( skin == "Default" ): current_skin = xbmc.getSkinDir()
        else: current_skin = skin
        if ( not os.path.exists( os.path.join( base_path, current_skin ))): current_skin = "Default"
        skin_path = os.path.join( base_path, current_skin )
        image_path = os.path.join( skin_path, image_path )
        if ( self.win.getResolution() == 0 or self.win.getResolution() % 2 ): xml_file = "%s_16x9.xml" % ( xml_name, )
        else: xml_file = "%s.xml" % ( xml_name, )
        if ( not os.path.isfile( os.path.join( skin_path, xml_file ))): xml_file = "%s.xml" % ( xml_name, )
        xml_file = os.path.join( skin_path, xml_file )
        return xml_file, image_path

    def _setup_variables( self ):
        """ initializes variables """
        self.win.controls = {}
        #self.win.controlKey = {}
        self.navigation = {}
        self.resolutions = { "1080i" : 0, "720p" : 1, "480p" : 2, "480p16x9" : 3, "ntsc" : 4, "ntsc16x9" : 5, "pal" : 6, "pal16x9" : 7, "pal60" : 8, "pal6016x9" : 9 }
        self.resPath = dict( zip( self.resolutions.values(), self.resolutions.keys() ) )
        self.currentResolution = self.win.getResolution()
        self.include_doc = []
        self.resolution = self.resolutions[ "pal" ]

    def _clear_variables( self ):
        """ clears variables and unlinks docs """
        self.navigation = None
        self.resPath = None
        self.resolutions = None
        self.currentResolution = None
        self.resolution = None
        for doc in self.include_doc:
            try: doc.unlink()
            except: pass

    def _add_control( self, control ):
        """ sets up the controls disctionary and adds the controls to the window """
        try:
            succeeded = True
            control[ "special" ] = False
            if ( self.use_desc_as_key ): key = control[ "description" ]
            else: key = control[ "id" ]
            # image control
            if ( control[ "type" ] == "image" ):
                if ( control[ "info" ] ):
                    control[ "texture" ] = xbmc.getInfoImage( control[ "info" ][ 0 ] )
                current_control = xbmcgui.ControlImage(
                    x = control[ "posx" ],
                    y = control[ "posy" ],
                    width = control[ "width" ],
                    height = control[ "height" ],
                    filename = control[ "texture" ],
                    colorKey = control[ "colorkey" ],
                    aspectRatio = control[ "aspectratio" ],
                    colorDiffuse = control[ "colordiffuse" ]
                )
                self.win.addControl( current_control )
            # progress control
            elif ( control[ "type" ] == "progress" ):
                current_control = xbmcgui.ControlProgress(
                    x = control[ "posx" ],
                    y = control[ "posy" ],
                    width = control[ "width" ],
                    height = control[ "height" ],
                    texturebg = control[ "texturebg" ],
                    textureleft = control[ "lefttexture" ],
                    texturemid = control[ "midtexture" ],
                    textureright = control[ "righttexture" ],
                    textureoverlay = control[ "overlaytexture" ]
                )
                self.win.addControl( current_control )
            # label control
            elif ( control[ "type" ] == "label" ):
                if ( control[ "info" ] ):
                    control[ "label" ][ 0 ] = xbmc.getInfoLabel( control[ "info" ][ 0 ] )
                current_control = xbmcgui.ControlLabel(
                    x = control[ "posx" ],
                    y = control[ "posy" ],
                    width = control[ "width" ],
                    height = control[ "height" ],
                    label = control[ "label" ][ 0 ],
                    font = control[ "font" ],
                    textColor = control[ "textcolor" ],
                    disabledColor = control[ "disabledcolor" ],
                    alignment = control[ "align" ],
                    hasPath = control[ "haspath" ],
                    #shadowColor = control[ "shadowcolor" ],
                    angle = control[ "angle" ]
                )
                self.win.addControl( current_control )
            # button control
            elif ( control[ "type" ] == "button" ):
                if ( control[ "info" ] ):
                    control[ "label" ][ 0 ] = xbmc.getInfoLabel( control[ "info" ][ 0 ] )
                current_control = xbmcgui.ControlButton(
                    x = control[ "posx" ],
                    y = control[ "posy"],
                    width = control[ "width" ],
                    height = control[ "height" ],
                    label = control[ "label" ][ 0 ],
                    font = control[ "font" ],
                    textColor = control[ "textcolor" ],
                    focusedColor = control[ "focusedcolor" ],
                    disabledColor = control[ "disabledcolor" ],
                    alignment = control[ "align" ],
                    angle = control[ "angle" ],
                    shadowColor = control[ "shadowcolor" ],
                    focusTexture = control[ "texturefocus" ],
                    noFocusTexture = control[ "texturenofocus" ],
                    textXOffset = control[ "textoffsetx" ],
                    textYOffset = control[ "textoffsety"]
                )
                self.win.addControl( current_control )
            # checkmark control
            elif ( control[ "type" ] == "checkmark" ):
                if ( control[ "info" ] ):
                    control[ "label" ][ 0 ] = xbmc.getInfoLabel( control[ "info" ][ 0 ] )
                current_control = xbmcgui.ControlCheckMark(
                    x = control[ "posx" ],
                    y = control[ "posy" ],
                    width = control[ "width" ],
                    height = control[ "height" ],
                    label = control[ "label" ][ 0 ],
                    font = control[ "font" ],
                    textColor = control[ "textcolor" ],
                    disabledColor = control[ "disabledcolor" ],
                    alignment = control[ "align" ],
                    focusTexture = control[ "texturecheckmark" ],
                    noFocusTexture = control[ "texturecheckmarknofocus" ],
                    checkWidth = control[ "markwidth" ],
                    checkHeight = control[ "markheight" ]
                )
                self.win.addControl( current_control )
            # textbox control
            elif ( control[ "type" ] == "textbox" ):
                if ( control[ "info" ] ):
                    control[ "label" ][ 0 ] = xbmc.getInfoLabel( control[ "info" ][ 0 ] )
                current_control = xbmcgui.ControlTextBox(
                    x = control[ "posx" ],
                    y = control[ "posy" ],
                    width = control[ "width" ],
                    height = control[ "height" ],
                    font = control[ "font" ],
                    textColor = control[ "textcolor" ]
                )
                self.win.addControl( current_control )
                if ( "label" in control ): current_control.setText( control[ "label" ][ 0 ] )
            #fadelabel control
            elif ( control[ "type" ] == "fadelabel" ):
                current_control = xbmcgui.ControlFadeLabel(
                    x = control[ "posx" ],
                    y = control[ "posy" ],
                    width = control[ "width" ],
                    height = control[ "height" ],
                    font = control[ "font" ],
                    textColor = control[ "textcolor" ],
                    #shadowColor = control[ "shadowcolor" ],
                    alignment = control[ "align" ]
                )
                self.win.addControl( current_control )
                if ( control[ "info" ] ):
                    for item in control[ "info" ]:
                        if ( item != "" ): current_control.addLabel( xbmc.getInfoLabel( item ) )
                if ( control[ "label" ] ):
                    for item in control[ "label" ]:
                        if ( item != "" ): current_control.addLabel( item )
            # list control
            elif ( control[ "type" ] == "list" or control[ "type" ] == "listcontrol" ):
                current_control = xbmcgui.ControlList(
                    x = control[ "posx" ],
                    y = control[ "posy" ],
                    width = control[ "width" ],
                    height = control[ "height" ],
                    font = control[ "font" ],
                    textColor = control[ "textcolor" ],
                    alignmentY = control[ "aligny" ],
                    buttonTexture = control[ "texturenofocus" ],
                    buttonFocusTexture = control[ "texturefocus" ],
                    selectedColor = control[ "selectedcolor" ],
                    imageWidth = control[ "itemwidth" ],
                    imageHeight = control[ "itemheight" ],
                    itemTextXOffset = control[ "textxoff" ],
                    itemTextYOffset = control[ "textyoff" ],
                    itemHeight = control[ "textureheight" ],
                    #shadowColor=control["shadowcolor"],
                    space = control[ "spacebetweenitems" ]
                )
                self.win.addControl( current_control )
                current_control.setPageControlVisible( not control[ "hidespinner" ] )
                control[ "special" ] = control[ "hidespinner" ]
                if ( control[ "label" ] ):
                    for cnt, item in enumerate( control[ "label" ] ):
                        if ( item != "" ): 
                            if ( cnt < len( control[ "label2" ] ) ): tmp = control[ "label2" ][ cnt ]
                            else: tmp = ""
                            if ( cnt < len( control[ "image" ] ) ): tmp2 = control[ "image" ][ cnt ]
                            elif control[ "image" ]: tmp2 = control[ "image" ][ len( control[ "image" ] ) - 1 ]
                            else: tmp2 = ""
                            list_item = xbmcgui.ListItem( item, tmp, tmp2, tmp2 )
                            current_control.addItem( list_item )
            
            self.win.controls[ key ] = {
                "id"			: control[ "id" ],
                "controlId"	: current_control.getId(),
                "control"		: current_control,
                "special"		: control[ "special" ],
                "visible"		: [ control[ "visible" ].lower(), control[ "allowhiddenfocus" ] ],
                "enable"		: control[ "enable" ].lower(),
                "animation"	: control[ "animation" ],
                "onclick"		: control[ "onclick" ],
                "onfocus"	: control[ "onfocus" ]
            }
            self.navigation[ control[ "id" ] ] = ( key, int( control[ "onup" ] ), int( control[ "ondown" ] ), int( control[ "onleft" ] ), int( control[ "onright" ] ) )
        except:
            succeeded = False
        return succeeded

    def _set_resolution( self ):
        """ sets the coordinate resolution compensating for widescreen modes """
        offset = 0
        # if current and skinned resolutions differ and skinned resolution is not
        # 1080i or 720p (they have no 4:3), calculate widescreen offset
        if ( ( not ( self.currentResolution == self.resolution ) ) and self.resolution > 1 ):
            # check if current resolution is 16x9
            if ( self.currentResolution == 0 or self.currentResolution % 2 ): iCur16x9 = 1
            else: iCur16x9 = 0
            # check if skinned resolution is 16x9
            if ( self.resolution % 2 ): i16x9 = 1
            else: i16x9 = 0
            # calculate widescreen offset
            offset = iCur16x9 - i16x9
        self.win.setCoordinateResolution( self.resolution + offset )

    def _parse_xml_file( self, xml_file, image_path ):
        """ parses and resolves an xml file and adds any missing tags """
        try:
            succeeded = True
            coord_posx = 0
            coord_posy = 0
            # load and parse skin.xml file
            skindoc = xml.dom.minidom.parse( xml_file )
            root = skindoc.documentElement
            # make sure this is a valid <window> xml file
            if ( not root or root.tagName != "window" ): raise
            # check for a <useincludes>tag
            includes_exist = False
            useIncludes = self.FirstChildElement( root, "useincludes" )
            if ( useIncludes and useIncludes.firstChild ): 
                overide = useIncludes.firstChild.nodeValue.lower()
                if ( overide == "1" or overide == "true" or overide == "yes" ):
                    includes_exist = self.LoadIncludes()
            #resolve xml file
            if ( includes_exist ): self.ResolveIncludes( root )
            # check for <defaultcontrol> and <coordinates> based system
            try:
                default = self.FirstChildElement( root, "defaultcontrol" )
                if ( default and default.firstChild ): self.defaultControl = int( default.firstChild.nodeValue )
                else: self.defaultControl = None
                coordinates = self.FirstChildElement( root, "coordinates" )
                if ( coordinates and coordinates.firstChild ):
                    systemBase = self.FirstChildElement( coordinates, "system" )
                    if ( systemBase and systemBase.firstChild ): 
                        system = int( systemBase.firstChild.nodeValue )
                        if ( system == 1 ):
                            posx = self.FirstChildElement( coordinates, "posx" )
                            if ( posx and posx.firstChild ): coord_posx = int( posx.firstChild.nodeValue )
                            posy = self.FirstChildElement( coordinates, "posy" )
                            if ( posy and posy.firstChild ): coord_posy = int( posy.firstChild.nodeValue )
            except: pass
            # check for a <resolution> tag and setCoordinateResolution()
            resolution = self.FirstChildElement( root, "resolution" )
            if ( resolution and resolution.firstChild ): self.resolution = self.resolutions.get( resolution.firstChild.nodeValue.lower(), 6 )
            self._set_resolution()
            # make sure <controls> block exists and resolve if necessary
            controls = self.FirstChildElement( root, "controls" )
            if ( controls and controls.firstChild ):
                if ( includes_exist ): self.ResolveIncludes( controls )
            else: raise
            # parse and resolve each <control>
            data = controls.getElementsByTagName( "control" )
            if ( not data ): raise
            for control in data:
            #control = self.FirstChildElement( controls, None )
            #while ( control ):
                control_type = None
                control_group = False
                if ( control.hasAttributes() ):
                    control_type = control.getAttribute( "type" )
                    control_id = control.getAttribute( "id" )
                #############################
                #group_posx = 0
                #group_posy = 0
                if ( control_type == "group" ): 
                    control_group = True
                    continue
                #############################

                if ( includes_exist ): self.ResolveIncludes( control, control_type )
                
                current_control = {}
                animation_tags = []
                label_tags = []
                label2_tags = []
                info_tags = []
                image_tags = []
                visible_tags = []
                enable_tags = []

                if ( control_type != "" ): current_control[ "type" ] = str( control_type )
                if ( control_id != "" ): current_control[ "id" ] = int( control_id )
                else: current_control[ "id" ] = 1
                
                # loop thru control and find all tags
                node = self.FirstChildElement( control, None )
                while ( node ):
                    # key node so save to the dictionary
                    if ( node.tagName.lower() == "label" ):
                        try:
                            v = node.firstChild.nodeValue
                            if ( self._ ):
                                ls = self._( int( v ) )
                            else: ls = xbmc.getLocalizedString( int( v ) )
                            if ( ls ): label_tags.append( ls )
                            else: raise
                        except:
                            if ( node.hasChildNodes() ): label_tags.append( node.firstChild.nodeValue )
                    elif ( node.tagName.lower() == "label2" ):
                        try: 
                            v = node.firstChild.nodeValue
                            if ( self._ ):
                                ls = self._( int( v ) )
                            else: ls = xbmc.getLocalizedString( int( v ) )
                            if ( ls ): label2_tags.append( ls )
                            else: raise
                        except:
                            if ( node.hasChildNodes() ): label2_tags.append( node.firstChild.nodeValue )
                    elif ( node.tagName.lower() == "info" ):
                        if ( node.hasChildNodes() ): info_tags.append( node.firstChild.nodeValue )
                    elif ( node.tagName.lower() == "image" ):
                        if ( node.hasChildNodes() ): image_tags.append( node.firstChild.nodeValue )
                    elif ( node.tagName.lower() == "visible" ):
                        if ( node.hasChildNodes() ):
                            if ( node.hasAttributes() ):
                                ah = node.getAttribute( "allowhiddenfocus" )
                            else: ah = "false"
                            current_control[ "allowhiddenfocus" ] = ah
                            visible_tags.append( node.firstChild.nodeValue )
                    elif ( node.tagName.lower() == "enable" ):
                        enable_tags.append( node.firstChild.nodeValue )
                    elif ( node.tagName.lower() == "animation" ):
                        if ( node.hasChildNodes() ): 
                            if ( node.hasAttributes() ):
                                condition = ""
                                if ( node.hasAttribute( "effect" ) ):
                                    condition += "effect=%s " % node.getAttribute( "effect" ).strip()
                                if ( node.hasAttribute( "time" ) ):
                                    condition += "time=%s " % node.getAttribute( "time" ).strip()
                                if ( node.hasAttribute( "delay" ) ):
                                    condition += "delay=%s " % node.getAttribute( "delay" ).strip()
                                if ( node.hasAttribute( "start" ) ):
                                    condition += "start=%s " % node.getAttribute( "start" ).strip()
                                if ( node.hasAttribute( "end" ) ):
                                    condition += "end=%s " % node.getAttribute( "end" ).strip()
                                if ( node.hasAttribute( "acceleration" ) ):
                                    condition += "acceleration=%s " % node.getAttribute( "acceleration" ).strip()
                                if ( node.hasAttribute( "center" ) ):
                                    condition += "center=%s " % node.getAttribute( "center" ).strip()
                                if ( node.hasAttribute( "condition" ) ):
                                    condition += "condition=%s " % node.getAttribute( "condition" ).strip()
                                if ( node.hasAttribute( "reversible" ) ):
                                    condition += "reversible=%s " % node.getAttribute( "reversible" ).strip()
                            animation_tags += [ ( node.firstChild.nodeValue, condition.strip().lower(), ) ]
                    elif (node.hasChildNodes()):
                        if (node.tagName.lower() == "type"): control_type = node.firstChild.nodeValue
                        if ( not node.tagName.lower() in current_control ):
                            current_control[ node.tagName.lower() ] = node.firstChild.nodeValue
                    node = self.NextSiblingElement( node, None )
                
                # setup the controls settings and defaults if necessary
                if ( control_type ):
                    # the following apply to all controls
                    if ( not "description" in current_control ): current_control[ "description" ] = control_type
                    if ( "posx" in current_control ): current_control[ "posx" ] = int( current_control[ "posx" ] ) + coord_posx
                    else: current_control[ "posx" ] = coord_posx
                    if ( "posy" in current_control ): current_control[ "posy" ] = int( current_control[ "posy" ] ) + coord_posy
                    else: current_control[ "posy" ] = coord_posy
                    if ( "width" in current_control ): current_control[ "width" ] = int( current_control[ "width" ] )
                    else: current_control[ "width" ] = 250
                    if ( "height" in current_control ): current_control[ "height" ] = int( current_control[ "height" ] )
                    else: current_control[ "height" ] = 100
                    if ( not "onup" in current_control ): current_control[ "onup" ] = current_control[ "id" ]
                    if ( not "ondown" in current_control ): current_control[ "ondown" ] = current_control[ "id" ]
                    if ( not "onleft" in current_control ): current_control[ "onleft" ] = current_control[ "id" ]
                    if ( not "onright" in current_control ): current_control[ "onright" ] = current_control[ "id" ]
                    if ( visible_tags ): current_control[ "visible" ] = self.GetConditionalVisibility( visible_tags )
                    else: current_control[ "visible" ] = "true"
                    if ( enable_tags ): current_control[ "enable" ] = self.GetConditionalVisibility( enable_tags )
                    else: current_control[ "enable" ] = "true"
                    if ( not "allowhiddenfocus" in current_control ): current_control[ "allowhiddenfocus" ] = "false"
                    current_control[ "allowhiddenfocus"] = current_control[ "allowhiddenfocus" ] in [ "true", "yes", "1" ]
                    if ( not "onclick" in current_control ): current_control[ "onclick" ] = ""
                    if ( not "onfocus" in current_control ): current_control[ "onfocus" ] = ""
                    if ( animation_tags ): current_control[ "animation" ] = animation_tags
                    else: current_control[ "animation" ] = ""

                    if ( control_type == "image" or control_type == "label" or control_type == "fadelabel" or control_type == "button" or control_type == "checkmark" or control_type == "textbox" ):
                        current_control[ "info" ] = info_tags
                        
                    if ( control_type == "label" or control_type == "fadelabel" or control_type == "button" or control_type == "checkmark" or control_type == "textbox" or control_type == "list" or control_type == "listcontrol" ):
                        if ( label_tags ): current_control[ "label" ] = label_tags
                        else: current_control[ "label" ] = [ "" ]
                        if ( not "shadowcolor" in current_control ): current_control[ "shadowcolor" ] = ""
                        if ( not "font" in current_control): current_control[ "font" ] = "font13"
                        if ( not "textcolor" in current_control ): current_control[ "textcolor" ] = "FFFFFFFF"

                    if ( control_type == "label" or control_type == "fadelabel" or control_type == "button" or control_type == "checkmark" or control_type == "list" or control_type == "listcontrol" ):
                        if (not "align" in current_control ): current_control[ "align" ] = "left"
                        try: current_control["align"] = [ "left", "right", "center" ].index( current_control["align"] )
                        except: current_control["align"] = 0
                        if ( not "aligny" in current_control ): current_control[ "aligny" ] = 0
                        current_control[ "aligny"] = ( current_control[ "aligny" ] in [ "center" ] ) * 4
                        current_control[ "align" ] += current_control[ "aligny" ]

                    if ( control_type == "label" or control_type == "button" or control_type == "checkmark" ):
                        if ( not "disabledcolor" in current_control ): current_control[ "disabledcolor" ] = "60FFFFFF"

                    if ( control_type == "label" or control_type == "button" ):
                        if ( not "angle" in current_control ): current_control[ "angle" ] = 0
                        else: current_control[ "angle" ] = int( current_control[ "angle" ] )

                    if ( control_type == "list" or control_type == "button" or control_type == "listcontrol" ):
                        if (not "texturefocus" in current_control ): current_control[ "texturefocus" ] = ""
                        elif ( current_control[ "texturefocus" ].startswith( "\\" ) ): current_control[ "texturefocus" ] = os.path.join( image_path, current_control[ "texturefocus" ][ 1 : ] )
                        if ( not "texturenofocus" in current_control ): current_control[ "texturenofocus" ] = ""
                        elif ( current_control[ "texturenofocus" ].startswith( "\\" ) ): current_control[ "texturenofocus" ] = os.path.join( image_path, current_control[ "texturenofocus" ][ 1 : ] )
                        
                    if ( control_type == "image" ):
                        try: current_control[ "aspectratio" ] = [ "stretch", "scale", "keep" ].index( current_control[ "aspectratio" ] )
                        except: current_control[ "aspectratio" ] = 0
                        if (not "colorkey" in current_control ): current_control[ "colorkey" ] = ""
                        if (not "colordiffuse" in current_control ): current_control[ "colordiffuse" ] = "0xFFFFFFFF"
                        if (not "texture" in current_control ): current_control[ "texture" ] = ""
                        elif ( current_control[ "texture" ].startswith( "\\" ) ): current_control[ "texture" ] = os.path.join( image_path, current_control[ "texture" ][ 1 : ] )

                    elif ( control_type == "label" ):
                        if ( not "haspath" in current_control ): current_control[ "haspath" ] = "false"
                        current_control[ "haspath"] = current_control[ "haspath" ] in [ "true", "yes", "1" ]
                        if ( "number" in current_control ): current_control[ "label" ][ 0 ] = [ current_control[ "number" ] ]

                    elif (control_type == "button"):
                        if ( not "textoffsetx" in current_control ): current_control[ "textoffsetx" ] = 0
                        else: current_control[ "textoffsetx" ] = int( current_control[ "textoffsetx" ] )
                        if ( not "textoffsety" in current_control ): current_control[ "textoffsety" ] = 0
                        else: current_control[ "textoffsety" ] = int( current_control[ "textoffsety" ] )
                        if ( not "focusedcolor" in current_control ): current_control[ "focusedcolor" ] = current_control[ "textcolor" ]

                    elif ( control_type == "checkmark" ):
                        if (not "texturecheckmark" in current_control ): current_control[ "texturecheckmark" ] = ""
                        elif ( current_control[ "texturecheckmark" ].startswith( "\\" ) ): current_control[ "texturecheckmark" ] = os.path.join( image_path, current_control[ "texturecheckmark" ][ 1 : ] )
                        if (not "texturecheckmarknofocus" in current_control ): current_control[ "texturecheckmarknofocus" ] = ""
                        elif ( current_control[ "texturecheckmarknofocus" ].startswith( "\\" ) ): current_control[ "texturecheckmarknofocus" ] = os.path.join( image_path, current_control[ "texturecheckmarknofocus" ][ 1 : ] )
                        if ( not "markwidth" in current_control ): current_control[ "markwidth" ] = 20
                        else: current_control[ "markwidth" ] = int( current_control[ "markwidth" ] )
                        if ( not "markheight" in current_control ): current_control[ "markheight" ] = 20
                        else: current_control[ "markheight" ] = int( current_control[ "markheight" ] )

                    elif ( control_type == "progress" ):
                        if ( not "texturebg" in current_control ): current_control[ "texturebg" ] = ""
                        elif ( current_control[ "texturebg" ].startswith( "\\" ) ): current_control[ "texturebg" ] = os.path.join( image_path, current_control[ "texturebg" ][ 1 : ] )
                        if ( not "lefttexture" in current_control ): current_control[ "lefttexture" ] = ""
                        elif ( current_control[ "lefttexture" ].startswith( "\\" ) ): current_control[ "lefttexture" ] = os.path.join( image_path, current_control[ "lefttexture" ][ 1 : ] )
                        if ( not "midtexture" in current_control ): current_control[ "midtexture" ] = ""
                        elif ( current_control[ "midtexture" ].startswith( "\\" ) ): current_control[ "midtexture" ] = os.path.join( image_path, current_control[ "midtexture" ][ 1 : ] )
                        if ( not "righttexture" in current_control ): current_control[ "righttexture" ] = ""
                        elif ( current_control[ "righttexture" ].startswith( "\\" ) ): current_control[ "righttexture" ] = os.path.join( image_path, current_control[ "righttexture" ][ 1 : ] )
                        if ( not "overlaytexture" in current_control ): current_control[ "overlaytexture" ] = ""
                        elif ( current_control[ "overlaytexture" ].startswith( "\\" ) ): current_control[ "overlaytexture" ] = os.path.join( image_path, current_control[ "overlaytexture" ][ 1 : ] )

                    elif ( control_type == "list" or control_type == "listcontrol" ):
                        current_control[ "label2" ] = label2_tags
                        current_control[ "image" ] = image_tags
                        if (not "selectedcolor" in current_control ): current_control[ "selectedcolor" ] = "FFFFFFFF"
                        if (not "itemwidth" in current_control ): current_control[ "itemwidth" ] = 20
                        else: current_control[ "itemwidth" ] = int( current_control[ "itemwidth" ] )
                        if (not "itemheight" in current_control ): current_control[ "itemheight" ] = 20
                        else: current_control[ "itemheight" ] = int( current_control[ "itemheight" ] )
                        if (not "textureheight" in current_control ): current_control[ "textureheight" ] = 20
                        else: current_control[ "textureheight" ] = int( current_control[ "textureheight" ] )
                        if (not "textxoff" in current_control ): current_control[ "textxoff" ] = 0
                        else: current_control[ "textxoff" ] = int( current_control[ "textxoff" ] )
                        if (not "textyoff" in current_control ): current_control[ "textyoff" ] = 0
                        else: current_control[ "textyoff" ] = int( current_control[ "textyoff" ] )
                        if (not "spacebetweenitems" in current_control ): current_control[ "spacebetweenitems" ] = 0
                        else: current_control[ "spacebetweenitems" ] = int( current_control[ "spacebetweenitems" ] )
                        if ( not "hidespinner" in current_control ): current_control[ "hidespinner" ] = "false"
                        current_control[ "hidespinner"] = current_control[ "hidespinner" ] in [ "true", "yes", "1" ]
                        if ( not "image" in current_control ): current_control[ "image" ] = [ " " ]
                        for img in range( len( current_control[ "image" ] ) ):
                            if ( current_control[ "image" ][ img ].startswith( "\\" ) ): current_control[ "image" ][ img ] = os.path.join( image_path, current_control[ "image" ][ img ][ 1 : ] )

                ok = self._add_control(current_control)
                if ( not ok ): raise
                ##control = self.NextSiblingElement( control, None )
        except:
            succeeded = False
        try: skindoc.unlink()
        except: pass
        return succeeded

    def _set_navigation( self ):
        """ sets control navigation """
        for item in self.navigation.values():
            if ( item[ 1 ] in self.navigation and self.navigation[ item[ 1 ] ][ 0 ] in self.win.controls ):
                self.win.controls[ item[ 0 ] ][ "control" ].controlUp( self.win.controls[ self.navigation[ item[ 1 ] ][ 0 ] ][ "control" ] )
            if ( item[ 2 ] in self.navigation and self.navigation[ item[ 2 ] ][ 0 ] in self.win.controls ):
                self.win.controls[ item[ 0 ] ][ "control" ].controlDown( self.win.controls[ self.navigation[ item[ 2 ] ][ 0 ] ][ "control" ] )
            if ( item[ 3 ] in self.navigation and self.navigation[ item[ 3 ] ][ 0 ] in self.win.controls ):
                self.win.controls[ item[ 0 ] ][ "control" ].controlLeft( self.win.controls[ self.navigation[ item[ 3 ] ][ 0 ] ][ "control" ] )
            if ( item[ 4 ] in self.navigation and self.navigation[ item[ 4 ] ][ 0 ] in self.win.controls ):
                self.win.controls[ item[ 0 ] ][ "control" ].controlRight( self.win.controls[ self.navigation[ item[ 4 ] ][ 0 ] ][ "control" ] )

    def _set_visibility_and_animations( self ):
        """ corrects control id's for some visible conditions and set's visible status """
        import re
        pattern = [ "control.hasfocus\(([0-9]+)\)", "control.isvisible\(([0-9]+)\)" ]
        rvalue = [ "control.hasfocus(##)", "control.isvisible(##)" ]
        for key in self.win.controls.keys():
            visible = self.win.controls[ key ][ "visible" ][ 0 ]
            enable = self.win.controls[ key ][ "enable" ]
            visibleChanged = False
            enableChanged = False
            animChanged = False
            final_anim = []
            for cnt in range( len( pattern ) ):
                items = re.findall( pattern[ cnt ], visible )
                visible = re.sub( pattern[ cnt ], rvalue[ cnt ], visible )
                # fix Control.HasFocus(id) visibility condition and Control.IsVisible(id) visibility condition
                for item in items:
                    visibleChanged = True
                    if ( int( item ) in self.navigation and self.navigation[ int( item ) ][ 0 ] in self.win.controls and self.win.controls[ self.navigation[ int( item ) ][ 0 ] ][ "id" ] == int( item ) ):
                        actualId = self.win.controls[ self.navigation[ int( item ) ][ 0 ] ][ "controlId" ]
                        visible = visible.replace( "##", str( actualId ), 1 )
                items = re.findall( pattern[ cnt ], enable )
                enable = re.sub( pattern[ cnt ], rvalue[ cnt ], enable )
                # fix Control.HasFocus(id) enabled condition and Control.IsVisible(id) enabled condition
                for item in items:
                    enableChanged = True
                    if ( int( item ) in self.navigation and self.navigation[ int( item ) ][ 0 ] in self.win.controls and self.win.controls[ self.navigation[ int( item ) ][ 0 ] ][ "id" ]==int( item ) ):
                        actualId = self.win.controls[ self.navigation[ int( item ) ][ 0 ] ][ "controlId" ]
                        enable = enable.replace( "##", str( actualId ), 1 )
                # fix Control.HasFocus(id) animation condition and Control.IsVisible(id) animation condition
                for acnt in range( len( self.win.controls[ key ][ "animation" ] ) ):
                    items = re.findall( pattern[ cnt ], self.win.controls[ key ][ "animation" ][ acnt ][ 1 ] )
                    anim_attr = re.sub( pattern[ cnt ], rvalue[ cnt ], self.win.controls[ key ][ "animation" ][ acnt ][ 1 ] )
                    for item in items:
                        animChanged = True
                        if ( int( item ) in self.navigation and self.navigation[ int( item ) ][ 0 ] in self.win.controls and self.win.controls[ self.navigation[ int( item ) ][ 0 ] ][ "id" ]==int( item ) ):
                            actualId = self.win.controls[ self.navigation[ int( item ) ][ 0 ] ][ "controlId" ]
                            anim_attr = anim_attr.replace( "##", str( actualId ), 1 )
                    if ( items ): final_anim += [ ( self.win.controls[ key ][ "animation" ][ acnt ][ 0 ], anim_attr, ) ]
            
            # set the controls new visible condition
            if ( visibleChanged ): self.win.controls[ key ][ "visible" ][ 0 ] = visible
            # set the controls new visible condition
            if ( enableChanged ): self.win.controls[ key ][ "enable" ] = enable
            # set the controls new animation condition
            if ( animChanged ): 
                self.win.controls[ key ][ "animation" ] = final_anim
            # set the controls initial visibility
            if ( visible != "false" and visible != "true" ):
                self.win.controls[ key ][ "control" ].setVisibleCondition( visible, self.win.controls[ key ][ "visible" ][ 1 ] )
            else:
                self.win.controls[ key ][ "control" ].setVisible( xbmc.getCondVisibility( visible ) )
            if ( enable != "false" and enable != "true" ):
                self.win.controls[ key ][ "control" ].setEnableCondition( enable )
            else:
                self.win.controls[ key ][ "control" ].setEnabled( xbmc.getCondVisibility( enable ) )
            # set the controls animations
            if ( self.win.controls[ key ][ "animation" ] ): self.win.controls[ key ][ "control" ].setAnimations( self.win.controls[ key ][ "animation" ] )
            
    def GetConditionalVisibility( self, conditions ):
        if ( len( conditions ) == 0 ): return "true"
        if ( len( conditions ) == 1 ): return conditions[ 0 ]
        else:
            # multiple conditions should be anded together
            conditionString = "["
            for i in range( len( conditions ) - 1 ):
                conditionString += conditions[ i ] + "] + ["
            conditionString += conditions[ len( conditions ) - 1 ] + "]"
        return conditionString

    def GetSkinPath(self, filename):
        default = 6
        defaultwide = 7
        try:
            fname = os.path.join("Q:\\skin", xbmc.getSkinDir(), "skin.xml")
            skindoc = xml.dom.minidom.parse(fname)
            root = skindoc.documentElement
            if (not root or root.tagName != "skin"): raise
            strDefault = self.FirstChildElement(root, "defaultresolution")
            if (strDefault and strDefault.firstChild): default = self.resolutions.get(strDefault.firstChild.nodeValue.lower(), default)
            strDefaultWide = self.FirstChildElement(root, "defaultresolutionwide")
            if (strDefaultWide and strDefaultWide.firstChild): defaultwide = self.resolutions.get(strDefaultWide.firstChild.nodeValue.lower(), defaultwide)
            skindoc.unlink()
        except: pass
        fname = os.path.join("Q:\\skin", xbmc.getSkinDir(), self.resPath[self.currentResolution], filename)
        if (os.path.exists(fname)):
            if (filename == "includes.xml"): self.resolution = self.currentResolution
            return fname
        # if we're in 1080i mode, try 720p next
        if (self.currentResolution == 0):
            fname = os.path.join("Q:\\skin", xbmc.getSkinDir(), self.resPath[1], filename)
            if (os.path.exists(fname)):
                if (filename == "includes.xml"): self.resolution = 1
                return fname
        # that failed - drop to the default widescreen resolution if we're in a widemode
        if (self.currentResolution % 2):
            fname = os.path.join("Q:\\skin", xbmc.getSkinDir(), self.resPath[defaultwide], filename)
            if (os.path.exists(fname)):
                if (filename == "includes.xml"): self.resolution = defaultwide
                return fname
        # that failed - drop to the default resolution
        fname = os.path.join("Q:\\skin", xbmc.getSkinDir(), self.resPath[default], filename)
        if (os.path.exists(fname)):
            if (filename == "includes.xml"): self.resolution = default
            return fname
        else:
            return None

    def FirstChildElement(self, root, value = "include"):
        node = root.firstChild
        while (node):
            if (node and node.nodeType == 1):
                if (node.tagName == value or not value): return node
            node = node.nextSibling
        return None

    def NextSiblingElement(self, node, value = "include"):
        while (node):
            node = node.nextSibling
            if (node and node.nodeType == 1):
                if (node.tagName == value or not value): return node
        return None

    def ClearIncludes( self ):
        self.m_includes = {}
        self.m_defaults = {}
        self.m_files = []

    def HasIncludeFile( self, file ):
        if ( file in self.m_files ): 
            return True
        else: return False

    def LoadIncludes( self, includeFile = "includes.xml" ):
        # check to see if we already have this loaded
        if ( self.HasIncludeFile( includeFile ) ):
            return True
        # get the includes.xml file location if it exists
        includeFile = self.GetSkinPath( str( includeFile ) )
        # load and parse includes.xml file
        try: 
            self.include_doc.append( xml.dom.minidom.parse( includeFile ) )
        except:
            return False
        # success, load the tags
        if ( self.LoadIncludesFromXML( self.include_doc[-1].documentElement ) ):
            self.m_files.append( includeFile )
            return True
        else: 
            return False

    def LoadIncludesFromXML( self, root ):
        if ( not root or root.tagName != "includes" ):
            return False
        node = self.FirstChildElement( root )
        while ( node ):
            if ( node.getAttribute( "name" ) and node.firstChild ):
                # key node so save to the dictionary
                tagName = node.getAttribute( "name" )
                self.m_includes[ tagName ] = node
            elif ( node.getAttribute( "file" ) ):
                # load this file in as well
                includeFile = node.getAttribute( "file" )
                result = self.LoadIncludes( includeFile )
            node = self.NextSiblingElement( node )

        # now defaults
        node = self.FirstChildElement( root, "default" )
        while ( node ):
            if ( node.getAttribute( "type" ) and node.firstChild ):
                tagName = node.getAttribute( "type" )
                self.m_defaults[ tagName ] = node
            node = self.NextSiblingElement( node, "default" )
        return True

    def ResolveIncludes( self, node, type = None ):
        # we have a node, find any <include file="fileName">tagName</include> tags and replace
        # recursively with their real includes
        if ( not node ): return

        # First add the defaults if this is for a control
        if ( type ):
            # resolve defaults
            it = self.m_defaults.get( type, None )
            if ( it != None ):
                element = it.cloneNode( True )
                tag = self.FirstChildElement( element , None )
                while ( tag != None ):
                    result = node.appendChild( tag.cloneNode( True ) )
                    tag = self.NextSiblingElement( tag, None )
        
        include = self.FirstChildElement( node, "include" )
        while ( include and include.firstChild ):
            # have an include tag - grab it's tag name and replace it with the real tag contents
            file = include.getAttribute( "file" )
            if ( file ):
                # we need to load this include from the alternative file
                result = self.LoadIncludes( file )
            tagName = include.firstChild.nodeValue
            it = self.m_includes.get( tagName, None )
            if ( it != None ):
                # found the tag(s) to include - let's replace it
                element = it.cloneNode( True )
                tag = self.FirstChildElement( element, None )
                for tag in element.childNodes:
                    # we insert before the <include> element to keep the correct
                    # order (we render in the order given in the xml file)
                    if ( tag.nodeType == 1 ): result = node.insertBefore( tag, include )
                # remove the <include>tagName</include> element
                result = node.removeChild( include )
                include.unlink()
                include = self.FirstChildElement( node, "include" )
            else:
                # invalid include
                include = self.NextSiblingElement( node, "include" )
