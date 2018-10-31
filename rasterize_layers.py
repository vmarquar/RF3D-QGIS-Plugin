"""
RockyFor3D Export Module by V. Marquart
"""
import os
from osgeo import gdal
from osgeo import ogr
from osgeo import gdalconst

# functions
def getExtentFromDEM(dem_path):
    """
    takes a raster file and returns a dict with the key:
    - geo_transform,
    - x_res,
    - y_res,
    - x_max
    access object like this: dem_data['geo_transform']
    """
    data = gdal.Open(dem_path, gdalconst.GA_ReadOnly)
    geo_transform = data.GetGeoTransform()

    x_min = geo_transform[0]
    y_max = geo_transform[3]
    x_max = x_min + geo_transform[1] * data.RasterXSize
    y_min = y_max + geo_transform[5] * data.RasterYSize
    x_res = data.RasterXSize
    y_res = data.RasterYSize
    pixel_width = geo_transform[1]
    #(geo_transform[0], geo_transform[1], geo_transform[2], geo_transform[3], geo_transform[4], geo_transform[5])
    # return {'geo_transform':(x_min, pixel_width, 0, y_min, 0, -pixel_width), 'x_res':x_res, 'y_res':y_res, 'x_max':x_max}
    return {'geo_transform':(geo_transform[0], geo_transform[1], geo_transform[2], geo_transform[3], geo_transform[4], geo_transform[5]), 'x_res':x_res, 'y_res':y_res, 'x_max':x_max}



def createRasterizedAscii(input_path_or_ds, output_path, output_file_name, attribute_field_name, geotransform, x_res, y_res, GDT_DataType={'d1': gdal.GDT_Float32}, keeptif=True, NoData_value=-9999):
    """ Creates Ascii and optionally Tif files from vector data input """
    #1) Check if input is dataset or path to a file. If its a valid file path -> open the file using ogr
    if isinstance(input_path_or_ds, ogr.DataSource):
        input_data = input_path_or_ds

    elif os.path.isfile(input_path_or_ds):
        # open file using ogr
        input_data = ogr.Open(input_path_or_ds)

    else:
        print("The provided input_path_or_ds is not a valid file path or can't be openend with ogr.")
        return

    # create needed instances of input vector layer
    input_layer = input_data.GetLayer()

    #2) create a temporary tif output file with the dem extent
    input_filename_without_ext = output_file_name
    #input_path = os.path.split(vector_data.name)[0]
    tif_path = os.path.join(output_path, input_filename_without_ext+'.tif')
    tif = gdal.GetDriverByName('GTiff').Create(tif_path, x_res, y_res, 1, GDT_DataType)
    tif.SetGeoTransform(geotransform) # funktioniert das!?!
    band = tif.GetRasterBand(1)
    band.SetNoDataValue(NoData_value)
    band.FlushCache()

    #3) Rasterize the input vector data into the tif File
    gdal.RasterizeLayer(tif, [1], input_layer, options=["ATTRIBUTE="+attribute_field_name])

    #4) CreateCopy the RasterizedLayer tif File
    ascii_path = os.path.join(output_path, input_filename_without_ext+'.asc')
    print("Creating Ascii file at:"+ascii_path)
    ascii_grid = gdal.GetDriverByName('AAIGrid').CreateCopy(ascii_path, tif, options=["FORCE_CELLSIZE=YES"])
    



    #5 Closing ds and writing values to file
    ascii_grid = None
    tif = None
    if not isinstance(input_path_or_ds, ogr.DataSource):
        input_data = None

    if not keeptif:
        os.remove(tif_path)

    return ascii_path

def createDEMCopy(input_path, output_path):
    """ Creates a copy of a input raster file and exports it as a Ascii Grid File """
    try:
        inputDEM = gdal.Open(input_path)
        output = gdal.GetDriverByName('AAIGrid').CreateCopy(output_path,inputDEM,options=["FORCE_CELLSIZE=YES"])
        output = None
        return output_path
    except Error :
        print(Error)
        return None



def rasterizeMultiFieldVectorLayer(vector_filepath, output_ascii_dir, dem_transform_data, exlude_list=['id'], GDT_DataType={'d1':gdal.GDT_Float32, 'd2':gdal.GDT_Float32, 'd3':gdal.GDT_Float32}, keeptif=True, NoData_value=-9999):
    """
    This function loops through all individual attribute fields of a vector layer and rasterizes them into a tif and ascii output.
    You can save the files automatically to subfolders by using following naming convention of the attribute field:
    filename_subfolder --> e.g. 'd1_block1' will be saved as: 'output_directory/block1/d1.asc'
    """

    #1) Open layer and instanciate layer
    vector_data = ogr.Open(vector_filepath)
    vector_layer = vector_data.GetLayer()
    layer_definition = vector_layer.GetLayerDefn()

    #2) Create schema of filenames and optionally of subfolders
    schema = []

    #3) loop through input vector layer and create output schema with raster name and output subfolder
    for n in range(layer_definition.GetFieldCount()):
        field_definition = layer_definition.GetFieldDefn(n)
        if field_definition.name in ['net_number', 'net_energy', 'net_height']:
            schema.append({"filename": field_definition.name, "folder": None, "attribute_field": field_definition.name})
        else:
            try:
                schema.append({"filename": field_definition.name.split('_')[0], "folder": field_definition.name.split('_')[1], "attribute_field": field_definition.name})

            # Exception for handling a simple configuration layer with fields containing only d1, d2, d3 -> not subfolder will be created
            except IndexError as indexE:
                print("IndexError in getting the field attribute schema with following error:")
                print(indexE)
                print("We will not use any subfolders...")
                schema.append({"filename": field_definition.name.split('_')[0], "folder": None, "attribute_field": field_definition.name})

    #4) Loop through folders and save each attribute field as Raster layer
    created_rasters = []
    for raster in schema:
        
        # exception for rocdensity -> rockdensity
        if raster['attribute_field'] == 'rocdensity':
            raster['filename'] = 'rockdensity'

        if raster['attribute_field'] not in exlude_list:
            subfolder = ''

            # 1) create a subfolder if it does not yet exist and if folder is not None
            if raster['folder'] is not None:
                subfolder = os.path.join(output_ascii_dir, raster['folder'])

                if os.path.isdir(subfolder):
                    print(subfolder+" already exists...")

                else:
                    print("Created new subfolder:\n"+subfolder)
                    os.makedirs(subfolder)

            # 2) rasterizeLayer the filename into the specific subfolder or into the main folder if folder == None
            if subfolder != '':
                ascii_path = createRasterizedAscii(vector_data, os.path.join(output_ascii_dir, subfolder), raster['filename'], raster['attribute_field'], dem_transform_data['geo_transform'], dem_transform_data['x_res'], dem_transform_data['y_res'], GDT_DataType[raster['filename']], keeptif, NoData_value)
                created_rasters.append(ascii_path)
            else:
                ascii_path = createRasterizedAscii(vector_data, output_ascii_dir, raster['filename'], raster['attribute_field'], dem_transform_data['geo_transform'], dem_transform_data['x_res'], dem_transform_data['y_res'], GDT_DataType[raster['filename']], keeptif, NoData_value)
                created_rasters.append(ascii_path)

    return created_rasters 
# Function end




# MAIN

#get extent / geotransformation matrix from input dem (including size, cell size, extent and coord system)
dem = '/Users/Valentin/Library/Mobile Documents/3L68KQB4HG~com~readdle~CommonDocuments/Documents/Ingenieur-und-Hydro/4 MASTERARBEIT/2 GIS/2 Feldvorbereitung und DGM/Raster/dgm_gesamt_1m_oGeb_9999.asc'
output_dir = '/Users/Valentin/Library/Mobile Documents/3L68KQB4HG~com~readdle~CommonDocuments/Documents/Ingenieur-und-Hydro/4 MASTERARBEIT/2 GIS/4 Rockyfor3D Inputdaten/output_data'

dem_data = getExtentFromDEM(dem)

#d1_d2_d3
# as d1_block1, d2_block1, d3_block1, ...
d1_d2_d3 = '/Users/Valentin/Library/Mobile Documents/3L68KQB4HG~com~readdle~CommonDocuments/Documents/Ingenieur-und-Hydro/4 MASTERARBEIT/2 GIS/4 Rockyfor3D Inputdaten/input_data/d1_d2_d3.shp'

output = rasterizeMultiFieldVectorLayer(d1_d2_d3, output_dir, dem_data, GDT_DataType={'d1':gdal.GDT_Float32, 'd2':gdal.GDT_Float32, 'd3':gdal.GDT_Float32, 'blshape': gdal.GDT_CInt32})

print(output)


# gdal.Rasterize(dst_name, blshape, options=rasterizeOptions)
# rasterizeOptions = gdal.RasterizeOptions(format='AAIGrid',outputType=gdal.GDT_Int32, creationOptions=["FORCE_CELLSIZE=YES"], outputSRS="EPSG:31468", width=457, height=397, xRes=0.999389934354, yRes=0.999389934354, noData=-9999, attribute="blshape")


# RasterizeOptions(options=[], format=None, outputType=0, creationOptions=None, noData=None, initValues=None, outputBounds=None, outputSRS=None, width=None, height=None, xRes=None, yRes=None, targetAlignedPixels=False, bands=None, inverse=False, allTouched=False, burnValues=None, attribute=None, useZ=False, layers=None, SQLStatement=None, SQLDialect=None, where=None, callback=None, callback_data=None)
#     Create a RasterizeOptions() object that can be passed to gdal.Rasterize()
#     Keyword arguments are :
#       options --- can be be an array of strings, a string or let empty and filled from other keywords.

#       format --- output format ("GTiff", etc...)
#       outputType --- output type (gdal.GDT_Byte, etc...)
#       creationOptions --- list of creation options
#       outputBounds --- assigned output bounds: [minx, miny, maxx, maxy]
#       outputSRS --- assigned output SRS
#       width --- width of the output raster in pixel
#       height --- height of the output raster in pixel
#       xRes, yRes --- output resolution in target SRS
#       targetAlignedPixels --- whether to force output bounds to be multiple of output resolution
#       noData --- nodata value
#       initValues --- Value or list of values to pre-initialize the output image bands with.  However, it is not marked as the nodata value in the output file.  If only one value is given, the same value is used in all the bands.
#       bands --- list of output bands to burn values into
#       inverse --- whether to invert rasterization, i.e. burn the fixed burn value, or the burn value associated  with the first feature into all parts of the image not inside the provided a polygon.
#       allTouched -- whether to enable the ALL_TOUCHED rasterization option so that all pixels touched by lines or polygons will be updated, not just those on the line render path, or whose center point is within the polygon.
#       burnValues -- list of fixed values to burn into each band for all objects. Excusive with attribute.
#       attribute --- identifies an attribute field on the features to be used for a burn-in value. The value will be burned into all output bands. Excusive with burnValues.
#       useZ --- whether to indicate that a burn value should be extracted from the "Z" values of the feature. These values are added to the burn value given by burnValues or attribute if provided. As of now, only points and lines are drawn in 3D.
#       layers --- list of layers from the datasource that will be used for input features.
#       SQLStatement --- SQL statement to apply to the source dataset
#       SQLDialect --- SQL dialect ('OGRSQL', 'SQLITE', ...)
#       where --- WHERE clause to apply to source layer(s)
#       callback --- callback method
#       callback_data --- user data for callback

