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
        # Button_verifier_topologie = self.dlg.findChild(QPushButton, "pushButton_verifier_topologie")
        # QObject.connect(Button_verifier_topologie, SIGNAL("clicked()"), self.verify_topology)
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
            text=self.tr(u'Performs Cable Dimensioning'),
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



                # self.dlg.findChild(QPushButton, "pushButton_verifier_topologie").setEnabled(True)
                # self.dlg.findChild(QPushButton, "pushButton_orientation").setEnabled(True)
                # self.dlg.findChild(QPushButton, "pushButton_fibres_utiles").setEnabled(True)
                # self.dlg.findChild(QPushButton, "pushButton_dimensions").setEnabled(True)
                # self.dlg.findChild(QPushButton, "pushButton_mettre_a_jour_chemin").setEnabled(True)
                self.dlg.findChild(QPushButton, "pushButton_mettre_a_jour_cable").setEnabled(True)

                # self.dlg.findChild(QPushButton, "pushButton_mettre_a_jour_chemin")
                # self.dlg.findChild(QPushButton, "pushButton_mettre_a_jour_cable").setEnabled(True)
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
            



                # self.fenetreMessage(QMessageBox.Warning,"Query for zs_refpm", "SELECT zs_refpm FROM " + self.dlg.Schema_grace.text() + ".t_zsro;")
                # result = self.executerRequette("SELECT zs_refpm FROM " + self.dlg.Schema_grace.text() + ".t_zsro;", True)
                # for elm in result:
                #     print elm[0]
                #     self.fenetreMessage(QMessageBox.Warning,"result of query", elm[0])

                # 3 - ZSRO (zs_refpm)
                self.remplir_menu_deroulant_reference(self.dlg.comboBox_zs_refpm, ("SELECT zs_refpm as refpm FROM " + self.dlg.Schema_prod.text() + ".p_zsro ;"), 'PMT_26325_FO01')

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




    def add_pg_layer(self, schema, table_name):
        # Create a data source URI
        uri = QgsDataSourceURI()

        # set host name, port, database name, username and password
        uri.setConnection(self.dlg.lineEdit_Host.text(), "5432", self.dlg.lineEdit_BD.text(), self.dlg.lineEdit_User.text(), self.dlg.lineEdit_Password.text())

        # set database schema, table name, geometry column and optionally subset (WHERE clause)
        # uri.setDataSource('temp', 'cheminement_al01', "geom")
        uri.setDataSource(schema, table_name, "geom")

        vlayer = QgsVectorLayer(uri.uri(False), table_name, "postgres")

        # if not vlayer.isValid():
        #     self.fenetreMessage(QMessageBox, "Error", "The layer %s is not valid" % vlayer.name())
        #     return


        # check first if the layer is already added to the map
        layer_names = [layer.name() for layer in QgsMapLayerRegistry.instance().mapLayers().values()]
        if table_name not in layer_names:
            # Add the vector layer to the map
            QgsMapLayerRegistry.instance().addMapLayers([vlayer])
            self.fenetreMessage(QMessageBox, "Success", "Layer %s is loaded" % vlayer.name())

        else :
            self.fenetreMessage(QMessageBox, "Success", "Layer %s already exists but it has been updated" % vlayer.name())