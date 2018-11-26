# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ViewsRefresher
                                 A QGIS plugin
 This plugin caluclates the required cable capacities in a FTTH project
                              -------------------
        begin                : 2018-05-31
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Mohannad ADHAM / Axians
        email                : mohannad.adm@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import PyQt4
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import psycopg2
import psycopg2.extras
import xml.etree.ElementTree as ET
import xlrd
import xlwt
import os.path
import os
import subprocess
import osgeo.ogr  
import processing



from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from views_refresher_dialog import ViewsRefresherDialog
import os.path


class ViewsRefresher:
    global conn, cursor
    # global isMultistring
    isMultistring = False
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgisInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'ViewsRefresher_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&ViewsRefresher')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'ViewsRefresher')
        self.toolbar.setObjectName(u'ViewsRefresher')

        # Create the dialog (after translation) and keep reference
        self.dlg = ViewsRefresherDialog()

#"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""" lsitner autojmatic dimensioning """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
        
        #creation du bouton "connexion BD"
        Button_connexion_BD= self.dlg.findChild(QPushButton,"pushButton_connexion")
        QObject.connect(Button_connexion_BD, SIGNAL("clicked()"),self.connectToDb)
        #mot de passe en etoile
        self.dlg.lineEdit_Password.setEchoMode(QLineEdit.Password)

        # # Connect the button "pushButton_verifier_topologie"
        Button_mettre_a_jour_cable = self.dlg.findChild(QPushButton, "pushButton_mettre_a_jour_cable")
        QObject.connect(Button_mettre_a_jour_cable, SIGNAL("clicked()"), self.refresh_views)

        # Connect the button "pushButton_select"
        Button_select_all = self.dlg.findChild(QPushButton, "pushButton_select")
        QObject.connect(Button_select_all, SIGNAL("clicked()"), self.select_all)

        # Connect the button "pushButton_deselect"
        Button_deselect_all = self.dlg.findChild(QPushButton, "pushButton_deselect")
        QObject.connect(Button_deselect_all, SIGNAL("clicked()"), self.deselect_all)





#"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""" Listner migration P vers T """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('ViewsRefresher', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
    

        # Create the dialog (after translation) and keep reference
        # self.dlg = ViewsRefresherDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/ViewsRefresher/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Refreshes control views'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Automatic Dimensioning'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.GetParamBD(self.dlg.lineEdit_BD, self.dlg.lineEdit_Password, self.dlg.lineEdit_User, self.dlg.lineEdit_Host, self.dlg.Schema_grace)
        self.dlg.show()

        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed

        # Activate the connection button 
        self.dlg.findChild(QPushButton, "pushButton_connexion").setEnabled(True)
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass




    def fenetreMessage(self,typeMessage,titre,message):
        ''' Displays a message box to the user '''
        try:
            msg = QMessageBox()
            # msg.setIcon(typeMessage)
            msg.setWindowTitle(titre)
            msg.setText(str(message))
            msg.setWindowFlags(PyQt4.QtCore.Qt.WindowStaysOnTopHint)
            msg.exec_()
        except Exception as e:
            self.fenetreMessage(QMessageBox.Warning,"Erreur_fenetreMessage",str(e))

            
    def GetParamBD(self, dbname, password, user, serveur, sche):
        ''' Looks for the information to connect to the DB within the QGIS project '''

        try:
            path_absolute = QgsProject.instance().fileName()
            
            if path_absolute != "":
                
                
                tree = ET.parse(path_absolute)
                sche.setText("gracethd")
                root = tree.getroot()

                listeModify = []
                
                for source in root.iter('datasource'):
                    
                    if "dbname" in source.text : 
                        modify = str(source.text)
                        listeModify = modify.split("sslmode")
                        if len(listeModify) > 1:
                            
                            break

                if len(listeModify) > 1 :
                    
                    infosConnexion = listeModify[0].replace("'","")
                    infosConnexion = infosConnexion.split(" ")
                    for info in infosConnexion:
                        inf = info.split("=")
                        if inf[0] == "dbname":
                            dbname.setText(inf[1])
                        if inf[0] == "password":
                            password.setText(inf[1])
                        if inf[0] == "user":
                            user.setText(inf[1])
                        if inf[0] == "host":
                            serveur.setText(inf[1])
                    schemainfo = listeModify[1].replace("'","")
                    schemainfo = schemainfo.split(" ")
                    for sch in schemainfo:
                        sh = sch.split("=")
                        if sh[0] == "table":
                            schema = sh[1].split(".")
                            # sche.setText(schema[0].replace('"',''))
                            sche.setText("gracethd")
        except Exception as e:
            self.fenetreMessage(QMessageBox.Warning,"Erreur_GetParamBD",str(e))
            # print str(e)


    def remplir_menu_deroulant_reference(self, combobox, rq_sql, DefValChamp):
        ''' Fill a combobox with a list of table names '''

        listVal = []
        combobox.clear()
        result = self.executerRequette(rq_sql, True)
        for elm in result:
            listVal.append(elm[0])
        combobox.addItems(listVal)
        try:
            combobox.setCurrentIndex(combobox.findText(DefValChamp))
        except Exception as e:
            self.fenetreMessage(QMessageBox.Warning,"Erreur_remplir_menu_deroulant_reference",str(e))




    def executerRequette(self, Requette, boool):
        ''' Sends a query to execute it within the database and receives the results '''

        global conn
        
        try:
            cursor = conn.cursor()
            cursor.execute(Requette)
            conn.commit()
            if boool:
                result = cursor.fetchall()
                cursor.close()
                try :
                    if len(result)>0:
                        return result
                except:
                    return None
            else:
                cursor.close()
            
        except Exception as e:
            self.fenetreMessage(QMessageBox.Warning,"Erreur_executerRequette",str(e))
            cursor.close()
            # self.connectToDb()




    def connectToDb(self):
        ''' Connects to the DB, enables the comboboxes and the buttons, and fill the comboboxes with the names of the control views '''
        global conn
        Host = self.dlg.lineEdit_Host.text()
        DBname = self.dlg.lineEdit_BD.text()
        User = self.dlg.lineEdit_User.text()
        Password = self.dlg.lineEdit_Password.text()
        Schema = self.dlg.Schema_grace.text()
        Schema_prod = self.dlg.Schema_prod.text()

        
        conn_string = "host='"+Host+"' dbname='"+DBname+"' user='"+User+"' password='"+Password+"'"

        try:
            conn = psycopg2.connect(conn_string)
            #recuperer tout les schemas
            shema_list=[]
            cursor = conn.cursor()
            sql =  "select schema_name from information_schema.schemata "
            cursor.execute(sql)
            result=cursor.fetchall()
            for elm in result:
                shema_list.append(elm[0].encode("utf8"))
            #passer au deuxieme onglet si la connexion est etablit et si le schema existe
            if Schema in shema_list:
                # Do Something
                # Enable the Comboboxes and Buttons

                self.dlg.findChild(QComboBox,"comboBox_adductabilite").setEnabled(True)
                self.dlg.findChild(QComboBox,"comboBox_cheminement").setEnabled(True)
                self.dlg.findChild(QComboBox,"comboBox_noeud").setEnabled(True)
                self.dlg.findChild(QComboBox, "comboBox_ebp").setEnabled(True)
                self.dlg.findChild(QComboBox, "comboBox_sitetech").setEnabled(True)
                self.dlg.findChild(QComboBox, "comboBox_baie").setEnabled(True)
                self.dlg.findChild(QComboBox, "comboBox_ptech").setEnabled(True)
                self.dlg.findChild(QComboBox, "comboBox_conduite").setEnabled(True)
                self.dlg.findChild(QComboBox, "comboBox_zpbo").setEnabled(True)
                self.dlg.findChild(QComboBox, "comboBox_cable").setEnabled(True)
                self.dlg.findChild(QComboBox, "comboBox_love").setEnabled(True)
                self.dlg.findChild(QComboBox, "comboBox_zdep").setEnabled(True)
                self.dlg.findChild(QComboBox, "comboBox_adresse").setEnabled(True)
                self.dlg.findChild(QComboBox, "comboBox_suf").setEnabled(True)
                self.dlg.findChild(QComboBox, "comboBox_cond_chem").setEnabled(True)
                self.dlg.findChild(QComboBox, "comboBox_cab_cond").setEnabled(True)


                self.dlg.findChild(QPushButton, "pushButton_mettre_a_jour_cable").setEnabled(True)


                # Disable connection button
                self.dlg.findChild(QPushButton, "pushButton_connexion").setEnabled(False)

                # Search for the names of the required tables in each schema in gracethd
                self.remplir_menu_deroulant_reference(self.dlg.comboBox_noeud, ("SELECT oid::regclass::text FROM pg_class WHERE  relkind = 'm';"), 'prod.vs_controles_noeud')
                self.remplir_menu_deroulant_reference(self.dlg.comboBox_adductabilite, ("SELECT oid::regclass::text FROM pg_class WHERE  relkind = 'm';"), 'prod.vs_controles_adductabilite')
                self.remplir_menu_deroulant_reference(self.dlg.comboBox_cheminement, ("SELECT oid::regclass::text FROM pg_class WHERE  relkind = 'm';"), 'prod.vs_controles_cheminement')
                self.remplir_menu_deroulant_reference(self.dlg.comboBox_ebp, ("SELECT oid::regclass::text FROM pg_class WHERE  relkind = 'm';"), 'prod.vs_controles_ebp')
                self.remplir_menu_deroulant_reference(self.dlg.comboBox_sitetech, ("SELECT oid::regclass::text FROM pg_class WHERE  relkind = 'm';"), 'prod.vs_controles_sitetech')
                self.remplir_menu_deroulant_reference(self.dlg.comboBox_baie, ("SELECT oid::regclass::text FROM pg_class WHERE  relkind = 'm';"), 'prod.vs_controles_baie')
                self.remplir_menu_deroulant_reference(self.dlg.comboBox_ptech, ("SELECT oid::regclass::text FROM pg_class WHERE  relkind = 'm';"), 'prod.vs_controles_ptech')
                self.remplir_menu_deroulant_reference(self.dlg.comboBox_conduite, ("SELECT oid::regclass::text FROM pg_class WHERE  relkind = 'm';"), 'prod.vs_controles_conduite')
                self.remplir_menu_deroulant_reference(self.dlg.comboBox_zpbo, ("SELECT oid::regclass::text FROM pg_class WHERE  relkind = 'm';"), 'prod.vs_controles_zpbo')
                self.remplir_menu_deroulant_reference(self.dlg.comboBox_cable, ("SELECT oid::regclass::text FROM pg_class WHERE  relkind = 'm';"), 'prod.vs_controles_cable')
                self.remplir_menu_deroulant_reference(self.dlg.comboBox_love, ("SELECT oid::regclass::text FROM pg_class WHERE  relkind = 'm';"), 'prod.vs_controles_love')
                self.remplir_menu_deroulant_reference(self.dlg.comboBox_zdep, ("SELECT oid::regclass::text FROM pg_class WHERE  relkind = 'm';"), 'prod.vs_controles_zdep')
                self.remplir_menu_deroulant_reference(self.dlg.comboBox_adresse, ("SELECT oid::regclass::text FROM pg_class WHERE  relkind = 'm';"), 'prod.vs_controles_adresse')
                self.remplir_menu_deroulant_reference(self.dlg.comboBox_suf, ("SELECT oid::regclass::text FROM pg_class WHERE  relkind = 'm';"), 'prod.vs_controles_suf')
                self.remplir_menu_deroulant_reference(self.dlg.comboBox_cond_chem, ("SELECT oid::regclass::text FROM pg_class WHERE  relkind = 'm';"), 'prod.vs_controles_cond_chem')
                self.remplir_menu_deroulant_reference(self.dlg.comboBox_cab_cond, ("SELECT oid::regclass::text FROM pg_class WHERE  relkind = 'm';"), 'prod.vs_controles_cab_cond')
            

                print "Schema found"
            else:
                print "Schema not found"
        except Exception as e:
                pass

        layers_names = ""
        for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
            layers_names += lyr.name() + "\n"


    def select_all(self):
        ''' Select all the checkbox objects within the dialog '''
        try:
            for box in self.dlg.findChildren(QCheckBox):
                box.setChecked(True)

        except Exception as e:
            self.fenetreMessage(QMessageBox.Warning, "Error", str(e))


    def deselect_all(self):
        ''' Deselect all the checkbox objects within the dialog '''
        try:
            for box in self.dlg.findChildren(QCheckBox):
                box.setChecked(False)

        except Exception as e:
            self.fenetreMessage(QMessageBox.Warning, "Error", str(e))


    def refresh_views(self):
        ''' Refresh the selected views within the database '''

        # Get the names of the views from the comboboxes
        noeud = self.dlg.comboBox_noeud.currentText()
        adductabilite = self.dlg.comboBox_adductabilite.currentText()
        adresse = self.dlg.comboBox_adresse.currentText()
        sitetech = self.dlg.comboBox_sitetech.currentText()
        baie = self.dlg.comboBox_baie.currentText()
        ptech = self.dlg.comboBox_ptech.currentText()
        cheminement = self.dlg.comboBox_cheminement.currentText()
        conduite = self.dlg.comboBox_conduite.currentText()
        ebp = self.dlg.comboBox_ebp.currentText()
        zpbo = self.dlg.comboBox_zpbo.currentText()
        cable = self.dlg.comboBox_cable.currentText()
        love = self.dlg.comboBox_love.currentText()
        zdep = self.dlg.comboBox_zdep.currentText()
        suf = self.dlg.comboBox_suf.currentText()
        cond_chem = self.dlg.comboBox_cond_chem.currentText()
        cab_cond = self.dlg.comboBox_cab_cond.currentText()


        # --------------------------- Refresh the Views -------------------------------------------------
        # create a dictionary of the views and the the corresponding subgroups
        views_groups = {adductabilite : "Reference", noeud : "Reference", suf : "Reference", adresse : "Reference", sitetech : "Hebergement", baie : "Hebergement", ptech : "Infrastructure d'acceuil",
            cheminement : "Infrastructure d'acceuil", conduite : "Infrastructure d'acceuil", cond_chem : "Infrastructure d'acceuil", cable : "Infrastructure optique", ebp : "Infrastructure optique",
            cab_cond : "Infrastructure optique", love : "Infrastructure optique", zpbo : "Zones d'expolitation", zdep : "Zones d'expolitation"}

        # create the query string that refreshes the selected materialized views
        query = ""
        for view in views_groups.keys():
            try:
                if self.dlg.findChild(QCheckBox, "checkBox_" + view.split("es_")[1]).isChecked():
                    query += "REFRESH MATERIALIZED VIEW " + view + "; \n" 
                    # self.fenetreMessage(QMessageBox, 'Info', 'The view is added')
            except Exception as e:
                self.fenetreMessage(QMessageBox.Warning, "Error", str(e))

        # execute the query
        self.executerRequette(query, False)

        # ---------------------------- Refresh the layers within the project -------------------------
        # create a list of the names of the subgroups to verify whether these subgroups already exist or not
        root = QgsProject.instance().layerTreeRoot()
        self.root_group = root.findGroup(u"Controle Ingénierie et structure BDD")

        try:
            subgroups_names = []
            for child in self.root_group.children():
                # if child.name().find("vs_") == -1:
                # verify if the child is a group
                if isinstance(child, QgsLayerTreeGroup):
                    subgroups_names.append(child.name())
                    # self.fenetreMessage(QMessageBox.Warning, "info", type(child))

        except Exception as e:
            self.fenetreMessage(QMessageBox.Warning, "Error", str(e))

        # -------------------- first case : the subgroups don't exist yet --------------------------------
        if len(subgroups_names) < 5:
            # get the names of the subgroups to create
            groups_names = set(val for val in views_groups.values())
            # create the subgroups
            try:
                self.add_groups(groups_names)
            except Exception as e:
                self.fenetreMessage(QMessageBox.Warning, "error", str(e))

            # copy the layers from the root group to the subgroups
            for view in views_groups.keys():
                try:
                    self.move_layer(view.split(".")[1], views_groups[view])
                except Exception as e:
                    self.fenetreMessage(QMessageBox.Warning, "error", str(e))


            # ----------------------------- End of the first case ---------------------------------------

        # -------------------- second case : the subgroups already exist --------------------------------
        # In the second case we need only to refresh the style of the layers within the subgroups.

        # -------------------------------- End of the second case ---------------------------------------

        # style the new layers in the subgroups
        # Add the style to only spatial layers ----------------
        try:
            for view in views_groups.keys():
                # self.fenetreMessage(QMessageBox, "info", "within the loop")
                if view not in (baie, love, suf, cond_chem, cab_cond) and self.dlg.findChild(QCheckBox, "checkBox_" + view.split("es_")[1]).isChecked():
                    layer = QgsMapLayerRegistry.instance().mapLayersByName(view.split(".")[1])[0]
                    self.add_style(layer)
        except Exception as e:
            self.fenetreMessage(QMessageBox.Warning, "error", str(e))

        self.fenetreMessage(QMessageBox, "info", "The selected views are updated!")





    def add_style(self, layer):
        """ Style a qgis layer by classifying the features using the 'intitule' field and giving the classes random colors """
        
        from random import randrange

        # get unique values 
        fni = layer.fieldNameIndex('intitule')
        unique_values = layer.dataProvider().uniqueValues(fni)

        # define categories
        categories = []
        for unique_value in unique_values:
            # initialize the default symbol for this geometry type
            symbol = QgsSymbolV2.defaultSymbol(layer.geometryType())

            # configure a symbol layer
            layer_style = {}
            layer_style['color'] = '%d, %d, %d' % (randrange(0,256), randrange(0,256), randrange(0,256))

            # Define the style of the point layers
            if layer.wkbType()==QGis.WKBPoint:
                layer_style['color'] = '%d, %d, %d' % (randrange(0,256), randrange(0,256), randrange(0,256))
                layer_style['size'] = '2'
                symbol_layer = QgsSimpleMarkerSymbolLayerV2.create(layer_style)
                symbol_layer.setOutlineWidth(0)

            # Define the style of the lineString layers
            if layer.wkbType()==QGis.WKBLineString:
                # print 'Layer is a line layer'
                layer_style['width_border'] = '0.46'
                layer_style['size'] = '0.46'
                symbol_layer = QgsSimpleFillSymbolLayerV2.create(layer_style)

            # Define the style of the polygon layers
            if layer.wkbType()==QGis.WKBPolygon or layer.wkbType()==QGis.WKBMultiPolygon:
                layer_style['width_border'] = '0.46'
                layer_style['color_border'] = 'black'
                symbol_layer = QgsSimpleFillSymbolLayerV2.create(layer_style)



            symbol_layer = QgsSimpleFillSymbolLayerV2.create(layer_style)

            # Replace default symbol layer with the configured one
            if symbol_layer is not None:
                symbol.changeSymbolLayer(0, symbol_layer)

            # Create renderer object
            category = QgsRendererCategoryV2(unique_value, symbol, str(unique_value))
            # Entry for the list of category items
            categories.append(category)

        # Create renderer object
        renderer = QgsCategorizedSymbolRendererV2('intitule', categories)

        # Assign the created renderer to the layer
        if renderer is not None:
            layer.setRendererV2(renderer)

        # layer.rendererChanged.connect(self.changed_renderer)
        layer.triggerRepaint()



    def add_groups(self, groups_names):
        ''' Create group of layers in the QGIS project based on the names provided
        groups_names: a set of string elements representing the names of the groups to be created '''

        for group_name in groups_names:
            self.root_group.addGroup(group_name)


    def move_layer(self, view, group_name):
        ''' Move the specified layer to the specified group of layers in the QGIS project
        view : (string) the name of the layer to be moved 
        group_name : (string) the name of the group to which the layer will be moved '''

        # find the subgroup
        group = self.root_group.findGroup(group_name)
        # find the layer within the root_group
        layer = QgsMapLayerRegistry.instance().mapLayersByName(view)[0]
        # get the id of the layer
        layer_id = layer.id()
        # copy the layer to the subgroup
        group.addLayer(layer)
        # remove the layer (legend entry) from the root_group
        # get the child node by id
        child_node = self.root_group.findLayer(layer_id)

        try:
            # remove the childeNode from the root group
            self.root_group.removeChildNode(child_node)
        except Exception as e:
            self.fenetreMessage(QMessageBox.Warning, "error", str(e))



