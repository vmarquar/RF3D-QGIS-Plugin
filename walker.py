import os
start_path = "/Volumes/ga84laz/MASTERARBEIT/Mod_PC/RockyFor3D/rf3d_obere-Berme_W_S_1m_bl123"
style_directory = "/Users/Valentin/Library/Mobile Documents/3L68KQB4HG~com~readdle~CommonDocuments/Documents/Ingenieur-und-Hydro/4 MASTERARBEIT/2 GIS/4 Rockyfor3D Inputdaten/styles"
import_files = ['E_95CI.asc', 'Ph_95CI.asc', 'Nr_deposited.asc', 'Reach_probability.asc']
crs_number = 31468
# or import_files = 'all'
root = QgsProject.instance().layerTreeRoot()

#1) Create a group to insert the imported layers into
#from time import localtime, strftime
#rf3d_group = root.insertGroup(0, 'RockyFor3D Import from '+strftime("%Y-%m-%d %H:%M", localtime()))
rf3d_group = root.insertGroup(0, os.path.basename(start_path))

#2) switch off crs prompt after import
s = QSettings()
oldValidation = s.value( "/Projections/defaultBehavior" )
s.setValue( "/Projections/defaultBehavior", "useGlobal" )

#3) walk through the directory recursevily and 3-1) create groups and subgroups, 3-2) import files, 3-3)style them 
try:
    for root, dirs, files in os.walk(start_path, topdown=True):
        for _dir in dirs:

            # only import *sims* directories!
            if "sims-" in _dir:
                relative_path = os.path.relpath(os.path.join(root, _dir),start_path)
                relatives = relative_path.split(os.sep)

                target_path = os.path.join(root, _dir)
                print("Creating following groups and subgroups: {}".format(relatives))
                print("Loading selected files from this folder: {}".format(target_path))
                
                # 3-1) create groups and subgroups
                group = rf3d_group
                for relative in relatives:
                    # create a group for each item
                    group = group.addGroup(relative)

                _files = [f for f in os.listdir(target_path) if os.path.isfile(os.path.join(target_path, f))]
                for _file in _files:
                    # filter for ascii files only:
                    if ".asc" == os.path.splitext(_file)[1]:
                        print("Should the following file be added: {}".format(_file))
                        # only import files in import_files
                        # 3-2) import files into last subgroup

                        if _file in import_files:
                            try:
                                filepath = os.path.join(target_path, _file)
                                rName = os.path.splitext(os.path.basename(filepath))[0]
                                rLayer = QgsRasterLayer(filepath, rName)
                                rLayer.setCrs( QgsCoordinateReferenceSystem(crs_number, QgsCoordinateReferenceSystem.EpsgCrsId) )
                                group.insertChildNode(0,QgsLayerTreeLayer(rLayer))

                                #3-3) style the imported files accordingly
                                rLayer.loadNamedStyle(os.path.join(style_directory, rName+'.qml')
                                rLayer.triggerRepaint()
                                iface.layerTreeView().refreshLayerSymbology( rLayer.id() )
                            except Error as e:
                                print(e)
                                print("Could not add the following File: {}".format(_file))




                        
except Error as e:
    print(e)


#re-enable the crs prompt
s.setValue( "/Projections/defaultBehavior", oldValidation )