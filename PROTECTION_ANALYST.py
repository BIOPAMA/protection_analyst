"""
Model exported as python.
Name : wdpa_country_processing
Group : wdpa
With QGIS : 32203
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsCoordinateReferenceSystem
from qgis.core import QgsProperty
import processing


class Wdpa_country_processing(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('inputcountries', 'Input Countries ', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('inputcountries (2)', 'Input EEZ', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('inputwdpapoints', 'Input wdpa points', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('inputwdpapolygons', 'Input wdpa polygons', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Acp_stats', 'ACP_STATS', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Region_stats', 'REGION_STATS', optional=True, type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Country_stats', 'COUNTRY_STATS', optional=True, type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(134, model_feedback)
        results = {}
        outputs = {}

        # Reproject layer eez
        alg_params = {
            'INPUT': parameters['inputwdpapolygons'],
            'OPERATION': '',
            'TARGET_CRS': QgsCoordinateReferenceSystem('ESRI:54009'),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ReprojectLayerEez'] = processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Extract by expression EEZ2
        alg_params = {
            'EXPRESSION': '"STATUS"   !=  \'Not Reported\'  \r\nor  "STATUS"   !=  \'Proposed\'  or  "DESIG_ENG" != \'UNESCO-MAB Biosphere Reserve\'  or "REP_AREA" >0',
            'INPUT': parameters['inputwdpapoints'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpressionEez2'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Reproject countries
        alg_params = {
            'INPUT': parameters['inputcountries'],
            'TARGET_CRS': QgsCoordinateReferenceSystem('ESRI:54009'),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ReprojectCountries'] = processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Centroids
        alg_params = {
            'ALL_PARTS': False,
            'INPUT': parameters['inputwdpapolygons'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Centroids'] = processing.run('native:centroids', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Reproject countries eez
        alg_params = {
            'INPUT': parameters['inputcountries (2)'],
            'OPERATION': '',
            'TARGET_CRS': QgsCoordinateReferenceSystem('ESRI:54009'),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ReprojectCountriesEez'] = processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Reproject layer
        alg_params = {
            'INPUT': parameters['inputwdpapolygons'],
            'TARGET_CRS': QgsCoordinateReferenceSystem('ESRI:54009'),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ReprojectLayer'] = processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Fix geometries PA POINT
        alg_params = {
            'INPUT': outputs['ReprojectLayerEez']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixGeometriesPaPoint'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Extract by expression
        alg_params = {
            'EXPRESSION': '"STATUS"   !=  \'Not Reported\'  \r\nor  "STATUS"   !=  \'Proposed\'  or  "DESIG_ENG" != \'UNESCO-MAB Biosphere Reserve\'  or "REP_AREA" >0',
            'INPUT': parameters['inputwdpapoints'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpression'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Merge vector layers
        alg_params = {
            'CRS': None,
            'LAYERS': [outputs['Centroids']['OUTPUT'],parameters['inputwdpapoints']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MergeVectorLayers'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Reproject points EEZ3
        alg_params = {
            'INPUT': outputs['ExtractByExpressionEez2']['OUTPUT'],
            'OPERATION': '',
            'TARGET_CRS': QgsCoordinateReferenceSystem('ESRI:54009'),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ReprojectPointsEez3'] = processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # NUMBER_OF_PAS_ TOTAL
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['ISO3'],
            'INPUT': outputs['MergeVectorLayers']['OUTPUT'],
            'VALUES_FIELD_NAME': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Number_of_pas_Total'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # better eez
        alg_params = {
            'INPUT': outputs['ReprojectCountriesEez']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['BetterEez'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # Fix geometries PA POLY
        alg_params = {
            'INPUT': outputs['ReprojectLayer']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixGeometriesPaPoly'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # Extract by attribute COSTAL
        alg_params = {
            'FIELD': 'MARINE',
            'INPUT': outputs['MergeVectorLayers']['OUTPUT'],
            'OPERATOR': 0,  # =
            'VALUE': '1',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByAttributeCostal'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}

        # Reproject points
        alg_params = {
            'INPUT': outputs['ExtractByExpression']['OUTPUT'],
            'TARGET_CRS': QgsCoordinateReferenceSystem('ESRI:54009'),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ReprojectPoints'] = processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}

        # Extract by attribute MARINE
        alg_params = {
            'FIELD': 'MARINE',
            'INPUT': outputs['MergeVectorLayers']['OUTPUT'],
            'OPERATOR': 0,  # =
            'VALUE': '2',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByAttributeMarine'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(16)
        if feedback.isCanceled():
            return {}

        # Extract by attribute TERRESTRIAL
        alg_params = {
            'FIELD': 'MARINE',
            'INPUT': outputs['MergeVectorLayers']['OUTPUT'],
            'OPERATOR': 0,  # =
            'VALUE': '0',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByAttributeTerrestrial'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(17)
        if feedback.isCanceled():
            return {}

        # Extracted polygons
        alg_params = {
            'INPUT': outputs['FixGeometriesPaPoly']['OUTPUT'],
            'INTERSECT': outputs['ReprojectCountries']['OUTPUT'],
            'PREDICATE': [0],  # intersect
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractedPolygons'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(18)
        if feedback.isCanceled():
            return {}

        # Extracted points EEZ4
        alg_params = {
            'INPUT': outputs['ReprojectPointsEez3']['OUTPUT'],
            'INTERSECT': outputs['BetterEez']['OUTPUT'],
            'PREDICATE': [0],  # intersect
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractedPointsEez4'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(19)
        if feedback.isCanceled():
            return {}

        # Extracted points
        alg_params = {
            'INPUT': outputs['ReprojectPoints']['OUTPUT'],
            'INTERSECT': outputs['ReprojectCountries']['OUTPUT'],
            'PREDICATE': [0],  # intersect
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractedPoints'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(20)
        if feedback.isCanceled():
            return {}

        # Extracted polygons EEZ
        alg_params = {
            'INPUT': outputs['FixGeometriesPaPoint']['OUTPUT'],
            'INTERSECT': outputs['BetterEez']['OUTPUT'],
            'PREDICATE': [0],  # intersect
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractedPolygonsEez'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(21)
        if feedback.isCanceled():
            return {}

        # NUMBER OF MARINE PAS
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['ISO3'],
            'INPUT': outputs['ExtractByAttributeMarine']['OUTPUT'],
            'VALUES_FIELD_NAME': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['NumberOfMarinePas'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(22)
        if feedback.isCanceled():
            return {}

        # Field calculator EEZ5
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'radius',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': 'sqrt(  "REP_AREA"/3.14)',
            'INPUT': outputs['ExtractedPointsEez4']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorEez5'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(23)
        if feedback.isCanceled():
            return {}

        # NUMBER OF COSTAL PAS
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['ISO3'],
            'INPUT': outputs['ExtractByAttributeCostal']['OUTPUT'],
            'VALUES_FIELD_NAME': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['NumberOfCostalPas'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(24)
        if feedback.isCanceled():
            return {}

        # Field calculator
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'radius',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': 'sqrt(  "REP_AREA"/3.14)',
            'INPUT': outputs['ExtractedPoints']['OUTPUT'],
            'NEW_FIELD': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculator'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(25)
        if feedback.isCanceled():
            return {}

        # NUMBER OF TERRESTRIAL PAS
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['ISO3'],
            'INPUT': outputs['ExtractByAttributeTerrestrial']['OUTPUT'],
            'VALUES_FIELD_NAME': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['NumberOfTerrestrialPas'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(26)
        if feedback.isCanceled():
            return {}

        # Extract by expression EEZ
        alg_params = {
            'EXPRESSION': '"STATUS"   !=  \'Not Reported\'  \r\nor  "STATUS"   !=  \'Proposed\'  or  "DESIG_ENG" != \'UNESCO-MAB Biosphere Reserve\' ',
            'INPUT': outputs['ExtractedPolygonsEez']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpressionEez'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(27)
        if feedback.isCanceled():
            return {}

        # Extract by expression
        alg_params = {
            'EXPRESSION': '"STATUS"   !=  \'Not Reported\'  \r\nor  "STATUS"   !=  \'Proposed\'  or  "DESIG_ENG" != \'UNESCO-MAB Biosphere Reserve\' ',
            'INPUT': outputs['ExtractedPolygons']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpression'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(28)
        if feedback.isCanceled():
            return {}

        # Buffer EEZ6
        alg_params = {
            'DISSOLVE': False,
            'DISTANCE': QgsProperty.fromExpression('"radius"*1000'),
            'END_CAP_STYLE': 0,  # Round
            'INPUT': outputs['FieldCalculatorEez5']['OUTPUT'],
            'JOIN_STYLE': 0,  # Round
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['BufferEez6'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(29)
        if feedback.isCanceled():
            return {}

        # Fix BUFFER EEZ7
        alg_params = {
            'INPUT': outputs['BufferEez6']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixBufferEez7'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(30)
        if feedback.isCanceled():
            return {}

        # Multipart to singleparts
        alg_params = {
            'INPUT': outputs['FixBufferEez7']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MultipartToSingleparts'] = processing.run('native:multiparttosingleparts', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(31)
        if feedback.isCanceled():
            return {}

        # Dissolve BUFFERED POINTS EEZ8
        alg_params = {
            'FIELD': ['ISO3'],
            'INPUT': outputs['MultipartToSingleparts']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DissolveBufferedPointsEez8'] = processing.run('native:dissolve', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(32)
        if feedback.isCanceled():
            return {}

        # Buffer
        alg_params = {
            'DISSOLVE': False,
            'DISTANCE': QgsProperty.fromExpression('"radius"*1000'),
            'END_CAP_STYLE': 0,  # Round
            'INPUT': outputs['FieldCalculator']['OUTPUT'],
            'JOIN_STYLE': 0,  # Round
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Buffer'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(33)
        if feedback.isCanceled():
            return {}

        # Fix EXTRACTED
        alg_params = {
            'INPUT': outputs['ExtractByExpression']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixExtracted'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(34)
        if feedback.isCanceled():
            return {}

        # Fix BUFFER
        alg_params = {
            'INPUT': outputs['Buffer']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixBuffer'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(35)
        if feedback.isCanceled():
            return {}

        # Fix EXTRACTED EEZ
        alg_params = {
            'INPUT': outputs['ExtractByExpressionEez']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixExtractedEez'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(36)
        if feedback.isCanceled():
            return {}

        # Dissolve POLYGONS
        alg_params = {
            'FIELD': 'ISO3',
            'INPUT': outputs['FixExtracted']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DissolvePolygons'] = processing.run('native:dissolve', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(37)
        if feedback.isCanceled():
            return {}

        # Multipart to singleparts
        alg_params = {
            'INPUT': outputs['FixBuffer']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MultipartToSingleparts'] = processing.run('native:multiparttosingleparts', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(38)
        if feedback.isCanceled():
            return {}

        # Dissolve POLYGONS EEZ
        alg_params = {
            'FIELD': ['ISO3'],
            'INPUT': outputs['FixExtractedEez']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DissolvePolygonsEez'] = processing.run('native:dissolve', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(39)
        if feedback.isCanceled():
            return {}

        # Merged Protection EEZ9
        alg_params = {
            'CRS': QgsCoordinateReferenceSystem('ESRI:54009'),
            'LAYERS': [outputs['DissolveBufferedPointsEez8']['OUTPUT'],outputs['DissolvePolygonsEez']['OUTPUT']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MergedProtectionEez9'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(40)
        if feedback.isCanceled():
            return {}

        # Fix merged points and polygons EEZ10
        alg_params = {
            'INPUT': outputs['MergedProtectionEez9']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixMergedPointsAndPolygonsEez10'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(41)
        if feedback.isCanceled():
            return {}

        # Dissolve BUFFERED POINTS
        alg_params = {
            'FIELD': ['ISO3'],
            'INPUT': outputs['MultipartToSingleparts']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DissolveBufferedPoints'] = processing.run('native:dissolve', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(42)
        if feedback.isCanceled():
            return {}

        # Merged Protection
        alg_params = {
            'CRS': QgsCoordinateReferenceSystem('ESRI:54009'),
            'LAYERS': [outputs['DissolveBufferedPoints']['OUTPUT'],outputs['DissolvePolygons']['OUTPUT']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MergedProtection'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(43)
        if feedback.isCanceled():
            return {}

        # Dissolve protection EEZ11
        alg_params = {
            'FIELD': ['ISO3'],
            'INPUT': outputs['FixMergedPointsAndPolygonsEez10']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DissolveProtectionEez11'] = processing.run('native:dissolve', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(44)
        if feedback.isCanceled():
            return {}

        # Fix dissolved protection EEZ12
        alg_params = {
            'INPUT': outputs['DissolveProtectionEez11']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixDissolvedProtectionEez12'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(45)
        if feedback.isCanceled():
            return {}

        # Clip EEZ13
        alg_params = {
            'INPUT': outputs['FixDissolvedProtectionEez12']['OUTPUT'],
            'OVERLAY': outputs['BetterEez']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ClipEez13'] = processing.run('native:clip', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(46)
        if feedback.isCanceled():
            return {}

        # Fix merged points and polygons
        alg_params = {
            'INPUT': outputs['MergedProtection']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixMergedPointsAndPolygons'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(47)
        if feedback.isCanceled():
            return {}

        # Calculate clipped area EEZ14
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'prot_mar_area',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': ' $area ',
            'INPUT': outputs['ClipEez13']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalculateClippedAreaEez14'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(48)
        if feedback.isCanceled():
            return {}

        # Dissolve protection
        alg_params = {
            'FIELD': 'ISO3',
            'INPUT': outputs['FixMergedPointsAndPolygons']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DissolveProtection'] = processing.run('native:dissolve', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(49)
        if feedback.isCanceled():
            return {}

        # Fix dissolved protection
        alg_params = {
            'INPUT': outputs['DissolveProtection']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixDissolvedProtection'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(50)
        if feedback.isCanceled():
            return {}

        # Join geometries with attributes eez15
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'isoa3_id',
            'FIELDS_TO_COPY': ['prot_mar_area'],
            'FIELD_2': 'ISO3',
            'INPUT': outputs['BetterEez']['OUTPUT'],
            'INPUT_2': outputs['CalculateClippedAreaEez14']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinGeometriesWithAttributesEez15'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(51)
        if feedback.isCanceled():
            return {}

        # Calculate country area EEZ16
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'country_mar_area_km',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '"country_area"/1000000',
            'INPUT': outputs['JoinGeometriesWithAttributesEez15']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalculateCountryAreaEez16'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(52)
        if feedback.isCanceled():
            return {}

        # Clip
        alg_params = {
            'INPUT': outputs['FixDissolvedProtection']['OUTPUT'],
            'OVERLAY': outputs['ReprojectCountries']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Clip'] = processing.run('native:clip', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(53)
        if feedback.isCanceled():
            return {}

        # Calculate protection eez17
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'prot_mar_km',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '"prot_mar_area"/1000000',
            'INPUT': outputs['CalculateCountryAreaEez16']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalculateProtectionEez17'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(54)
        if feedback.isCanceled():
            return {}

        # Calculate protection percentage eez18
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'prot_mar_perc',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '("prot_mar_km"*100)/"country_mar_area_km"',
            'INPUT': outputs['CalculateProtectionEez17']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalculateProtectionPercentageEez18'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(55)
        if feedback.isCanceled():
            return {}

        # Calculate clipped area
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'prot_area',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': ' $area ',
            'INPUT': outputs['Clip']['OUTPUT'],
            'NEW_FIELD': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalculateClippedArea'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(56)
        if feedback.isCanceled():
            return {}

        # Reproject layer FINAL EEZ
        alg_params = {
            'INPUT': outputs['CalculateProtectionPercentageEez18']['OUTPUT'],
            'OPERATION': '',
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:4326'),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ReprojectLayerFinalEez'] = processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(57)
        if feedback.isCanceled():
            return {}

        # Join geometries with attributes
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'isoa3_id',
            'FIELDS_TO_COPY': ['prot_area'],
            'FIELD_2': 'ISO3',
            'INPUT': outputs['ReprojectCountries']['OUTPUT'],
            'INPUT_2': outputs['CalculateClippedArea']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinGeometriesWithAttributes'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(58)
        if feedback.isCanceled():
            return {}

        # Calculate country area
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'country_area_km',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '"country_area"/1000000',
            'INPUT': outputs['JoinGeometriesWithAttributes']['OUTPUT'],
            'NEW_FIELD': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalculateCountryArea'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(59)
        if feedback.isCanceled():
            return {}

        # Calculate protection
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'prot_km',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '"prot_area"/1000000',
            'INPUT': outputs['CalculateCountryArea']['OUTPUT'],
            'NEW_FIELD': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalculateProtection'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(60)
        if feedback.isCanceled():
            return {}

        # Calculate protection percentage
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'prot_perc',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '("prot_km"*100)/"country_area_km"',
            'INPUT': outputs['CalculateProtection']['OUTPUT'],
            'NEW_FIELD': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalculateProtectionPercentage'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(61)
        if feedback.isCanceled():
            return {}

        # Reproject layer FINAL COUNTRY
        alg_params = {
            'INPUT': outputs['CalculateProtectionPercentage']['OUTPUT'],
            'OPERATION': '',
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:4326'),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ReprojectLayerFinalCountry'] = processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(62)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value
        alg_params = {
            'DISCARD_NONMATCHING': True,
            'FIELD': 'ISO3',
            'FIELDS_TO_COPY': ['grouping_i','region_acp','country_area_km','prot_km','prot_perc',''],
            'FIELD_2': 'isoa3_id',
            'INPUT': outputs['Number_of_pas_Total']['OUTPUT'],
            'INPUT_2': outputs['ReprojectLayerFinalCountry']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValue'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(63)
        if feedback.isCanceled():
            return {}

        # PROTECTION_CALCULATION
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'ISO3',
            'FIELDS_TO_COPY': ['country_mar_area_km','prot_mar_km','prot_mar_perc'],
            'FIELD_2': 'isoa3_id',
            'INPUT': outputs['JoinAttributesByFieldValue']['OUTPUT'],
            'INPUT_2': outputs['ReprojectLayerFinalEez']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Protection_calculation'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(64)
        if feedback.isCanceled():
            return {}

        # PROT_CALC_TER
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'ISO3',
            'FIELDS_TO_COPY': ['count'],
            'FIELD_2': 'ISO3',
            'INPUT': outputs['Protection_calculation']['OUTPUT'],
            'INPUT_2': outputs['NumberOfTerrestrialPas']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': 'terrestrial_',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Prot_calc_ter'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(65)
        if feedback.isCanceled():
            return {}

        # PROT_CALC_COSTAL
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'ISO3',
            'FIELDS_TO_COPY': ['count'],
            'FIELD_2': 'ISO3',
            'INPUT': outputs['Prot_calc_ter']['OUTPUT'],
            'INPUT_2': outputs['NumberOfCostalPas']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': 'costal_',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Prot_calc_costal'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(66)
        if feedback.isCanceled():
            return {}

        # PROT_CALC_MARINE
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'ISO3',
            'FIELDS_TO_COPY': ['count'],
            'FIELD_2': 'ISO3',
            'INPUT': outputs['Prot_calc_costal']['OUTPUT'],
            'INPUT_2': outputs['NumberOfMarinePas']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': 'marine_',
            'OUTPUT': parameters['Country_stats']
        }
        outputs['Prot_calc_marine'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Country_stats'] = outputs['Prot_calc_marine']['OUTPUT']

        feedback.setCurrentStep(67)
        if feedback.isCanceled():
            return {}

        # calculate region prot area
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['region_acp'],
            'INPUT': outputs['Prot_calc_marine']['OUTPUT'],
            'VALUES_FIELD_NAME': 'prot_km',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalculateRegionProtArea'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(68)
        if feedback.isCanceled():
            return {}

        # calculate marine_count_region
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['region_acp'],
            'INPUT': outputs['Prot_calc_marine']['OUTPUT'],
            'VALUES_FIELD_NAME': 'marine_count',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalculateMarine_count_region'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(69)
        if feedback.isCanceled():
            return {}

        # Export to PostgreSQL COUNTRY STATS
        alg_params = {
            'CREATEINDEX': True,
            'DATABASE': 'Biopama_api',
            'DROP_STRING_LENGTH': False,
            'ENCODING': 'UTF-8',
            'FORCE_SINGLEPART': False,
            'GEOMETRY_COLUMN': 'geom',
            'INPUT': outputs['Prot_calc_marine']['OUTPUT'],
            'LOWERCASE_NAMES': True,
            'OVERWRITE': False,
            'PRIMARY_KEY': '',
            'SCHEMA': 'protection_level',
            'TABLENAME': 'country_stats'
        }
        outputs['ExportToPostgresqlCountryStats'] = processing.run('qgis:importintopostgis', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(70)
        if feedback.isCanceled():
            return {}

        # calculate region land area
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['region_acp'],
            'INPUT': outputs['Prot_calc_marine']['OUTPUT'],
            'VALUES_FIELD_NAME': 'country_area_km',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalculateRegionLandArea'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(71)
        if feedback.isCanceled():
            return {}

        # Drop field(s) marine_count
        alg_params = {
            'COLUMN': ['mean','q1','q3','count','unique','min','max','range','median','stddev','minority','majority','iqr'],
            'INPUT': outputs['CalculateMarine_count_region']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldsMarine_count'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(72)
        if feedback.isCanceled():
            return {}

        # calculate region mar area
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['region_acp'],
            'INPUT': outputs['Prot_calc_marine']['OUTPUT'],
            'VALUES_FIELD_NAME': 'country_mar_area_km',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalculateRegionMarArea'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(73)
        if feedback.isCanceled():
            return {}

        # calculate costal_count_region
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['region_acp'],
            'INPUT': outputs['Prot_calc_marine']['OUTPUT'],
            'VALUES_FIELD_NAME': 'costal_count',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalculateCostal_count_region'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(74)
        if feedback.isCanceled():
            return {}

        # calculate region mar prot area
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['region_acp'],
            'INPUT': outputs['Prot_calc_marine']['OUTPUT'],
            'VALUES_FIELD_NAME': 'prot_mar_km',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalculateRegionMarProtArea'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(75)
        if feedback.isCanceled():
            return {}

        # Drop field(s) reg land area prot
        alg_params = {
            'COLUMN': ['mean','q1','q3','count','unique','min','max','range','median','stddev','minority','majority','iqr'],
            'INPUT': outputs['CalculateRegionProtArea']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldsRegLandAreaProt'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(76)
        if feedback.isCanceled():
            return {}

        # calculate terrestrial_count_region
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['region_acp'],
            'INPUT': outputs['Prot_calc_marine']['OUTPUT'],
            'VALUES_FIELD_NAME': 'terrestrial_count',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalculateTerrestrial_count_region'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(77)
        if feedback.isCanceled():
            return {}

        # MAR COUNT REG
        alg_params = {
            'FIELD': 'sum',
            'INPUT': outputs['DropFieldsMarine_count']['OUTPUT'],
            'NEW_NAME': 'reg_mar_count',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MarCountReg'] = processing.run('native:renametablefield', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(78)
        if feedback.isCanceled():
            return {}

        # Drop field(s) reg land area
        alg_params = {
            'COLUMN': ['mean','q1','q3','count','unique','min','max','range','median','stddev','minority','majority','iqr'],
            'INPUT': outputs['CalculateRegionLandArea']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldsRegLandArea'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(79)
        if feedback.isCanceled():
            return {}

        # Drop field(s) reg mar area prot 
        alg_params = {
            'COLUMN': ['mean','q1','q3','count','unique','min','max','range','median','stddev','minority','majority','iqr'],
            'INPUT': outputs['CalculateRegionMarProtArea']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldsRegMarAreaProt'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(80)
        if feedback.isCanceled():
            return {}

        # Rename field reg land area
        alg_params = {
            'FIELD': 'sum',
            'INPUT': outputs['DropFieldsRegLandArea']['OUTPUT'],
            'NEW_NAME': 'reg_land_area',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RenameFieldRegLandArea'] = processing.run('native:renametablefield', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(81)
        if feedback.isCanceled():
            return {}

        # Drop field(s) terrestrial_count
        alg_params = {
            'COLUMN': ['mean','q1','q3','count','unique','min','max','range','median','stddev','minority','majority','iqr'],
            'INPUT': outputs['CalculateTerrestrial_count_region']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldsTerrestrial_count'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(82)
        if feedback.isCanceled():
            return {}

        # Rename field reg land area prot
        alg_params = {
            'FIELD': 'sum',
            'INPUT': outputs['DropFieldsRegLandAreaProt']['OUTPUT'],
            'NEW_NAME': 'reg_land_area_prot',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RenameFieldRegLandAreaProt'] = processing.run('native:renametablefield', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(83)
        if feedback.isCanceled():
            return {}

        # Drop field(s) reg mar area
        alg_params = {
            'COLUMN': ['mean','q1','q3','count','unique','min','max','range','median','stddev','minority','majority','iqr'],
            'INPUT': outputs['CalculateRegionMarArea']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldsRegMarArea'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(84)
        if feedback.isCanceled():
            return {}

        # TERR COUNT REG
        alg_params = {
            'FIELD': 'sum',
            'INPUT': outputs['DropFieldsTerrestrial_count']['OUTPUT'],
            'NEW_NAME': 'reg_terr_count',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['TerrCountReg'] = processing.run('native:renametablefield', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(85)
        if feedback.isCanceled():
            return {}

        # Drop field(s) costal_count
        alg_params = {
            'COLUMN': ['mean','q1','q3','count','unique','min','max','range','median','stddev','minority','majority','iqr'],
            'INPUT': outputs['CalculateCostal_count_region']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldsCostal_count'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(86)
        if feedback.isCanceled():
            return {}

        # MARANDTERCOUNT JOIN
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'region_acp',
            'FIELDS_TO_COPY': ['reg_mar_count'],
            'FIELD_2': 'region_acp',
            'INPUT': outputs['TerrCountReg']['OUTPUT'],
            'INPUT_2': outputs['MarCountReg']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MarandtercountJoin'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(87)
        if feedback.isCanceled():
            return {}

        # COSTAL COUNT REG
        alg_params = {
            'FIELD': 'sum',
            'INPUT': outputs['DropFieldsCostal_count']['OUTPUT'],
            'NEW_NAME': 'reg_costal_count',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CostalCountReg'] = processing.run('native:renametablefield', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(88)
        if feedback.isCanceled():
            return {}

        # count_final
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'region_acp',
            'FIELDS_TO_COPY': ['reg_costal_count'],
            'FIELD_2': 'region_acp',
            'INPUT': outputs['MarandtercountJoin']['OUTPUT'],
            'INPUT_2': outputs['CostalCountReg']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Count_final'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(89)
        if feedback.isCanceled():
            return {}

        # terr_data
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'region_acp',
            'FIELDS_TO_COPY': ['reg_land_area_prot'],
            'FIELD_2': 'region_acp',
            'INPUT': outputs['RenameFieldRegLandArea']['OUTPUT'],
            'INPUT_2': outputs['RenameFieldRegLandAreaProt']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Terr_data'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(90)
        if feedback.isCanceled():
            return {}

        # Rename field reg mar area prot
        alg_params = {
            'FIELD': 'sum',
            'INPUT': outputs['DropFieldsRegMarAreaProt']['OUTPUT'],
            'NEW_NAME': 'reg_mar_area_prot',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RenameFieldRegMarAreaProt'] = processing.run('native:renametablefield', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(91)
        if feedback.isCanceled():
            return {}

        # reg_terr_prot_perc
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'reg_terr_prot_perc',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '("reg_land_area_prot"*100)/"reg_land_area"',
            'INPUT': outputs['Terr_data']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Reg_terr_prot_perc'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(92)
        if feedback.isCanceled():
            return {}

        # Rename field reg mar area
        alg_params = {
            'FIELD': 'sum',
            'INPUT': outputs['DropFieldsRegMarArea']['OUTPUT'],
            'NEW_NAME': 'reg_mar_area',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RenameFieldRegMarArea'] = processing.run('native:renametablefield', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(93)
        if feedback.isCanceled():
            return {}

        # Field calculator COUNT TOTAL REG
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'count_reg_tot',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '"reg_terr_count"+"reg_mar_count"+"reg_costal_count"',
            'INPUT': outputs['Count_final']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorCountTotalReg'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(94)
        if feedback.isCanceled():
            return {}

        # mar_data
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'region_acp',
            'FIELDS_TO_COPY': ['reg_mar_area_prot'],
            'FIELD_2': 'region_acp',
            'INPUT': outputs['RenameFieldRegMarArea']['OUTPUT'],
            'INPUT_2': outputs['RenameFieldRegMarAreaProt']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Mar_data'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(95)
        if feedback.isCanceled():
            return {}

        # reg_mar_prot_perc
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'reg_mar_prot_perc',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '("reg_mar_area_prot"*100)/"reg_mar_area"',
            'INPUT': outputs['Mar_data']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Reg_mar_prot_perc'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(96)
        if feedback.isCanceled():
            return {}

        # ter and mar prot perc
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'region_acp',
            'FIELDS_TO_COPY': ['reg_mar_area','reg_mar_area_prot','reg_mar_prot_perc'],
            'FIELD_2': 'region_acp',
            'INPUT': outputs['Reg_terr_prot_perc']['OUTPUT'],
            'INPUT_2': outputs['Reg_mar_prot_perc']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['TerAndMarProtPerc'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(97)
        if feedback.isCanceled():
            return {}

        # count and prot final REGION
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'region_acp',
            'FIELDS_TO_COPY': [''],
            'FIELD_2': 'region_acp',
            'INPUT': outputs['TerAndMarProtPerc']['OUTPUT'],
            'INPUT_2': outputs['FieldCalculatorCountTotalReg']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': parameters['Region_stats']
        }
        outputs['CountAndProtFinalRegion'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Region_stats'] = outputs['CountAndProtFinalRegion']['OUTPUT']

        feedback.setCurrentStep(98)
        if feedback.isCanceled():
            return {}

        # Statistics by categories - MARINE AREA PROT ACP
        alg_params = {
            'CATEGORIES_FIELD_NAME': [''],
            'INPUT': outputs['CountAndProtFinalRegion']['OUTPUT'],
            'VALUES_FIELD_NAME': 'reg_mar_area_prot',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesMarineAreaProtAcp'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(99)
        if feedback.isCanceled():
            return {}

        # Statistics by categories - MARINE COUNT ACP
        alg_params = {
            'CATEGORIES_FIELD_NAME': [''],
            'INPUT': outputs['CountAndProtFinalRegion']['OUTPUT'],
            'VALUES_FIELD_NAME': 'reg_mar_count',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesMarineCountAcp'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(100)
        if feedback.isCanceled():
            return {}

        # Statistics by categories - LAND COUNT ACP
        alg_params = {
            'CATEGORIES_FIELD_NAME': [''],
            'INPUT': outputs['CountAndProtFinalRegion']['OUTPUT'],
            'VALUES_FIELD_NAME': 'reg_terr_count',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesLandCountAcp'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(101)
        if feedback.isCanceled():
            return {}

        # Drop field - MARINE AREA PROT ACP
        alg_params = {
            'COLUMN': ['mean','q1','q3','unique','min','max','range','median','stddev','minority','majority','iqr'],
            'INPUT': outputs['StatisticsByCategoriesMarineAreaProtAcp']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldMarineAreaProtAcp'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(102)
        if feedback.isCanceled():
            return {}

        # Statistics by categories - LAND AREA PROT ACP
        alg_params = {
            'CATEGORIES_FIELD_NAME': [''],
            'INPUT': outputs['CountAndProtFinalRegion']['OUTPUT'],
            'VALUES_FIELD_NAME': 'reg_land_area_prot',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesLandAreaProtAcp'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(103)
        if feedback.isCanceled():
            return {}

        # Export to PostgreSQL REGION STATS
        alg_params = {
            'CREATEINDEX': True,
            'DATABASE': 'Biopama_api',
            'DROP_STRING_LENGTH': False,
            'ENCODING': 'UTF-8',
            'FORCE_SINGLEPART': False,
            'GEOMETRY_COLUMN': 'geom',
            'INPUT': outputs['CountAndProtFinalRegion']['OUTPUT'],
            'LOWERCASE_NAMES': True,
            'OVERWRITE': False,
            'PRIMARY_KEY': '',
            'SCHEMA': 'protection_level',
            'TABLENAME': 'region_stats'
        }
        outputs['ExportToPostgresqlRegionStats'] = processing.run('qgis:importintopostgis', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(104)
        if feedback.isCanceled():
            return {}

        # Drop field - LAND AREA PROT ACP
        alg_params = {
            'COLUMN': ['mean','q1','q3','unique','min','max','range','median','stddev','minority','majority','iqr'],
            'INPUT': outputs['StatisticsByCategoriesLandAreaProtAcp']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldLandAreaProtAcp'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(105)
        if feedback.isCanceled():
            return {}

        # Statistics by categories - TOT COUNT ACP
        alg_params = {
            'CATEGORIES_FIELD_NAME': [''],
            'INPUT': outputs['CountAndProtFinalRegion']['OUTPUT'],
            'VALUES_FIELD_NAME': 'count_reg_tot',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesTotCountAcp'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(106)
        if feedback.isCanceled():
            return {}

        # Drop field - LAND COUNT ACP
        alg_params = {
            'COLUMN': ['mean','q1','q3','unique','min','max','range','median','stddev','minority','majority','iqr'],
            'INPUT': outputs['StatisticsByCategoriesLandCountAcp']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldLandCountAcp'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(107)
        if feedback.isCanceled():
            return {}

        # Rename field - LAND AREA PROT ACP
        alg_params = {
            'FIELD': 'sum',
            'INPUT': outputs['DropFieldLandAreaProtAcp']['OUTPUT'],
            'NEW_NAME': 'ter_area_prot_acp',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RenameFieldLandAreaProtAcp'] = processing.run('native:renametablefield', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(108)
        if feedback.isCanceled():
            return {}

        # Rename field - MARINE AREA PROT ACP
        alg_params = {
            'FIELD': 'sum',
            'INPUT': outputs['DropFieldMarineAreaProtAcp']['OUTPUT'],
            'NEW_NAME': 'mar_area_prot_acp',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RenameFieldMarineAreaProtAcp'] = processing.run('native:renametablefield', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(109)
        if feedback.isCanceled():
            return {}

        # Statistics by categories - COSTAL COUNT ACP
        alg_params = {
            'CATEGORIES_FIELD_NAME': [''],
            'INPUT': outputs['CountAndProtFinalRegion']['OUTPUT'],
            'VALUES_FIELD_NAME': 'reg_costal_count',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesCostalCountAcp'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(110)
        if feedback.isCanceled():
            return {}

        # Statistics by categories - LAND AREA ACP
        alg_params = {
            'CATEGORIES_FIELD_NAME': [''],
            'INPUT': outputs['CountAndProtFinalRegion']['OUTPUT'],
            'VALUES_FIELD_NAME': 'reg_land_area',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesLandAreaAcp'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(111)
        if feedback.isCanceled():
            return {}

        # Statistics by categories - MARINE AREA ACP
        alg_params = {
            'CATEGORIES_FIELD_NAME': [''],
            'INPUT': outputs['CountAndProtFinalRegion']['OUTPUT'],
            'VALUES_FIELD_NAME': 'reg_mar_area',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesMarineAreaAcp'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(112)
        if feedback.isCanceled():
            return {}

        # Drop field - MAR COUNT ACP
        alg_params = {
            'COLUMN': ['mean','q1','q3','unique','min','max','range','median','stddev','minority','majority','iqr'],
            'INPUT': outputs['StatisticsByCategoriesMarineCountAcp']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldMarCountAcp'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(113)
        if feedback.isCanceled():
            return {}

        # Drop field - LAND AREA ACP
        alg_params = {
            'COLUMN': ['mean','q1','q3','unique','min','max','range','median','stddev','minority','majority','iqr'],
            'INPUT': outputs['StatisticsByCategoriesLandAreaAcp']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldLandAreaAcp'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(114)
        if feedback.isCanceled():
            return {}

        # Drop field - COSTAL COUNT ACP
        alg_params = {
            'COLUMN': ['mean','q1','q3','unique','min','max','range','median','stddev','minority','majority','iqr'],
            'INPUT': outputs['StatisticsByCategoriesCostalCountAcp']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldCostalCountAcp'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(115)
        if feedback.isCanceled():
            return {}

        # Drop field - MARINE AREA ACP
        alg_params = {
            'COLUMN': ['mean','q1','q3','unique','min','max','range','median','stddev','minority','majority','iqr'],
            'INPUT': outputs['StatisticsByCategoriesMarineAreaAcp']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldMarineAreaAcp'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(116)
        if feedback.isCanceled():
            return {}

        # Drop field - TOT COUNT ACP
        alg_params = {
            'COLUMN': ['mean','q1','q3','unique','min','max','range','median','stddev','minority','majority','iqr'],
            'INPUT': outputs['StatisticsByCategoriesTotCountAcp']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldTotCountAcp'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(117)
        if feedback.isCanceled():
            return {}

        # Rename field - MARINE COUNT ACP
        alg_params = {
            'FIELD': 'sum',
            'INPUT': outputs['DropFieldMarCountAcp']['OUTPUT'],
            'NEW_NAME': 'mar_count_acp',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RenameFieldMarineCountAcp'] = processing.run('native:renametablefield', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(118)
        if feedback.isCanceled():
            return {}

        # Rename field - LAND COUNT ACP
        alg_params = {
            'FIELD': 'sum',
            'INPUT': outputs['DropFieldLandCountAcp']['OUTPUT'],
            'NEW_NAME': 'terr_count_acp',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RenameFieldLandCountAcp'] = processing.run('native:renametablefield', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(119)
        if feedback.isCanceled():
            return {}

        # Rename field - COSTAL COUNT ACP
        alg_params = {
            'FIELD': 'sum',
            'INPUT': outputs['DropFieldCostalCountAcp']['OUTPUT'],
            'NEW_NAME': 'costal_count_acp',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RenameFieldCostalCountAcp'] = processing.run('native:renametablefield', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(120)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value - 1ST COUNT ACP
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'count',
            'FIELDS_TO_COPY': ['mar_count_acp'],
            'FIELD_2': 'count',
            'INPUT': outputs['RenameFieldLandCountAcp']['OUTPUT'],
            'INPUT_2': outputs['RenameFieldMarineCountAcp']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValue1stCountAcp'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(121)
        if feedback.isCanceled():
            return {}

        # Rename field - LAND AREA ACP
        alg_params = {
            'FIELD': 'sum',
            'INPUT': outputs['DropFieldLandAreaAcp']['OUTPUT'],
            'NEW_NAME': 'ter_area_acp',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RenameFieldLandAreaAcp'] = processing.run('native:renametablefield', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(122)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value - LAND ACP
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'count',
            'FIELDS_TO_COPY': ['ter_area_prot_acp'],
            'FIELD_2': 'count',
            'INPUT': outputs['RenameFieldLandAreaAcp']['OUTPUT'],
            'INPUT_2': outputs['RenameFieldLandAreaProtAcp']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueLandAcp'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(123)
        if feedback.isCanceled():
            return {}

        # Rename field - MARINE AREA ACP
        alg_params = {
            'FIELD': 'sum',
            'INPUT': outputs['DropFieldMarineAreaAcp']['OUTPUT'],
            'NEW_NAME': 'mar_area_acp',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RenameFieldMarineAreaAcp'] = processing.run('native:renametablefield', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(124)
        if feedback.isCanceled():
            return {}

        # Rename field - TOT COUNT ACP
        alg_params = {
            'FIELD': 'sum',
            'INPUT': outputs['DropFieldTotCountAcp']['OUTPUT'],
            'NEW_NAME': 'tot_count_acp',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RenameFieldTotCountAcp'] = processing.run('native:renametablefield', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(125)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value - 2ND COUNT ACP
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'count',
            'FIELDS_TO_COPY': ['tot_count_acp'],
            'FIELD_2': 'count',
            'INPUT': outputs['RenameFieldCostalCountAcp']['OUTPUT'],
            'INPUT_2': outputs['RenameFieldTotCountAcp']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValue2ndCountAcp'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(126)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value - MARINE ACP
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'count',
            'FIELDS_TO_COPY': ['mar_area_prot_acp'],
            'FIELD_2': 'count',
            'INPUT': outputs['RenameFieldMarineAreaAcp']['OUTPUT'],
            'INPUT_2': outputs['RenameFieldMarineAreaProtAcp']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueMarineAcp'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(127)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value - COUNT ACP
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'count',
            'FIELDS_TO_COPY': [''],
            'FIELD_2': 'count',
            'INPUT': outputs['JoinAttributesByFieldValue1stCountAcp']['OUTPUT'],
            'INPUT_2': outputs['JoinAttributesByFieldValue2ndCountAcp']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueCountAcp'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(128)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value - PROTECTION ACP
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'count',
            'FIELDS_TO_COPY': [''],
            'FIELD_2': 'count',
            'INPUT': outputs['JoinAttributesByFieldValueLandAcp']['OUTPUT'],
            'INPUT_2': outputs['JoinAttributesByFieldValueMarineAcp']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueProtectionAcp'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(129)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value - ALL ACP
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'count',
            'FIELDS_TO_COPY': [''],
            'FIELD_2': 'count',
            'INPUT': outputs['JoinAttributesByFieldValueProtectionAcp']['OUTPUT'],
            'INPUT_2': outputs['JoinAttributesByFieldValueCountAcp']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueAllAcp'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(130)
        if feedback.isCanceled():
            return {}

        # Field calculator - TERR PROT PERC ACP
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'ter_prot_perc_acp',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '("ter_area_prot_acp"*100)/"ter_area_acp"',
            'INPUT': outputs['JoinAttributesByFieldValueAllAcp']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorTerrProtPercAcp'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(131)
        if feedback.isCanceled():
            return {}

        # Field calculator - MAR PROT PERC ACP
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'mar_prot_perc_acp',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '("mar_area_prot_acp"*100)/"mar_area_acp"',
            'INPUT': outputs['FieldCalculatorTerrProtPercAcp']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorMarProtPercAcp'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(132)
        if feedback.isCanceled():
            return {}

        # Drop field(s) ACP FINAL
        alg_params = {
            'COLUMN': ['count','count_2','count_3','count_2_2'],
            'INPUT': outputs['FieldCalculatorMarProtPercAcp']['OUTPUT'],
            'OUTPUT': parameters['Acp_stats']
        }
        outputs['DropFieldsAcpFinal'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Acp_stats'] = outputs['DropFieldsAcpFinal']['OUTPUT']

        feedback.setCurrentStep(133)
        if feedback.isCanceled():
            return {}

        # Export to PostgreSQL ACP STATS
        alg_params = {
            'CREATEINDEX': True,
            'DATABASE': 'Biopama_api',
            'DROP_STRING_LENGTH': False,
            'ENCODING': 'UTF-8',
            'FORCE_SINGLEPART': False,
            'GEOMETRY_COLUMN': 'geom',
            'INPUT': outputs['DropFieldsAcpFinal']['OUTPUT'],
            'LOWERCASE_NAMES': True,
            'OVERWRITE': False,
            'PRIMARY_KEY': '',
            'SCHEMA': 'protection_level',
            'TABLENAME': 'acp_stats'
        }
        outputs['ExportToPostgresqlAcpStats'] = processing.run('qgis:importintopostgis', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        return results

    def name(self):
        return 'wdpa_country_processing'

    def displayName(self):
        return 'wdpa_country_processing'

    def group(self):
        return 'wdpa'

    def groupId(self):
        return 'wdpa'

    def createInstance(self):
        return Wdpa_country_processing()
