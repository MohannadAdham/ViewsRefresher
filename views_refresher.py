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



        # # Connect the button "pushButton_orientation"
        # Button_orientation = self.dlg.findChild(QPushButton, "pushButton_orientation")
        # QObject.connect(Button_orientation, SIGNAL("clicked()"), self.calcul_orientation)

        # # Connect the button "pushButton_fibres_utiles"
        # Button_fibres_utiles = self.dlg.findChild(QPushButton, "pushButton_fibres_utiles")
        # QObject.connect(Button_fibres_utiles, SIGNAL("clicked()"), self.calcul_fibres_utiles)

        # # Connect the button "pushButton_"
        # Button_dimensios = self.dlg.findChild(QPushButton, "pushButton_dimensions")
        # QObject.connect(Button_dimensios, SIGNAL("clicked()"), self.calcul_cable_dimensions)

        # # Connect the butoon "pushButton_mettre_a_jour_chemin"
        # Button_mettre_a_jour_chemin = self.dlg.findChild(QPushButton, "pushButton_mettre_a_jour_chemin")
        # QObject.connect(Button_mettre_a_jour_chemin, SIGNAL("clicked()"), self.update_p_cheminement)

        # # Connect the button "pushButton_mettre_a_jour_cable"
        # Button_mettre_a_jour_cable = self.dlg.findChild(QPushButton, "pushButton_mettre_a_jour_cable")
        # QObject.connect(Button_mettre_a_jour_cable, SIGNAL("clicked()"), self.update_p_cable)



        # self.fenetreMessage(QMessageBox, "info", "within add_group")


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
        # self.fenetreMessage(QMessageBox, "info", "inside remplir_menu_deroulant_reference")
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

            # if "MultiLineString" in str(e):
                # self.fenetreMessage(QMessageBox, "info", "You have a cable with MultilineString geometry (cable id = " + str(self.findMultiLineString()) + ")")
                # self.isMultistring = True
                # self.findMultiLineString()

    # def findMultiLineString(self):
    #     zs_refpm = self.dlg.comboBox_zs_refpm.currentText()

    #     query = "SELECT id FROM temp.cable_" + zs_refpm.split("_")[2].lower()  + " WHERE ST_GeometryType(geom) = 'ST_MultiLineString'"
    #     result = self.executerRequette(query,  True)
    #     # return result[0][0]
    #     if len(result) > 0:
    #         message2 = "You have " + str(len(result)) + "  cables with MultilineString geometry at id = " + str(result[0][0])
    #         for i in range(1, len(result)):
    #             if i < len(result) - 1:
    #                 message2 += ", " + str(result[i][0])
    #             else :
    #                 message2 += " and " + str(result[i][0])
    #     message2 += "\n Please consult the table cable_multilinestring_" + zs_refpm.split("_")[2].lower()
    #     self.fenetreMessage(QMessageBox, "Warning!", message2)

    #     query2 = """ DROP TABLE IF EXISTS temp.cable_multilinestring_""" + zs_refpm.split("_")[2].lower()  + """;

    #             CREATE TABLE temp.cable_multilinestring_""" + zs_refpm.split("_")[2].lower()  + """ AS 
    #             SELECT id, geom FROM temp.cable_""" + zs_refpm.split("_")[2].lower()  + """ WHERE ST_GeometryType(geom) = 'ST_MultiLineString';

    #      """
    #     self.executerRequette(query2,  False)
    #     self.add_pg_layer("temp", "cable_multilinestring_" + zs_refpm.split("_")[2].lower())




    def connectToDb(self):
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

                # Search for the names of the required tables in each schema
                # 1 - in gracethd
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
            



                # self.fenetreMessage(QMessageBox.Warning,"Query for zs_refpm", "SELECT zs_refpm FROM " + self.dlg.Schema_grace.text() + ".t_zsro;")
                # result = self.executerRequette("SELECT zs_refpm FROM " + self.dlg.Schema_grace.text() + ".t_zsro;", True)
                # for elm in result:
                #     print elm[0]
                #     self.fenetreMessage(QMessageBox.Warning,"result of query", elm[0])

                # 3 - ZSRO (zs_refpm)
                # self.remplir_menu_deroulant_reference(self.dlg.comboBox_zs_refpm, ("SELECT zs_refpm as refpm FROM " + self.dlg.Schema_prod.text() + ".p_zsro ;"), 'PMT_26325_FO01')

                # print "SELECT zs_refpm FROM " + self.dlg.Schema_grace.text() + ".t_zsro;"


                print "Schema found"
                # self.dlg2.findChild(QPushButton,"pushButton_controle_avt_migration").setEnabled(True)
            else:
                # self.dlg2.findChild(QPushButton,"pushButton_controle_avt_migration").setEnabled(False)
                # self.dlg2.findChild(QPushButton,"pushButton_migration").setEnabled(False)
                print "Schema not found"
        except Exception as e:
                pass
            #desactiver les bouton
            # self.dlg2.findChild(QPushButton,"pushButton_controle_avt_migration").setEnabled(False)
            # self.dlg2.findChild(QPushButton,"pushButton_migration").setEnabled(False)
            #         self.fenetreMessage(QMessageBox.Warning,"Erreur_connectToDb",str(e))
            #         cursor.close()

        layers_names = ""
        for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
            layers_names += lyr.name() + "\n"

        self.fenetreMessage(QMessageBox, "info", "layers names : " + layers_names)



    # def add_pg_layer(self, schema, table_name):
    #     self.fenetreMessage(QMessageBox.Warning, "info", "within add_pg_layer")
    #     # Create a data source URI
    #     uri = QgsDataSourceURI()

    #     # set host name, port, database name, username and password
    #     uri.setConnection(self.dlg.lineEdit_Host.text(), "5432", self.dlg.lineEdit_BD.text(), self.dlg.lineEdit_User.text(), self.dlg.lineEdit_Password.text())

    #     # set database schema, table name, geometry column and optionally subset (WHERE clause)
    #     # uri.setDataSource('temp', 'cheminement_al01', "geom")
    #     uri.setDataSource(schema, table_name, "geom")

    #     vlayer = QgsVectorLayer(uri.uri(False), table_name, "postgres")
    #     try:
    #         self.fenetreMessage(QMessageBox, "info", vlayer.name())
    #     except Exception as e:
    #         self.fenetreMessage(QMessageBox.Warning, "error", str(e))

    #     # if not vlayer.isValid():
    #     #     self.fenetreMessage(QMessageBox, "Error", "The layer %s is not valid" % vlayer.name())
    #     #     return


    #     try:
    #         self.second_group.addLayer(vlayer)
    #     except Exception as e:
    #         self.fenetreMessage(QMessageBox.Warning, "error", str(e))


    #     # check first if the layer is already added to the map
    #     layer_names = [layer.name() for layer in QgsMapLayerRegistry.instance().mapLayers().values()]
    #     if table_name not in layer_names:
    #         # Add the vector layer to the map
    #         QgsMapLayerRegistry.instance().addMapLayers([vlayer])
    #         self.fenetreMessage(QMessageBox, "Success", "Layer %s is loaded" % vlayer.name())

    #     else :
    #         self.fenetreMessage(QMessageBox, "Success", "Layer %s already exists but it has been updated" % vlayer.name())
            



    # def add_pg_table(self, schema, table_name):
    #     self.fenetreMessage(QMessageBox.Warning, "info", "within add_pg_table")
    #     # Create a data source URI
    #     uri = QgsDataSourceURI()

    #     # set host name, port, database name, username and password
    #     uri.setConnection(self.dlg.lineEdit_Host.text(), "5432", self.dlg.lineEdit_BD.text(), self.dlg.lineEdit_User.text(), self.dlg.lineEdit_Password.text())

    #     # set database schema, table name, geometry column and optionally subset (WHERE clause)
    #     # uri.setDataSource('temp', 'cheminement_al01', "geom")
    #     uri.setDataSource(schema, table_name, None)

    #     vlayer = QgsVectorLayer(uri.uri(False), table_name, "postgres")


    #     try:
    #         self.fenetreMessage(QMessageBox, "info", vlayer.name())
    #     except Exception as e:
    #         self.fenetreMessage(QMessageBox.Warning, "error", str(e))

    #     # if not vlayer.isValid():
    #     #     self.fenetreMessage(QMessageBox, "Error", "The layer %s is not valid" % vlayer.name())
    #     #     return

    #     try:
    #         self.second_group.addLayer(vlayer)
    #     except Exception as e:
    #         self.fenetreMessage(QMessageBox.Warning, "error", str(e))



    #     # check first if the layer is already added to the map
    #     layer_names = [layer.name() for layer in QgsMapLayerRegistry.instance().mapLayers().values()]
    #     if table_name not in layer_names:
    #         # Add the vector layer to the map
    #         QgsMapLayerRegistry.instance().addMapLayers([vlayer])
    #         # self.fenetreMessage(QMessageBox, "Success", "Layer %s is loaded" % vlayer.name())

    #     else :
    #         # self.fenetreMessage(QMessageBox, "Success", "Layer %s already exists but it has been updated" % vlayer.name())
    #         pass



    def refresh_views(self):
        self.fenetreMessage(QMessageBox, "info", "within refresh_views")
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
        # create a dictionary of the views and the corresponding subgroups
        views_groups = {adductabilite : "Reference", noeud : "Reference", suf : "Reference", adresse : "Reference", sitetech : "Hebergement", baie : "Hebergement", ptech : "Infrastructure d'acceuil",
            cheminement : "Infrastructure d'acceuil", conduite : "Infrastructure d'acceuil", cond_chem : "Infrastructure d'acceuil", cable : "Infrastructure optique", ebp : "Infrastructure optique",
            cab_cond : "Infrastructure optique", love : "Infrastructure optique", zpbo : "Zones d'expolitation", zdep : "Zones d'expolitation"}
        self.fenetreMessage(QMessageBox, "info", str(views_groups))
        # create the query string
        query = ""
        for view in views_groups.keys():
            query += "REFRESH MATERIALIZED VIEW " + view + "; \n"  

        # execute the query
        # self.executerRequette(query, False)

        # ---------------------------- Refresh the layers within the project -------------------------
        # create a list of the names of the subgroups to verify whether these subgroups already exist or not
        root = QgsProject.instance().layerTreeRoot()
        self.root_group = root.findGroup(u"Controle Ingénierie et structure BDD")

        self.fenetreMessage(QMessageBox, "info", self.root_group.name())

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

        self.fenetreMessage(QMessageBox, "info", "after creating subgroups_names")
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
        for view in views_groups.keys():
            if view not in (baie, lovesuf, cond_chem, cab_cond):
                # self.fenetreMessage(QMessageBox.Warning, "info", "before add_pg_layer " + "prod." + view.split(".")[1])
                layer = QgsMapLayerRegistry.instance().mapLayersByName(view.split(".")[1])[0]
                self.add_style(layer)





        #     # first_group_name = "Livrables"
        #     # first_group = root.findGroup(first_group_name)
        #     second_group_name = u"Controle Ingénierie et structure BDD"
        #     self.second_group = first_group.findGroup(second_group_name)


        #     self.fenetreMessage(QMessageBox, "info", "before sleep")
        #     # import time
        #     # time.sleep(5000)
        #     self.fenetreMessage(QMessageBox, "info", "after sleep")

        #     # views_list = [adductabilite, noeud, suf, adresse, sitetech, baie, ptech, cheminement, conduite, cond_chem, cable, cab_cond, love, ebp, zpbo, zdep]

        #     views_groups = {adductabilite : "Reference", noeud : "Reference", adresse : "Reference", sitetech : "Hebergement", baie : "Hebergement", ptech : "Infrastructure d'acceuil",
        #     cheminement : "Infrastructure d'acceuil", conduite : "Infrastructure d'acceuil", cable : "Infrastructure optique", ebp : "Infrastructure optique",
        #     love : "Infrastructure optique", zpbo : "Zones d'expolitation", zdep : "Zones d'expolitation"}

        #     groups_names = set(val for val in views_groups.values())

        #     self.add_groups(groups_names)

        #     self.fenetreMessage(QMessageBox, "info", "After add_groups")

        # except Exception as e:
        #     self.fenetreMessage(QMessageBox.Warning, "error", str(e))



        # try:
        #     query = ""
        #     for view in views_groups.keys():
        #         query += "REFRESH MATERIALIZED VIEW " + view + "; \n"       


        # except Exception as e:
        #     self.fenetreMessage(QMessageBox.Warning, "error", str(e))


        # # self.executerRequette(query, False)



        # try:
        #     # self.fenetreMessage(QMessageBox.Warning, "info", "before adding layers")
        #     for view in views_groups.keys():
        #         # self.fenetreMessage(QMessageBox, "info", view.split(".")[1])

        #         # else:
        #         #     self.fenetreMessage(QMessageBox.Warning, "info", "before add_pg_table " + "prod." + view.split(".")[1])

        #         #     self.fenetreMessage(QMessageBox.Warning, "info", "after add_pg_table")

        #         # ---------------- move the layers to the subgroups ---------------------
        #         self.fenetreMessage(QMessageBox, "info", "before move_layer")
        #         try:
        #             self.move_layer(view.split(".")[1], views_groups[view])
        #         except Exception as e:
        #             self.fenetreMessage(QMessageBox.Warning, "error", str(e))


        #         # ------------------- Add the style to only spatial layers ----------------
        #         if view not in (baie, love):
        #             # self.fenetreMessage(QMessageBox.Warning, "info", "before add_pg_layer " + "prod." + view.split(".")[1])
        #             self.fenetreMessage(QMessageBox.Warning, "info", "after add_pg_layer")
        #             layer = QgsMapLayerRegistry.instance().mapLayersByName(view.split(".")[1])[0]
        #             # exclude non-spatial tables
        #             self.add_style(layer)
        #         # ------------------------------------------------------------------------

        #     # self.fenetreMessage(QMessageBox, "Success", query)


        # except Exception as e:
        #     self.fenetreMessage(QMessageBox.Warning, "error", str(e))

        # self.fenetreMessage(QMessageBox.Warning, "info", "before deleting children")

        # # ---------- remove all children within the root group ---------------
        # # self.second_group.removeAllChildren()
        # try:
        #     for child in self.second_group.children():
        #         if child.name().find("vs_") == 0:
        #             self.second_group.removeChildNode(child)
        # except Exception as e:
        #     self.fenetreMessage(QMessageBox.Warning, "error", str(e))  


        # self.fenetreMessage(QMessageBox.Warning, "info", "after deleting children")     
        #     # else:
        #     #     for child2 in child.children():
        #     #         child.removeChildNode(child2)


    


    def add_style(self, layer):
        from random import randrange
        # self.fenetreMessage(QMessageBox, 'info', 'within add style for layer ' + layer.name())

        # Get the active layer (must be a vector layer)
        # layer = qgis.utils.iface.activeLayer()

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

            if layer.wkbType()==QGis.WKBPoint:
                # print 'Layer is a pojnt layer'
                layer_style['color'] = '%d, %d, %d' % (randrange(240,256), randrange(0,20), randrange(0,16))
                layer_style['size'] = '2'
                symbol_layer = QgsSimpleMarkerSymbolLayerV2.create(layer_style)
                symbol_layer.setOutlineWidth(0)


            if layer.wkbType()==QGis.WKBLineString:
                # print 'Layer is a line layer'
                layer_style['width_border'] = '0.46'
                layer_style['size'] = '0.46'
                # layer_style['color_border'] = 'red'
                symbol_layer = QgsSimpleFillSymbolLayerV2.create(layer_style)


            if layer.wkbType()==QGis.WKBPolygon or layer.wkbType()==QGis.WKBMultiPolygon:
                # print 'Layer is a polygon layer'
                layer_style['width_border'] = '0.46'
                layer_style['color_border'] = 'black'
                symbol_layer = QgsSimpleFillSymbolLayerV2.create(layer_style)



            symbol_layer = QgsSimpleFillSymbolLayerV2.create(layer_style)

            # replace default symbol layer with the configured one
            if symbol_layer is not None:
                symbol.changeSymbolLayer(0, symbol_layer)

            # create renderer object
            category = QgsRendererCategoryV2(unique_value, symbol, str(unique_value))
            # entry for the list of category items
            categories.append(category)

        # create renderer object
        renderer = QgsCategorizedSymbolRendererV2('intitule', categories)

        # assign the created renderer to the layer
        if renderer is not None:
            layer.setRendererV2(renderer)

        # layer.rendererChanged.connect(self.changed_renderer)
        layer.triggerRepaint()



    # def changed_renderer(self):
    #     self.fenetreMessage(QMessageBox, 'info', 'the renderer is changed')

    def add_groups(self, groups_names):
        # self.fenetreMessage(QMessageBox, "info", "within add_group")


        for group_name in groups_names:
            self.root_group.addGroup(group_name)
            # self.fenetreMessage(QMessageBox, "info", "The group " + group_name + " is added")




    def move_layer(self, view, group_name):
        # self.fenetreMessage(QMessageBox, "info", "within move_layer")
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
        # self.fenetreMessage(QMessageBox, "info", "group : " + self.root_group.name() + ", view : " + view)
        # self.fenetreMessage(QMessageBox, "info", child_node.name())
        try:
            # remove the childeNode from the root group
            self.root_group.removeChildNode(child_node)
        except Exception as e:
            self.fenetreMessage(QMessageBox.Warning, "error", str(e))

        # QgsMapLayerRegistry.instance().removeMapLayer(layer_id)


